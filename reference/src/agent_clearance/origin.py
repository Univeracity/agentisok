from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from agent_clearance.canonical import (
    b64url,
    b64url_decode,
    canonical_dumps,
    isoformat,
    parse_iso,
    request_binding_digest,
    same_origin,
    sha256_digest_header,
)
from agent_clearance.http_sig import HttpSignatureError, verify_request
from agent_clearance.keys import (
    MANDATE_ISSUER_KEY_ID,
    PRESENTER_KEY_ID,
    artifact_issuer_private,
    public_key,
)
from agent_clearance.schemas import validate_schema

HMS_PROFILE = "urn:agent-clearance:profile:http-message-signatures:rfc9421:0.1"
MANDATE_PROFILE = "urn:agent-clearance:profile:origin-scoped-mandate:0.1"
WBA_PROFILE = "urn:agent-clearance:profile:web-bot-auth:0.1"

RATE_LIMIT = "urn:agent-clearance:obligation:rate-limit:0.1"
MAXIMUM_RESULTS = "urn:agent-clearance:obligation:maximum-results:0.1"
ONE_TIME = "urn:agent-clearance:obligation:one-time:0.1"
ACTION_RESTRICTION = "urn:agent-clearance:obligation:action-restriction:0.1"
STEP_UP_BEFORE = "urn:agent-clearance:obligation:step-up-before:0.1"

CORE_OBLIGATIONS = {
    RATE_LIMIT,
    MAXIMUM_RESULTS,
    ONE_TIME,
    ACTION_RESTRICTION,
    STEP_UP_BEFORE,
}


class EvaluationError(Exception):
    def __init__(self, code: str, message: str, decision: str = "deny"):
        super().__init__(message)
        self.code = code
        self.message = message
        self.decision = decision


@dataclass
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: bytes


@dataclass
class Origin:
    now: datetime
    used_nonces: set[str] = field(default_factory=set)
    presenter_keys: dict[str, Ed25519PublicKey] = field(default_factory=dict)
    mandate_issuer_keys: dict[str, Ed25519PublicKey] = field(default_factory=dict)
    supported_obligations: set[str] = field(default_factory=lambda: set(CORE_OBLIGATIONS))
    fail_closed_on_unknown_revocation: bool = False
    max_presentation_bytes: int = 65536

    def __post_init__(self) -> None:
        if not self.presenter_keys:
            self.presenter_keys = {PRESENTER_KEY_ID: public_key("presenter")}
        if not self.mandate_issuer_keys:
            self.mandate_issuer_keys = {MANDATE_ISSUER_KEY_ID: public_key("mandate-issuer")}

    def evaluate(self, challenge: dict[str, Any], request: HttpRequest) -> dict[str, Any]:
        try:
            if len(request.body) > self.max_presentation_bytes:
                raise EvaluationError("evidence.invalid", "presentation exceeds size limit")
            presentation = _load_json_body(request.body)
            facts = self.verify(challenge, presentation, request)
            return self.decide(challenge, presentation, facts)
        except EvaluationError as exc:
            return self._decision(
                challenge,
                presentation_digest(request.body) if request.body else challenge_binding_digest(challenge),
                exc.decision,
                [],
                [{"code": exc.code}],
            )

    def verify(
        self,
        challenge: dict[str, Any],
        presentation: dict[str, Any],
        request: HttpRequest,
    ) -> list[dict[str, Any]]:
        try:
            validate_schema("challenge", challenge)
            validate_schema("presentation", presentation)
        except ValueError as exc:
            raise EvaluationError("evidence.invalid", str(exc)) from exc
        self._check_challenge(challenge)
        self._check_presentation_endpoint(challenge, request)
        if presentation["challenge_id"] != challenge["challenge_id"]:
            raise EvaluationError("binding.mismatch", "challenge_id mismatch")
        expected_digest = challenge_binding_digest(challenge)
        if presentation["request_binding_digest"] != expected_digest:
            raise EvaluationError("binding.mismatch", "request-binding digest mismatch")

        try:
            required_components = {
                "@method",
                "@authority",
                "@path",
                "content-digest",
                "content-type",
            }
            if urlparse(request.url).query:
                required_components.add("@query")
            verified = verify_request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                body=request.body,
                public_keys=self.presenter_keys,
                expected_nonce=challenge["nonce"],
                expected_tag="agent-clearance",
                required_components=required_components,
                now=int(self.now.timestamp()),
                not_before=int(parse_iso(challenge["created_at"]).timestamp()),
                not_after=int(parse_iso(challenge["expires_at"]).timestamp()),
            )
        except HttpSignatureError as exc:
            raise EvaluationError("evidence.invalid", str(exc)) from exc

        if verified["key_id"] != presentation["presenter"]["key_id"]:
            raise EvaluationError("binding.mismatch", "presenter key does not match HTTP keyid")
        content_type = {key.lower(): value for key, value in request.headers.items()}.get("content-type")
        if content_type != "application/agent-clearance-presentation+json":
            raise EvaluationError("evidence.invalid", "unexpected presentation content type")
        if int(parse_iso(presentation["created_at"]).timestamp()) != verified["params"]["created"]:
            raise EvaluationError("binding.mismatch", "presentation time does not match HTTP signature")
        if presentation["presenter"]["proof_profile"] not in {HMS_PROFILE, WBA_PROFILE}:
            raise EvaluationError("evidence.invalid", "unsupported proof profile")

        nonce = challenge["nonce"]
        if nonce in self.used_nonces:
            raise EvaluationError("replay.nonce", "challenge nonce already used")
        self.used_nonces.add(nonce)

        return self._verify_evidence(challenge, presentation, verified["key_id"])

    def decide(
        self,
        challenge: dict[str, Any],
        presentation: dict[str, Any],
        facts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        action = challenge["request_binding"]["action"]
        if action["type"] == "reservation.commit":
            decision = self._decision(
                challenge,
                presentation["request_binding_digest"],
                "step_up",
                [],
                [{"code": "step_up.required"}],
                continuation_uri=f"{challenge['origin']}/agent-clearance/step-up/{challenge['challenge_id']}",
            )
            validate_schema("decision", decision)
            return decision

        if action["type"] not in {"availability.read", "inventory.read"}:
            raise EvaluationError("policy.denied", "action not admitted")

        constraints = action.get("constraints", {})
        maximum_results = constraints.get("maximum_results", 100)
        if type(maximum_results) is not int or maximum_results < 1:
            raise EvaluationError("policy.denied", "maximum_results must be a positive integer")
        obligations = [
            {
                "type": RATE_LIMIT,
                "critical": True,
                "parameters": {
                    "requests": 20,
                    "window_seconds": 3600,
                    "bucket": "origin_pairwise_subject",
                },
            },
            {
                "type": MAXIMUM_RESULTS,
                "critical": True,
                "parameters": {"count": maximum_results},
            },
            {
                "type": ACTION_RESTRICTION,
                "critical": True,
                "parameters": {"actions": [action["type"]]},
            },
            {
                "type": STEP_UP_BEFORE,
                "critical": True,
                "parameters": {"action": "reservation.commit"},
            },
        ]
        unsupported = [item["type"] for item in obligations if item["type"] not in self.supported_obligations]
        if unsupported:
            raise EvaluationError("obligation.unsupported", f"cannot enforce {unsupported[0]}")

        pairwise = next(fact["subject"]["id"] for fact in facts if fact["claim"] == "subject.pairwise_id")
        del pairwise  # used only to prove the fact exists
        artifact = self._artifact(challenge, presentation, obligations)
        decision = self._decision(
            challenge,
            presentation["request_binding_digest"],
            "allow_with_obligations",
            obligations,
            [{"code": "evidence.sufficient"}, {"code": "policy.bounded_read"}],
            clearance_artifact=artifact,
        )
        validate_schema("decision", decision)
        return decision

    def _check_challenge(self, challenge: dict[str, Any]) -> None:
        created = parse_iso(challenge["created_at"])
        expires = parse_iso(challenge["expires_at"])
        if expires <= created:
            raise EvaluationError("challenge.expired", "challenge expiry is not after created_at")
        if self.now < created or self.now > expires:
            raise EvaluationError("challenge.expired", "challenge is outside its validity window")
        ids = [item["id"] for item in challenge["evidence_requirements"]]
        if len(ids) != len(set(ids)):
            raise EvaluationError("evidence.invalid", "duplicate evidence requirement ids")
        if not same_origin(challenge["presentation_endpoint"], challenge["origin"]):
            raise EvaluationError("origin.mismatch", "presentation endpoint is not on the challenge origin")

    def _check_presentation_endpoint(self, challenge: dict[str, Any], request: HttpRequest) -> None:
        if request.method.upper() != "POST":
            raise EvaluationError("binding.mismatch", "presentation method must be POST")
        expected = challenge["presentation_endpoint"]
        if request.url.rstrip("/") != expected.rstrip("/"):
            raise EvaluationError("binding.mismatch", "presentation URL mismatch")

    def _verify_evidence(
        self,
        challenge: dict[str, Any],
        presentation: dict[str, Any],
        presenter_key_id: str,
    ) -> list[dict[str, Any]]:
        envelope_ids = [item["requirement_id"] for item in presentation["evidence"]]
        if len(envelope_ids) != len(set(envelope_ids)):
            raise EvaluationError("evidence.invalid", "duplicate evidence requirement ids")
        requirement_ids = {item["id"] for item in challenge["evidence_requirements"]}
        if not set(envelope_ids).issubset(requirement_ids):
            raise EvaluationError("evidence.invalid", "presentation contains unrequested evidence")
        envelopes = {item["requirement_id"]: item for item in presentation["evidence"]}
        facts: list[dict[str, Any]] = []
        for requirement in challenge["evidence_requirements"]:
            if requirement["id"] not in envelopes:
                if requirement["required"]:
                    raise EvaluationError("evidence.missing", f"missing {requirement['id']}")
                continue
            envelope = envelopes[requirement["id"]]
            if envelope["profile"] not in requirement["profiles"]:
                raise EvaluationError("evidence.invalid", "profile not accepted for requirement")
            if requirement["class"] == "request_integrity":
                facts.extend(self._integrity_facts(challenge, envelope, presenter_key_id))
            elif requirement["class"] == "delegation":
                facts.extend(
                    self._mandate_facts(challenge, requirement, envelope, presenter_key_id)
                )
            else:
                raise EvaluationError("evidence.invalid", f"unsupported class {requirement['class']}")
        return facts

    def _integrity_facts(
        self,
        challenge: dict[str, Any],
        envelope: dict[str, Any],
        presenter_key_id: str,
    ) -> list[dict[str, Any]]:
        value = envelope["value"]
        if not isinstance(value, dict) or value.get("coverage") != "http-request":
            raise EvaluationError("evidence.invalid", "request integrity must be the HTTP request")
        return [
            {
                "claim": "presenter.controls_key",
                "value": presenter_key_id,
                "subject": {"kind": "presenter", "id": presenter_key_id},
                "issuer": "presentation-http-signature",
                "audience": challenge["origin"],
                "evidence_profile": envelope["profile"],
                "presenter_key_id": presenter_key_id,
                "validation": "valid",
            }
        ]

    def _mandate_facts(
        self,
        challenge: dict[str, Any],
        requirement: dict[str, Any],
        envelope: dict[str, Any],
        presenter_key_id: str,
    ) -> list[dict[str, Any]]:
        if envelope["profile"] != MANDATE_PROFILE:
            raise EvaluationError("evidence.invalid", "unsupported delegation profile")
        mandate = envelope["value"]
        if not isinstance(mandate, dict):
            raise EvaluationError("evidence.invalid", "mandate must be an object")
        validate_schema("mandate", mandate)
        if mandate["audience"] != challenge["origin"] or mandate["issuer"] != challenge["origin"]:
            raise EvaluationError("origin.mismatch", "mandate audience is not the challenge origin")
        if mandate["presenter_key_id"] != presenter_key_id:
            raise EvaluationError("binding.mismatch", "mandate presenter does not match")
        if challenge["privacy"]["pairwise_subject_required"]:
            if mandate["subject"]["kind"] != "pairwise_principal":
                raise EvaluationError("evidence.invalid", "pairwise subject required")
        expires = parse_iso(mandate["expires_at"])
        created = parse_iso(mandate["created_at"])
        if self.now > expires:
            raise EvaluationError("mandate.expired", "mandate has expired")
        max_age = requirement.get("max_age_seconds")
        if max_age is not None:
            age = (self.now - created).total_seconds()
            if age > max_age:
                raise EvaluationError("mandate.expired", "mandate exceeds max_age_seconds")
        if not _mandate_covers(mandate["actions"], challenge["request_binding"]["action"]):
            raise EvaluationError("mandate.scope", "mandate does not cover the requested action")
        signature = mandate["signature"]
        key_id = signature["key_id"]
        if key_id not in self.mandate_issuer_keys:
            raise EvaluationError("evidence.untrusted_issuer", "unknown mandate issuer key")
        payload = {k: v for k, v in mandate.items() if k != "signature"}
        protected = dict(payload)
        protected["signature"] = {
            "alg": signature["alg"],
            "key_id": key_id,
        }
        try:
            self.mandate_issuer_keys[key_id].verify(
                b64url_decode(signature["value"]),
                canonical_dumps(protected).encode("utf-8"),
            )
        except Exception as exc:  # noqa: BLE001 - surface as evidence.invalid
            raise EvaluationError("evidence.invalid", "mandate signature invalid") from exc
        if self.fail_closed_on_unknown_revocation:
            raise EvaluationError(
                "evaluation.indeterminate",
                "revocation state unavailable",
                decision="indeterminate",
            )
        digest = sha256_digest_header(canonical_dumps(payload).encode("utf-8"))
        action = challenge["request_binding"]["action"]
        return [
            {
                "claim": "mandate.action",
                "value": action["type"],
                "subject": dict(mandate["subject"]),
                "issuer": mandate["issuer"],
                "audience": mandate["audience"],
                "issued_at": mandate["created_at"],
                "expires_at": mandate["expires_at"],
                "presenter_key_id": presenter_key_id,
                "evidence_profile": MANDATE_PROFILE,
                "evidence_digest": digest,
                "revocation": {"status": "not_revoked", "checked_at": isoformat(self.now)},
                "validation": "valid",
            },
            {
                "claim": "mandate.expires_at",
                "value": mandate["expires_at"],
                "subject": dict(mandate["subject"]),
                "issuer": mandate["issuer"],
                "audience": mandate["audience"],
                "evidence_profile": MANDATE_PROFILE,
                "validation": "valid",
            },
            {
                "claim": "subject.pairwise_id",
                "value": mandate["subject"]["id"],
                "subject": dict(mandate["subject"]),
                "issuer": mandate["issuer"],
                "audience": mandate["audience"],
                "evidence_profile": MANDATE_PROFILE,
                "validation": "valid",
            },
        ]

    def _artifact(
        self,
        challenge: dict[str, Any],
        presentation: dict[str, Any],
        obligations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        claims = {
            "typ": "clearance-artifact",
            "origin": challenge["origin"],
            "action": challenge["request_binding"]["action"]["type"],
            "presenter_key_id": presentation["presenter"]["key_id"],
            "challenge_id": challenge["challenge_id"],
            "request_binding_digest": presentation["request_binding_digest"],
            "expires_at": challenge["expires_at"],
            "obligations": obligations,
        }
        payload = canonical_dumps(claims).encode("utf-8")
        signature = artifact_issuer_private().sign(payload)
        return {
            "format": "urn:agent-clearance:artifact:sender-constrained:0.1",
            "value": b64url(payload) + "." + b64url(signature),
            "expires_at": challenge["expires_at"],
            "key_confirmation": presentation["presenter"]["key_id"],
        }

    def _decision(
        self,
        challenge: dict[str, Any],
        request_binding_digest_value: str,
        value: str,
        obligations: list[dict[str, Any]],
        reasons: list[dict[str, str]],
        continuation_uri: str | None = None,
        clearance_artifact: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        decision: dict[str, Any] = {
            "protocol_version": "0.1",
            "decision_id": f"urn:uuid:{uuid4()}",
            "challenge_id": challenge["challenge_id"],
            "request_binding_digest": request_binding_digest_value,
            "evaluated_at": isoformat(self.now),
            "policy": dict(challenge["policy"]),
            "decision": value,
            "obligations": obligations,
            "reasons": reasons,
        }
        if continuation_uri:
            decision["continuation_uri"] = continuation_uri
        if clearance_artifact:
            decision["clearance_artifact"] = clearance_artifact
        return decision


def challenge_binding_digest(challenge: dict[str, Any]) -> str:
    return request_binding_digest(challenge["request_binding"])


def presentation_digest(body: bytes) -> str:
    return sha256_digest_header(body)


def _load_json_body(body: bytes) -> dict[str, Any]:
    import json

    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvaluationError("evaluation.indeterminate", "presentation is not JSON", "indeterminate") from exc
    if not isinstance(value, dict):
        raise EvaluationError("evaluation.indeterminate", "presentation is not an object", "indeterminate")
    return value


def _mandate_covers(mandate_actions: list[dict[str, Any]], requested: dict[str, Any]) -> bool:
    for action in mandate_actions:
        if action.get("type") != requested.get("type"):
            continue
        if requested.get("resource") and action.get("resource") != requested.get("resource"):
            continue
        if not _constraints_cover(action.get("constraints", {}), requested.get("constraints", {})):
            continue
        return True
    return False


def _constraints_cover(approved: dict[str, Any], requested: dict[str, Any]) -> bool:
    for key, value in requested.items():
        if key not in approved:
            return False
        if isinstance(value, (int, float)) and isinstance(approved[key], (int, float)):
            if value > approved[key]:
                return False
        elif approved[key] != value:
            return False
    return True


def default_origin(now: datetime | None = None) -> Origin:
    return Origin(now=now or datetime.now(timezone.utc))
