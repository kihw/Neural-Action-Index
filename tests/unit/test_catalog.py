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


def test_secondary_indexes() -> None:
    root = Path(__file__).resolve().parents[2]
    catalog = ResourceCatalog(root)
    catalog.refresh()

    assert {item.id for item in catalog.by_tag("linux")} == {"system.logs.rotate"}
    assert "system.logs.rotate" in {item.id for item in catalog.by_category("system")}
    assert "system.logs.rotate" in {item.id for item in catalog.by_theme("logs")}
