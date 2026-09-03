from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_NAMES = {
    "challenge": "challenge.schema.json",
    "presentation": "presentation.schema.json",
    "decision": "decision.schema.json",
    "discovery": "discovery.schema.json",
    "fact": "fact.schema.json",
    "mandate": "mandate.schema.json",
}


def repo_root() -> Path:
    for path in Path(__file__).resolve().parents:
        if (path / "spec" / "schema" / "challenge.schema.json").is_file():
            return path
    raise RuntimeError("could not locate repository root")


def schema_dir() -> Path:
    return repo_root() / "spec" / "schema"


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    filename = SCHEMA_NAMES[name]
    return json.loads((schema_dir() / filename).read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(
        load_schema(name),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def validate_schema(name: str, document: dict[str, Any]) -> None:
    errors = sorted(validator(name).iter_errors(document), key=lambda e: e.path)
    if errors:
        first = errors[0]
        path = "/".join(str(part) for part in first.path) or "<root>"
        raise ValueError(f"{name} schema: {path}: {first.message}")
