from __future__ import annotations

import json
import sys
from typing import Any

from agent_clearance.canonical import parse_iso
from agent_clearance.origin import CORE_OBLIGATIONS, HttpRequest, Origin
from agent_clearance.schemas import repo_root


def load_vectors() -> list[dict[str, Any]]:
    root = repo_root() / "conformance" / "vectors"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    vectors = []
    for entry in manifest["vectors"]:
        document = json.loads((root / entry["file"]).read_text(encoding="utf-8"))
        vectors.append(document)
    return vectors


def run_vector(vector: dict[str, Any]) -> dict[str, Any]:
    http = vector["http"]
    request = HttpRequest(
        method=http["method"],
        url=http["url"],
        headers=http["headers"],
        body=http["body"].encode("utf-8"),
    )
    supported = vector.get("supported_obligations")
    origin = Origin(
        now=parse_iso(vector["now"]),
        used_nonces=set(vector.get("used_nonces") or []),
        supported_obligations=set(supported) if supported is not None else set(CORE_OBLIGATIONS),
        fail_closed_on_unknown_revocation=bool(vector.get("fail_closed_on_unknown_revocation")),
    )
    return origin.evaluate(vector["challenge"], request)


def check_vector(vector: dict[str, Any]) -> None:
    decision = run_vector(vector)
    expected = vector["expect"]
    if decision["decision"] != expected["decision"]:
        raise AssertionError(
            f"{vector['id']}: expected {expected['decision']}, got {decision['decision']} ({decision['reasons']})"
        )
    codes = [item["code"] for item in decision["reasons"]]
    for code in expected.get("reason_codes", []):
        if code not in codes:
            raise AssertionError(f"{vector['id']}: expected reason {code}, got {codes}")


def main() -> int:
    vectors = load_vectors()
    failures = 0
    for vector in vectors:
        try:
            check_vector(vector)
            print(f"PASS {vector['id']}")
        except Exception as exc:  # noqa: BLE001 - conformance CLI reports every vector
            failures += 1
            print(f"FAIL {vector['id']}: {exc}")
    print(f"{len(vectors) - failures} passed, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
