from __future__ import annotations

import pytest

from agent_clearance.fixtures import challenge_object, discovery
from agent_clearance.schemas import validate_schema


def test_origin_rejects_path() -> None:
    challenge = challenge_object()
    challenge["origin"] = "https://travel.example/app"
    with pytest.raises(ValueError, match="origin"):
        validate_schema("challenge", challenge)


def test_allow_cannot_carry_obligations() -> None:
    from agent_clearance.fixtures import happy_path

    _, _, _, decision = happy_path()
    decision["decision"] = "allow"
    with pytest.raises(ValueError):
        validate_schema("decision", decision)


def test_discovery_schema() -> None:
    validate_schema("discovery", discovery())
