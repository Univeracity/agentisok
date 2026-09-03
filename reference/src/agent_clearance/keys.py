from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

PRESENTER_KEY_ID = "https://harness.example/keys/k/8f3a1c"
MANDATE_ISSUER_KEY_ID = "https://travel.example/.well-known/agent-clearance/keys/mandate-issuer"
ARTIFACT_KEY_ID = "https://travel.example/.well-known/agent-clearance/keys/artifact-issuer"

_SEED_PREFIX = "agent-clearance-test-key-do-not-use:"


def private_key(label: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256((_SEED_PREFIX + label).encode("utf-8")).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def public_key(label: str) -> Ed25519PublicKey:
    return private_key(label).public_key()


def presenter_private() -> Ed25519PrivateKey:
    return private_key("presenter")


def mandate_issuer_private() -> Ed25519PrivateKey:
    return private_key("mandate-issuer")


def artifact_issuer_private() -> Ed25519PrivateKey:
    return private_key("artifact-issuer")


def raw_public(label: str) -> bytes:
    return public_key(label).public_bytes_raw()
