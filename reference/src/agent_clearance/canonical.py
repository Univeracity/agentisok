from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse


def canonical_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest_header(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha-256=:" + base64.b64encode(digest).decode("ascii") + ":"


def request_binding_digest(binding: dict[str, Any]) -> str:
    obj: dict[str, Any] = {
        "action": binding["action"],
        "method": binding["method"],
        "target_uri": binding["target_uri"],
    }
    if "content_digest" in binding:
        obj["content_digest"] = binding["content_digest"]
    return sha256_digest_header(canonical_dumps(obj).encode("utf-8"))


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def isoformat(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def origin_form(url_or_origin: str) -> str:
    parsed = urlparse(url_or_origin)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("origin must be https")
    host = parsed.hostname.lower()
    if parsed.port and parsed.port != 443:
        return f"https://{host}:{parsed.port}"
    return f"https://{host}"


def authority(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.port and parsed.port != 443:
        return f"{host}:{parsed.port}"
    return host


def same_origin(endpoint: str, origin: str) -> bool:
    parsed = urlparse(endpoint)
    return parsed.scheme == "https" and origin_form(endpoint) == origin_form(origin)
