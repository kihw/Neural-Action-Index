from __future__ import annotations

from backend.core.schema.models import Resource


def build_adjacency(resources: dict[str, Resource]) -> dict[str, list[str]]:
    return {resource_id: resource.related for resource_id, resource in resources.items()}
