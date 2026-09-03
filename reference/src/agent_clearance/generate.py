from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from datetime import datetime, timezone

from agent_clearance.fixtures import (
    NOW,
    PRESENTATION_CREATED,
    RESPONSE_ID,
    discovery,
    happy_path,
    http_request_to_json,
    unsigned_mandate,
    challenge_object,
    protected_request_binding,
)
from agent_clearance.responder import build_presentation, sign_mandate, sign_presentation
from agent_clearance.schemas import repo_root, validate_schema


def _write(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _stable_decision(decision: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(decision)
    out["decision_id"] = "urn:uuid:74ac4c90-4d53-4b2c-a8d3-72e8269fe229"
    return out


def _vector(
    vector_id: str,
    title: str,
    expect: dict[str, Any],
    challenge: dict[str, Any],
    request: Any,
    *,
    now: str | None = None,
    used_nonces: list[str] | None = None,
    supported_obligations: list[str] | None = None,
    fail_closed_on_unknown_revocation: bool = False,
) -> dict[str, Any]:
    return {
        "id": vector_id,
        "title": title,
        "expect": expect,
        "now": now or "2026-08-31T16:00:31Z",
        "used_nonces": used_nonces or [],
        "supported_obligations": supported_obligations,
        "fail_closed_on_unknown_revocation": fail_closed_on_unknown_revocation,
        "challenge": challenge,
        "http": http_request_to_json(request),
    }


def main() -> None:
    root = repo_root()
    examples = root / "examples"
    vectors = root / "conformance" / "vectors"

    challenge, presentation, request, decision = happy_path()
    validate_schema("challenge", challenge)
    validate_schema("presentation", presentation)
    validate_schema("decision", _stable_decision(decision))
    validate_schema("discovery", discovery())
    mandate = next(item["value"] for item in presentation["evidence"] if item["requirement_id"] == "bounded-mandate")
    validate_schema("mandate", mandate)

    _write(examples / "discovery.json", discovery())
    _write(examples / "challenge.json", challenge)
    _write(examples / "mandate.json", mandate)
    _write(examples / "presentation.json", presentation)
    _write(examples / "decision.json", _stable_decision(decision))

    positive = _vector(
        "positive.availability-search",
        "Bounded availability search is allowed with obligations",
        {
            "decision": "allow_with_obligations",
            "reason_codes": ["evidence.sufficient", "policy.bounded_read"],
        },
        challenge,
        request,
    )
    _write(vectors / "positive" / "availability-search.json", positive)

    negatives: list[dict[str, Any]] = []

    negatives.append(
        _vector(
            "negative.replay-nonce",
            "Replayed challenge nonce is rejected",
            {"decision": "deny", "reason_codes": ["replay.nonce"]},
            challenge,
            request,
            used_nonces=[challenge["nonce"]],
        )
    )

    negatives.append(
        _vector(
            "negative.expired-challenge",
            "Expired challenge is rejected",
            {"decision": "deny", "reason_codes": ["challenge.expired"]},
            challenge,
            request,
            now="2026-08-31T16:05:00Z",
        )
    )

    wrong_audience = sign_mandate(unsigned_mandate(audience="https://evil.example"))
    # issuer still travel.example; audience mismatch should hit origin.mismatch.
    # Schema and profile require issuer and audience to be origins; signature still verifies.
    wrong_audience["issuer"] = "https://travel.example"
    wrong_audience = sign_mandate({k: v for k, v in wrong_audience.items() if k != "signature"})
    ch = deepcopy(challenge)
    pres = build_presentation(ch, wrong_audience, PRESENTATION_CREATED, RESPONSE_ID)
    created = int(datetime(2026, 8, 31, 16, 0, 30, tzinfo=timezone.utc).timestamp())
    expires = int(datetime(2026, 8, 31, 16, 2, 0, tzinfo=timezone.utc).timestamp())
    req = sign_presentation(ch, pres, created, expires)
    negatives.append(
        _vector(
            "negative.wrong-audience",
            "Mandate for another origin is rejected",
            {"decision": "deny", "reason_codes": ["origin.mismatch"]},
            ch,
            req,
        )
    )

    mutated = deepcopy(presentation)
    mutated["request_binding_digest"] = "sha-256=:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=:"
    req = sign_presentation(challenge, mutated, created, expires)
    negatives.append(
        _vector(
            "negative.binding-mismatch",
            "Altered request-binding digest is rejected",
            {"decision": "deny", "reason_codes": ["binding.mismatch"]},
            challenge,
            req,
        )
    )

    scoped = challenge_object(protected_request_binding("reservation.commit"))
    # reservation.commit is not covered by the availability mandate.
    mandate = sign_mandate(unsigned_mandate(action_type="availability.read"))
    pres = build_presentation(scoped, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    req = sign_presentation(scoped, pres, created, expires)
    negatives.append(
        _vector(
            "negative.mandate-scope",
            "Mandate that does not cover the requested action is rejected",
            {"decision": "deny", "reason_codes": ["mandate.scope"]},
            scoped,
            req,
        )
    )

    expired_mandate = sign_mandate(
        unsigned_mandate(expires_at=datetime(2026, 8, 31, 16, 0, 10, tzinfo=timezone.utc))
    )
    pres = build_presentation(challenge, expired_mandate, PRESENTATION_CREATED, RESPONSE_ID)
    req = sign_presentation(challenge, pres, created, expires)
    negatives.append(
        _vector(
            "negative.expired-mandate",
            "Expired mandate is rejected",
            {"decision": "deny", "reason_codes": ["mandate.expired"]},
            challenge,
            req,
        )
    )

    missing = deepcopy(presentation)
    missing["evidence"] = [item for item in missing["evidence"] if item["requirement_id"] != "bounded-mandate"]
    req = sign_presentation(challenge, missing, created, expires)
    negatives.append(
        _vector(
            "negative.missing-mandate",
            "Missing mandatory delegation evidence is rejected",
            {"decision": "deny", "reason_codes": ["evidence.missing"]},
            challenge,
            req,
        )
    )

    excessive = challenge_object(protected_request_binding("availability.read", maximum_results=500))
    mandate = sign_mandate(unsigned_mandate(maximum_results=100))
    pres = build_presentation(excessive, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    req = sign_presentation(excessive, pres, created, expires)
    negatives.append(
        _vector(
            "negative.excessive-quantity",
            "Request exceeding mandate quantity bounds is rejected",
            {"decision": "deny", "reason_codes": ["mandate.scope"]},
            excessive,
            req,
        )
    )

    negatives.append(
        _vector(
            "negative.unsupported-obligation",
            "Critical obligation the PEP cannot enforce fails closed",
            {"decision": "deny", "reason_codes": ["obligation.unsupported"]},
            challenge,
            request,
            supported_obligations=[
                "urn:agent-clearance:obligation:rate-limit:0.1",
                "urn:agent-clearance:obligation:one-time:0.1",
                "urn:agent-clearance:obligation:action-restriction:0.1",
                "urn:agent-clearance:obligation:step-up-before:0.1",
            ],
        )
    )

    untrusted = sign_mandate(unsigned_mandate())
    untrusted["signature"]["key_id"] = "https://evil.example/keys/not-trusted"
    # key_id is protected by the signature, but issuer trust is checked first so
    # the stable failure for this vector is evidence.untrusted_issuer.
    pres = build_presentation(challenge, untrusted, PRESENTATION_CREATED, RESPONSE_ID)
    req = sign_presentation(challenge, pres, created, expires)
    negatives.append(
        _vector(
            "negative.untrusted-issuer",
            "Mandate signed under an unknown issuer key is rejected",
            {"decision": "deny", "reason_codes": ["evidence.untrusted_issuer"]},
            challenge,
            req,
        )
    )

    negatives.append(
        _vector(
            "negative.indeterminate-revocation",
            "Unavailable revocation state is indeterminate, not allow",
            {"decision": "indeterminate", "reason_codes": ["evaluation.indeterminate"]},
            challenge,
            request,
            fail_closed_on_unknown_revocation=True,
        )
    )

    signed_at = datetime(2026, 8, 31, 16, 0, 0, tzinfo=timezone.utc)
    expired_at = datetime(2026, 8, 31, 16, 0, 10, tzinfo=timezone.utc)
    mandate = sign_mandate(unsigned_mandate())
    pres = build_presentation(challenge, mandate, signed_at, RESPONSE_ID)
    req = sign_presentation(challenge, pres, int(signed_at.timestamp()), int(expired_at.timestamp()))
    negatives.append(
        _vector(
            "negative.expired-signature",
            "Expired HTTP signature is rejected",
            {"decision": "deny", "reason_codes": ["evidence.invalid"]},
            challenge,
            req,
        )
    )

    future_created = datetime(2026, 8, 31, 16, 1, 40, tzinfo=timezone.utc)
    future_expires = datetime(2026, 8, 31, 16, 1, 50, tzinfo=timezone.utc)
    pres = build_presentation(challenge, mandate, future_created, RESPONSE_ID)
    req = sign_presentation(
        challenge,
        pres,
        int(future_created.timestamp()),
        int(future_expires.timestamp()),
    )
    negatives.append(
        _vector(
            "negative.future-signature",
            "HTTP signature created too far in the future is rejected",
            {"decision": "deny", "reason_codes": ["evidence.invalid"]},
            challenge,
            req,
        )
    )

    pres = build_presentation(challenge, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    req = sign_presentation(
        challenge,
        pres,
        created,
        expires,
        components=["@method", "@authority", "@path", "content-digest"],
    )
    negatives.append(
        _vector(
            "negative.missing-signature-coverage",
            "Presentation signature missing content-type coverage is rejected",
            {"decision": "deny", "reason_codes": ["evidence.invalid"]},
            challenge,
            req,
        )
    )

    duplicate = build_presentation(challenge, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    duplicate["evidence"].append(deepcopy(duplicate["evidence"][0]))
    req = sign_presentation(challenge, duplicate, created, expires)
    negatives.append(
        _vector(
            "negative.duplicate-evidence",
            "Duplicate evidence requirement identifiers are rejected",
            {"decision": "deny", "reason_codes": ["evidence.invalid"]},
            challenge,
            req,
        )
    )

    unrequested = build_presentation(challenge, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    unrequested["evidence"].append(
        {
            "requirement_id": "not-requested",
            "profile": "urn:agent-clearance:profile:unrequested:0.1",
            "format": "embedded",
            "value": {"sensitive": "must-not-be-accepted-or-logged"},
        }
    )
    req = sign_presentation(challenge, unrequested, created, expires)
    negatives.append(
        _vector(
            "negative.unrequested-evidence",
            "Evidence not requested by the challenge is rejected",
            {"decision": "deny", "reason_codes": ["evidence.invalid"]},
            challenge,
            req,
        )
    )

    for vector in negatives:
        filename = vector["id"].split(".", 1)[1].replace("_", "-")
        _write(vectors / "negative" / f"{filename}.json", vector)

    manifest = {
        "protocol_version": "0.1",
        "vectors": [
            {
                "id": positive["id"],
                "file": "positive/availability-search.json",
                "expect": positive["expect"]["decision"],
            }
        ]
        + [
            {
                "id": vector["id"],
                "file": f"negative/{vector['id'].split('.', 1)[1].replace('_', '-')}.json",
                "expect": vector["expect"]["decision"],
            }
            for vector in negatives
        ],
    }
    _write(vectors / "manifest.json", manifest)
    print(f"wrote examples and {1 + len(negatives)} conformance vectors")


if __name__ == "__main__":
    main()
