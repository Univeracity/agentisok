from __future__ import annotations

import base64
import re
from typing import Any
from urllib.parse import urlparse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from agent_clearance.canonical import authority, sha256_digest_header

COMPONENT_RE = re.compile(r'"([^"]+)"')
SIG_INPUT_RE = re.compile(r"^([A-Za-z0-9]+)=\((.*)\);(.*)$")


class HttpSignatureError(ValueError):
    pass


def content_headers(body: bytes, content_type: str) -> dict[str, str]:
    return {
        "content-type": content_type,
        "content-digest": sha256_digest_header(body),
    }


def _derived(name: str, method: str, url: str) -> str:
    parsed = urlparse(url)
    if name == "@method":
        return method.upper()
    if name == "@authority":
        return authority(url)
    if name == "@path":
        return parsed.path or "/"
    if name == "@query":
        return "" if parsed.query == "" else f"?{parsed.query}"
    raise HttpSignatureError(f"unsupported derived component {name}")


def _header(headers: dict[str, str], name: str) -> str:
    lower = {k.lower(): v for k, v in headers.items()}
    if name not in lower:
        raise HttpSignatureError(f"missing header {name}")
    return lower[name]


def signature_base(
    method: str,
    url: str,
    headers: dict[str, str],
    components: list[str],
    params: dict[str, Any],
) -> str:
    lines: list[str] = []
    for component in components:
        if component.startswith("@"):
            value = _derived(component, method, url)
        else:
            value = _header(headers, component)
        lines.append(f'"{component}": {value}')
    lines.append(f'"@signature-params": {_serialize_params(components, params)}')
    return "\n".join(lines)


def _serialize_params(components: list[str], params: dict[str, Any]) -> str:
    inner = " ".join(f'"{c}"' for c in components)
    parts = [f"({inner})"]
    for key, value in params.items():
        if key in {"created", "expires"}:
            parts.append(f"{key}={int(value)}")
        else:
            parts.append(f'{key}="{value}"')
    return ";".join(parts)


def sign_request(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    components: list[str],
    params: dict[str, Any],
    private_key: Ed25519PrivateKey,
    label: str = "sig1",
) -> dict[str, str]:
    ordered = dict(params)
    base = signature_base(method, url, headers, components, ordered)
    signature = private_key.sign(base.encode("utf-8"))
    encoded = base64.b64encode(signature).decode("ascii")
    out = dict(headers)
    out["signature-input"] = f"{label}={_serialize_params(components, ordered)}"
    out["signature"] = f"{label}=:{encoded}:"
    return out


def parse_signature_input(value: str) -> tuple[str, list[str], dict[str, Any]]:
    match = SIG_INPUT_RE.match(value.strip())
    if not match:
        raise HttpSignatureError("unparseable Signature-Input")
    label, inner, rest = match.groups()
    components = COMPONENT_RE.findall(inner)
    if not components:
        raise HttpSignatureError("no covered components")
    params: dict[str, Any] = {}
    for item in rest.split(";"):
        if not item:
            continue
        key, _, raw = item.partition("=")
        if not key or not raw or key in params:
            raise HttpSignatureError("invalid or duplicate signature parameter")
        if raw.startswith('"') and raw.endswith('"'):
            params[key] = raw[1:-1]
        else:
            try:
                params[key] = int(raw)
            except ValueError as exc:
                raise HttpSignatureError("invalid signature parameter") from exc
    return label, components, params


def parse_signature(value: str, label: str) -> bytes:
    prefix = f"{label}=:"
    if not value.startswith(prefix) or not value.endswith(":"):
        raise HttpSignatureError("unparseable Signature")
    try:
        return base64.b64decode(value[len(prefix) : -1], validate=True)
    except ValueError as exc:
        raise HttpSignatureError("invalid signature encoding") from exc


def verify_request(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes,
    public_keys: dict[str, Ed25519PublicKey],
    expected_nonce: str | None = None,
    expected_tag: str = "agent-clearance",
    required_components: set[str] | None = None,
    now: int | None = None,
    not_before: int | None = None,
    not_after: int | None = None,
    max_future_skew: int = 60,
) -> dict[str, Any]:
    lower = {k.lower(): v for k, v in headers.items()}
    if "signature-input" not in lower or "signature" not in lower:
        raise HttpSignatureError("missing signature headers")
    label, components, params = parse_signature_input(lower["signature-input"])
    required = required_components or {"@method", "@authority", "@path", "content-digest"}
    if not required.issubset(components):
        raise HttpSignatureError("insufficient coverage")
    if params.get("tag") != expected_tag:
        raise HttpSignatureError("unexpected tag")
    if params.get("alg") != "ed25519":
        raise HttpSignatureError("unexpected alg")
    if expected_nonce is not None and params.get("nonce") != expected_nonce:
        raise HttpSignatureError("nonce mismatch")
    created = params.get("created")
    expires = params.get("expires")
    if type(created) is not int or type(expires) is not int:
        raise HttpSignatureError("created and expires are required integer parameters")
    if expires <= created:
        raise HttpSignatureError("signature expiry is not after creation")
    if now is not None:
        if created > now + max_future_skew:
            raise HttpSignatureError("signature creation is too far in the future")
        if expires < now:
            raise HttpSignatureError("signature has expired")
    if not_before is not None and created < not_before:
        raise HttpSignatureError("signature predates its challenge")
    if not_after is not None and expires > not_after:
        raise HttpSignatureError("signature outlives its challenge")
    if "content-digest" in components:
        expected_digest = sha256_digest_header(body)
        if _header(lower, "content-digest") != expected_digest:
            raise HttpSignatureError("content-digest mismatch")
    key_id = params.get("keyid")
    if not isinstance(key_id, str) or key_id not in public_keys:
        raise HttpSignatureError("unknown keyid")
    base = signature_base(method, url, lower, components, params)
    signature = parse_signature(lower["signature"], label)
    try:
        public_keys[key_id].verify(signature, base.encode("utf-8"))
    except InvalidSignature as exc:
        raise HttpSignatureError("invalid signature") from exc
    return {"key_id": key_id, "params": params, "components": components, "label": label}
