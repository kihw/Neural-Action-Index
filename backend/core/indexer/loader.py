from __future__ import annotations

from pathlib import Path

import yaml

from backend.core.schema.models import Resource


def load_resources(index_dir: Path) -> list[Resource]:
    resources: list[Resource] = []
    for path in sorted(index_dir.glob("*.yml")) + sorted(index_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        resources.append(Resource.model_validate(raw))
    return resources


def validate_cross_references(resources: list[Resource]) -> None:
    ids = {resource.id for resource in resources}
    for resource in resources:
        missing = [rid for rid in resource.related if rid not in ids]
        if missing:
            raise ValueError(
                f"Resource '{resource.id}' has unresolved related ids: {missing}"
            )
