from backend.api.app import app, related, search


def test_only_mvp_routes_are_exposed() -> None:
    paths = set(app.openapi()["paths"].keys())
    assert paths == {
        "/recall",
        "/tree",
        "/resource/{id}",
        "/search",
        "/related/{id}",
        "/resolve/{id}",
    }


def test_search_contract_shape() -> None:
    payload = search(q="logs", limit=5)
    assert set(payload.keys()) == {"query", "total", "results"}
    assert payload["query"] == "logs"
    assert isinstance(payload["total"], int)
    assert isinstance(payload["results"], list)


def test_related_uses_explicit_then_fallback() -> None:
    explicit_payload = related("system.logs.rotate")
    explicit_ids = {item["id"] for item in explicit_payload["related"]}
    assert "docs.system.logs.rotation_policy" in explicit_ids

    # Force fallback for this resource by clearing explicit links in-memory.
    from backend.api.app import catalog

    resource = catalog.get("docs.system.logs.rotation_policy")
    previous = list(resource.related)
    resource.related = []
    try:
        fallback_payload = related("docs.system.logs.rotation_policy")
        assert isinstance(fallback_payload["related"], list)
    finally:
        resource.related = previous
