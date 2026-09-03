from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from agent_clearance.canonical import canonical_dumps, isoformat, request_binding_digest
from agent_clearance.http_sig import content_headers, sign_request
from agent_clearance.keys import (
    MANDATE_ISSUER_KEY_ID,
    PRESENTER_KEY_ID,
    mandate_issuer_private,
    presenter_private,
)
from agent_clearance.origin import HMS_PROFILE, MANDATE_PROFILE, HttpRequest

PRESENTATION_COMPONENTS = [
    "@method",
    "@authority",
    "@path",
    "content-digest",
    "content-type",
]


def sign_mandate(mandate: dict[str, Any]) -> dict[str, Any]:
    unsigned = {k: v for k, v in mandate.items() if k != "signature"}
    protected = dict(unsigned)
    protected["signature"] = {
        "alg": "ed25519",
        "key_id": MANDATE_ISSUER_KEY_ID,
    }
    value = mandate_issuer_private().sign(canonical_dumps(protected).encode("utf-8"))
    from agent_clearance.canonical import b64url

    signed = dict(protected)
    signed["signature"]["value"] = b64url(value)
    return signed


def build_presentation(
    challenge: dict[str, Any],
    mandate: dict[str, Any],
    created_at: datetime,
    response_id: str | None = None,
) -> dict[str, Any]:
    return {
        "protocol_version": "0.1",
        "response_id": response_id or f"urn:uuid:{uuid4()}",
        "challenge_id": challenge["challenge_id"],
        "created_at": isoformat(created_at),
        "request_binding_digest": request_binding_digest(challenge["request_binding"]),
        "presenter": {
            "key_id": PRESENTER_KEY_ID,
            "proof_profile": HMS_PROFILE,
        },
        "evidence": [
            {
                "requirement_id": "request-proof",
                "profile": HMS_PROFILE,
                "format": "embedded",
                "value": {"coverage": "http-request", "signature_label": "sig1"},
            },
            {
                "requirement_id": "bounded-mandate",
                "profile": MANDATE_PROFILE,
                "format": "embedded",
                "value": mandate,
            },
        ],
    }


def sign_presentation(
    challenge: dict[str, Any],
    presentation: dict[str, Any],
    created: int,
    expires: int,
    components: list[str] | None = None,
) -> HttpRequest:
    body = canonical_dumps(presentation).encode("utf-8")
    headers = content_headers(body, "application/agent-clearance-presentation+json")
    signed = sign_request(
        method="POST",
        url=challenge["presentation_endpoint"],
        headers=headers,
        components=components or PRESENTATION_COMPONENTS,
        params={
            "created": created,
            "expires": expires,
            "keyid": PRESENTER_KEY_ID,
            "alg": "ed25519",
            "nonce": challenge["nonce"],
            "tag": "agent-clearance",
        },
        private_key=presenter_private(),
    )
    return HttpRequest(
        method="POST",
        url=challenge["presentation_endpoint"],
        headers=signed,
        body=body,
    )


def presentation_from_bytes(body: bytes) -> dict[str, Any]:
    return json.loads(body.decode("utf-8"))
