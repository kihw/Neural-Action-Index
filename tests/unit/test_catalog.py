from pathlib import Path

from backend.core.indexer.catalog import ResourceCatalog


def test_catalog_loads_resources() -> None:
    root = Path(__file__).resolve().parents[2]
    catalog = ResourceCatalog(root)
    catalog.refresh()

    assert "system.logs.rotate" in catalog.resources
    assert catalog.get("docs.system.logs.rotation_policy").type.value == "doc"


def test_related_resources() -> None:
    root = Path(__file__).resolve().parents[2]
    catalog = ResourceCatalog(root)
    catalog.refresh()

    related_ids = {resource.id for resource in catalog.related("system.logs.rotate")}
    assert "docs.system.logs.rotation_policy" in related_ids
    assert "config.system.logs.default" in related_ids
