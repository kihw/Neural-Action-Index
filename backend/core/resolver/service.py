from __future__ import annotations

from pathlib import Path

from backend.core.indexer.catalog import ResourceCatalog
from backend.core.schema.models import Resource


def resolve_resource_content(resource: Resource, root: Path) -> str:
    path = resource.content_path(root)
    if not path.exists():
        raise FileNotFoundError(f"content_ref does not exist for {resource.id}: {path}")
    return path.read_text(encoding="utf-8")


def summarize_catalog(catalog: ResourceCatalog) -> dict:
    recall = catalog.recall()
    return {
        "summary": {
            "total": len(catalog.resources),
            "by_type": {node.key: node.count for node in recall["types"]},
            "by_category": {node.key: node.count for node in recall["categories"]},
        }
    }
