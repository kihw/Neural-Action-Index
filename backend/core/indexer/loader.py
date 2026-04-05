from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from backend.core.errors import CoreError, ErrorCode
from backend.core.schema.models import Resource


def _iter_index_files(index_dir: Path) -> list[Path]:
    return sorted(index_dir.glob("*.yml")) + sorted(index_dir.glob("*.yaml"))


def load_resources(index_dir: Path) -> list[Resource]:
    resources: list[Resource] = []
    for path in _iter_index_files(index_dir):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        try:
            resources.append(Resource.model_validate(raw))
        except ValidationError as exc:
            raise CoreError(
                ErrorCode.INVALID_RESOURCE,
                "Resource schema validation failed",
                context={"index_file": str(path), "errors": exc.errors()},
            ) from exc
    return resources


def validate_resources(root: Path, resources: list[Resource]) -> None:
    ids: set[str] = set()
    for resource in resources:
        if resource.id in ids:
            raise CoreError(
                ErrorCode.DUPLICATE_RESOURCE_ID,
                f"Duplicate resource id: {resource.id}",
                context={"resource_id": resource.id},
            )
        ids.add(resource.id)

        content_path = resource.content_path(root)
        if not content_path.exists():
            raise CoreError(
                ErrorCode.MISSING_CONTENT_REF,
                "content_ref does not exist",
                context={"resource_id": resource.id, "content_ref": resource.content_ref},
            )

    for resource in resources:
        missing_related = [related_id for related_id in resource.related if related_id not in ids]
        if missing_related:
            raise CoreError(
                ErrorCode.MISSING_RELATED_RESOURCE,
                "Resource has unresolved related ids",
                context={"resource_id": resource.id, "missing_related": missing_related},
            )
