from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from typing import Any

import pytest

from agent_clearance.fixtures import (
    CHALLENGE_EXPIRES,
    NOW,
    PRESENTATION_CREATED,
    RESPONSE_ID,
    challenge_object,
    unsigned_mandate,
)
from agent_clearance.origin import HttpRequest, Origin, WBA_PROFILE
from agent_clearance.responder import build_presentation, sign_mandate, sign_presentation
from agent_clearance.schemas import validate_schema


def signed_request(challenge: dict[str, Any], mandate: dict[str, Any]) -> HttpRequest:
    presentation = build_presentation(
        challenge, sign_mandate(mandate), PRESENTATION_CREATED, RESPONSE_ID
    )
    return sign_presentation(
        challenge, presentation,
        int(PRESENTATION_CREATED.timestamp()), int(CHALLENGE_EXPIRES.timestamp()),
    )


def assert_denied(
    challenge: dict[str, Any], request: HttpRequest, code: str, **origin_options: Any
) -> None:
    decision = Origin(now=NOW, **origin_options).evaluate(challenge, request)
    validate_schema("decision", decision)
    assert decision["decision"] == "deny"
    assert decision["reasons"][0]["code"] == code
    from agent_clearance.canonical import request_binding_digest

    assert decision["request_binding_digest"] == request_binding_digest(challenge["request_binding"])


def test_invalid_embedded_mandate_returns_a_decision() -> None:
    challenge = challenge_object()
    mandate = unsigned_mandate()
    del mandate["subject"]
    assert_denied(challenge, signed_request(challenge, mandate), "evidence.invalid")


@pytest.mark.parametrize("created,expires", [
    ("2026-08-31T16:01:00Z", "2026-08-31T16:15:00Z"),
    ("2026-08-31T16:01:00Z", "2026-08-31T16:00:40Z"),
])
def test_mandate_validity_window(created: str, expires: str) -> None:
    challenge = challenge_object()
    mandate = unsigned_mandate()
    mandate.update(created_at=created, expires_at=expires)
    assert_denied(challenge, signed_request(challenge, mandate), "evidence.invalid")


@pytest.mark.parametrize("missing", ["resource", "constraints"])
def test_omitting_scope_cannot_expand_a_mandate(missing: str) -> None:
    challenge = challenge_object()
    del challenge["request_binding"]["action"][missing]
    mandate = unsigned_mandate(maximum_results=10)
    assert_denied(challenge, signed_request(challenge, mandate), "mandate.scope")


def test_bounded_read_requires_an_explicit_limit_even_when_both_omit_it() -> None:
    challenge = challenge_object()
    del challenge["request_binding"]["action"]["constraints"]
    mandate = unsigned_mandate()
    del mandate["actions"][0]["constraints"]
    assert_denied(challenge, signed_request(challenge, mandate), "policy.denied")


@pytest.mark.parametrize("approved,requested", [(True, 1), (100, True), (100.0, 50)])
def test_result_limit_requires_positive_integers(approved: Any, requested: Any) -> None:
    challenge = challenge_object()
    challenge["request_binding"]["action"]["constraints"]["maximum_results"] = requested
    mandate = unsigned_mandate(maximum_results=approved)
    assert_denied(challenge, signed_request(challenge, mandate), "mandate.scope")


def test_unknown_numeric_constraints_do_not_inherit_maximum_semantics() -> None:
    challenge = challenge_object()
    challenge["request_binding"]["action"]["constraints"]["minimum_age"] = 18
    mandate = unsigned_mandate()
    mandate["actions"][0]["constraints"]["minimum_age"] = 21
    assert_denied(challenge, signed_request(challenge, mandate), "mandate.scope")


def test_a_tighter_known_result_limit_is_allowed() -> None:
    challenge = challenge_object()
    challenge["request_binding"]["action"]["constraints"]["maximum_results"] = 10
    decision = Origin(now=NOW).evaluate(challenge, signed_request(challenge, unsigned_mandate()))
    assert decision["decision"] == "allow_with_obligations"
    maximum = next(item for item in decision["obligations"] if "maximum-results" in item["type"])
    assert maximum["parameters"]["count"] == 10


def test_a_valid_commit_mandate_still_requires_step_up() -> None:
    challenge = challenge_object()
    challenge["request_binding"]["action"]["type"] = "reservation.commit"
    request = signed_request(challenge, unsigned_mandate(action_type="reservation.commit"))
    decision = Origin(now=NOW).evaluate(challenge, request)
    validate_schema("decision", decision)
    assert decision["decision"] == "step_up"
    assert "clearance_artifact" not in decision


@pytest.mark.parametrize("keyring,code", [
    ("presenter_keys", "evidence.invalid"),
    ("mandate_issuer_keys", "evidence.untrusted_issuer"),
])
def test_empty_trust_configuration_does_not_restore_fixture_keys(keyring: str, code: str) -> None:
    challenge = challenge_object()
    assert_denied(challenge, signed_request(challenge, unsigned_mandate()), code, **{keyring: {}})


def test_endpoint_trailing_slash_is_not_silently_normalized() -> None:
    challenge = challenge_object()
    other = deepcopy(challenge)
    other["presentation_endpoint"] += "/"
    assert_denied(challenge, signed_request(other, unsigned_mandate()), "binding.mismatch")


def test_web_bot_auth_sketch_cannot_be_claimed_by_an_agent_clearance_signature() -> None:
    challenge = challenge_object()
    challenge["evidence_requirements"][0]["profiles"] = [WBA_PROFILE]
    presentation = build_presentation(
        challenge, sign_mandate(unsigned_mandate()), PRESENTATION_CREATED, RESPONSE_ID
    )
    presentation["presenter"]["proof_profile"] = WBA_PROFILE
    presentation["evidence"][0]["profile"] = WBA_PROFILE
    request = sign_presentation(
        challenge, presentation,
        int(PRESENTATION_CREATED.timestamp()), int(CHALLENGE_EXPIRES.timestamp()),
    )
    assert_denied(challenge, request, "evidence.invalid")


def test_concurrent_nonce_consumption_allows_only_one_evaluation() -> None:
    challenge = challenge_object()
    request = signed_request(challenge, unsigned_mandate())
    origin = Origin(now=NOW)
    barrier = Barrier(8)

    def evaluate(_: int) -> dict[str, Any]:
        barrier.wait()
        return origin.evaluate(challenge, request)

    with ThreadPoolExecutor(max_workers=8) as pool:
        decisions = list(pool.map(evaluate, range(8)))
    assert sum(d["decision"] == "allow_with_obligations" for d in decisions) == 1
    assert sum(d["reasons"][0]["code"] == "replay.nonce" for d in decisions) == 7
