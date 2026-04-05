from __future__ import annotations

from backend.api.app import get_resource, resolve, search


EXISTING_RESOURCE_ID = "system.logs.rotate"


def test_search_smoke() -> None:
    payload = search(q="logs", limit=20)

    assert payload["query"] == "logs"
    assert "results" in payload


def test_resource_smoke() -> None:
    payload = get_resource(resource_id=EXISTING_RESOURCE_ID).model_dump()

    assert payload["resource"]["id"] == EXISTING_RESOURCE_ID


def test_resolve_smoke() -> None:
    payload = resolve(resource_id=EXISTING_RESOURCE_ID).model_dump()

    assert payload["resource"]["id"] == EXISTING_RESOURCE_ID
    assert isinstance(payload["resolved_content"], str)
    assert payload["resolved_content"].strip()
