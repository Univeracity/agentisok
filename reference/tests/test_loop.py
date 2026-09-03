from __future__ import annotations

from datetime import datetime, timezone

from agent_clearance.canonical import request_binding_digest
from agent_clearance.fixtures import (
    CHALLENGE_EXPIRES,
    NOW,
    PRESENTATION_CREATED,
    RESPONSE_ID,
    challenge_object,
    happy_path,
    unsigned_mandate,
)
from agent_clearance.keys import MANDATE_ISSUER_KEY_ID, public_key
from agent_clearance.origin import HttpRequest, Origin
from agent_clearance.responder import build_presentation, sign_mandate, sign_presentation
from agent_clearance.schemas import validate_schema


def test_happy_path_allows_bounded_read() -> None:
    challenge, presentation, request, decision = happy_path()
    validate_schema("challenge", challenge)
    validate_schema("presentation", presentation)
    validate_schema("decision", decision)
    assert decision["decision"] == "allow_with_obligations"
    assert presentation["request_binding_digest"] == request_binding_digest(challenge["request_binding"])
    assert "proof" not in presentation
    assert decision["clearance_artifact"]["key_confirmation"] == presentation["presenter"]["key_id"]
    types = {item["type"] for item in decision["obligations"]}
    assert "urn:agent-clearance:obligation:step-up-before:0.1" in types


def test_replay_is_rejected_on_second_presentation() -> None:
    challenge, _, request, _ = happy_path()
    origin = Origin(now=datetime(2026, 8, 31, 16, 0, 31, tzinfo=timezone.utc))
    first = origin.evaluate(challenge, request)
    second = origin.evaluate(challenge, request)
    assert first["decision"] == "allow_with_obligations"
    assert second["decision"] == "deny"
    assert second["reasons"][0]["code"] == "replay.nonce"


def test_mandate_signature_round_trip() -> None:
    mandate = sign_mandate(unsigned_mandate())
    validate_schema("mandate", mandate)
    assert mandate["signature"]["alg"] == "ed25519"


def test_mandate_signature_protects_key_metadata() -> None:
    alias = "https://travel.example/.well-known/agent-clearance/keys/alias"
    mandate = sign_mandate(unsigned_mandate())
    mandate["signature"]["key_id"] = alias
    challenge = challenge_object()
    presentation = build_presentation(challenge, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    request = sign_presentation(
        challenge,
        presentation,
        int(PRESENTATION_CREATED.timestamp()),
        int(CHALLENGE_EXPIRES.timestamp()),
    )
    origin = Origin(
        now=NOW,
        mandate_issuer_keys={
            MANDATE_ISSUER_KEY_ID: public_key("mandate-issuer"),
            alias: public_key("mandate-issuer"),
        },
    )
    decision = origin.evaluate(challenge, request)
    assert decision["decision"] == "deny"
    assert decision["reasons"][0]["code"] == "evidence.invalid"


def test_oversized_presentation_is_rejected_before_parsing() -> None:
    challenge = challenge_object()
    request = HttpRequest(
        method="POST",
        url=challenge["presentation_endpoint"],
        headers={},
        body=b"{" + b"x" * 65536 + b"}",
    )
    decision = Origin(now=NOW).evaluate(challenge, request)
    assert decision["decision"] == "deny"
    assert decision["reasons"][0]["code"] == "evidence.invalid"
