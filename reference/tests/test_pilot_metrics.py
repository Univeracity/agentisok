from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).parents[2]
SCHEMA = json.loads((ROOT / "pilot/schema/shadow-observation.schema.json").read_text())
EXAMPLE = json.loads((ROOT / "pilot/examples/shadow-observation.json").read_text())


def test_shadow_observation_example() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    jsonschema.validate(EXAMPLE, SCHEMA)


@pytest.mark.parametrize("field, value", [("route_template", "/search?q=private"), ("unexpected", "value")])
def test_shadow_observation_rejects_unsafe_shape(field: str, value: str) -> None:
    candidate = {**EXAMPLE, field: value}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(candidate, SCHEMA)
