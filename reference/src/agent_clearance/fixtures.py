from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any

from agent_clearance.canonical import isoformat, parse_iso, sha256_digest_header
from agent_clearance.keys import MANDATE_ISSUER_KEY_ID, PRESENTER_KEY_ID
from agent_clearance.origin import HMS_PROFILE, MANDATE_PROFILE, Origin
from agent_clearance.responder import build_presentation, sign_mandate, sign_presentation

ORIGIN = "https://travel.example"
PRESENTATION_ENDPOINT = "https://travel.example/.well-known/agent-clearance/presentations"
CHALLENGE_ID = "urn:uuid:0d191f2f-73ae-4d41-b662-e1f45a968762"
RESPONSE_ID = "urn:uuid:1b36ca5d-0499-489e-a4af-04618f4b6871"
MANDATE_ID = "urn:uuid:9c0e2b1a-7d54-4f0e-9a6b-2c8f41d0e7aa"
NONCE = "xW5qjPzVZfR7L2eH9sK4mQ1uB8cD6nT3aY0iO7pE5gA"
PAIRWISE_SUBJECT = "urn:uuid:43ff2d65-a302-4b52-9f80-f1f3776d8b71"
PROTECTED_BODY = b'{"check_in":"2026-09-10","nights":1}'
NOW = datetime(2026, 8, 31, 16, 0, 31, tzinfo=timezone.utc)
CHALLENGE_CREATED = datetime(2026, 8, 31, 16, 0, 0, tzinfo=timezone.utc)
CHALLENGE_EXPIRES = datetime(2026, 8, 31, 16, 2, 0, tzinfo=timezone.utc)
PRESENTATION_CREATED = datetime(2026, 8, 31, 16, 0, 30, tzinfo=timezone.utc)
MANDATE_CREATED = datetime(2026, 8, 31, 15, 50, 0, tzinfo=timezone.utc)
MANDATE_EXPIRES = datetime(2026, 8, 31, 16, 15, 0, tzinfo=timezone.utc)


def discovery() -> dict[str, Any]:
    return {
        "protocol_versions": ["0.1"],
        "presentation_endpoint": PRESENTATION_ENDPOINT,
        "evidence_profiles": [HMS_PROFILE, MANDATE_PROFILE],
        "http_signature_algs": ["ed25519"],
        "max_body_bytes": 65536,
        "mandate_issuer_key_id": MANDATE_ISSUER_KEY_ID,
    }


def protected_request_binding(action_type: str = "availability.read", maximum_results: int = 100) -> dict[str, Any]:
    return {
        "method": "POST",
        "target_uri": "https://travel.example/availability/search",
        "content_digest": sha256_digest_header(PROTECTED_BODY),
        "action": {
            "type": action_type,
            "resource": "hotel_inventory",
            "constraints": {"maximum_results": maximum_results},
        },
    }


def unsigned_mandate(
    *,
    audience: str = ORIGIN,
    action_type: str = "availability.read",
    maximum_results: int = 100,
    presenter_key_id: str = PRESENTER_KEY_ID,
    expires_at: datetime = MANDATE_EXPIRES,
) -> dict[str, Any]:
    return {
        "mandate_id": MANDATE_ID,
        "profile": MANDATE_PROFILE,
        "issuer": ORIGIN,
        "audience": audience,
        "subject": {"kind": "pairwise_principal", "id": PAIRWISE_SUBJECT},
        "presenter_key_id": presenter_key_id,
        "actions": [
            {
                "type": action_type,
                "resource": "hotel_inventory",
                "constraints": {"maximum_results": maximum_results},
            }
        ],
        "created_at": isoformat(MANDATE_CREATED),
        "expires_at": isoformat(expires_at),
        "approval": {
            "method": "passkey",
            "displayed": {
                "origin": ORIGIN,
                "action": action_type,
                "resource": "hotel_inventory",
                "expires_at": isoformat(expires_at),
                "presenter_key_id": presenter_key_id,
            },
        },
    }


def challenge_object(binding: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "protocol_version": "0.1",
        "challenge_id": CHALLENGE_ID,
        "nonce": NONCE,
        "origin": ORIGIN,
        "created_at": isoformat(CHALLENGE_CREATED),
        "expires_at": isoformat(CHALLENGE_EXPIRES),
        "request_binding": binding or protected_request_binding(),
        "evidence_requirements": [
            {
                "id": "request-proof",
                "class": "request_integrity",
                "profiles": [HMS_PROFILE],
                "required": True,
                "max_age_seconds": 120,
                "disclosures": [],
            },
            {
                "id": "bounded-mandate",
                "class": "delegation",
                "profiles": [MANDATE_PROFILE],
                "required": True,
                "max_age_seconds": 900,
                "disclosures": ["mandate.action", "mandate.expires_at", "subject.pairwise_id"],
            },
        ],
        "policy": {"id": "availability-agent-policy", "version": "2026-08-31.1"},
        "privacy": {
            "pairwise_subject_required": True,
            "natural_language_task_forbidden": True,
            "retention_hint_seconds": 86400,
        },
        "presentation_endpoint": PRESENTATION_ENDPOINT,
    }


def happy_path(
    *,
    mandate: dict[str, Any] | None = None,
    challenge: dict[str, Any] | None = None,
    now: datetime = NOW,
) -> tuple[dict[str, Any], dict[str, Any], Any, dict[str, Any]]:
    challenge = copy.deepcopy(challenge or challenge_object())
    mandate = sign_mandate(mandate or unsigned_mandate())
    presentation = build_presentation(challenge, mandate, PRESENTATION_CREATED, RESPONSE_ID)
    created = int(PRESENTATION_CREATED.timestamp())
    expires = int(parse_iso(challenge["expires_at"]).timestamp())
    request = sign_presentation(challenge, presentation, created, expires)
    origin = Origin(now=now)
    decision = origin.evaluate(challenge, request)
    return challenge, presentation, request, decision


def http_request_to_json(request: Any) -> dict[str, Any]:
    return {
        "method": request.method,
        "url": request.url,
        "headers": request.headers,
        "body": request.body.decode("utf-8"),
    }
