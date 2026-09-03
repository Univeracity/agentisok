from __future__ import annotations

from agent_clearance.conformance import check_vector, load_vectors


def test_all_committed_vectors() -> None:
    vectors = load_vectors()
    assert len(vectors) >= 17
    for vector in vectors:
        check_vector(vector)
