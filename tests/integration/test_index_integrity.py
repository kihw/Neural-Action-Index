from __future__ import annotations

from pathlib import Path

import yaml

from backend.core.schema.models import Resource


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_index_documents() -> list[tuple[Path, dict]]:
    index_dir = _repo_root() / "resources" / "index"
    docs: list[tuple[Path, dict]] = []
    for path in sorted(index_dir.glob("*.yml")) + sorted(index_dir.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            docs.append((path, yaml.safe_load(f)))
    return docs


def test_index_resources_match_resource_schema() -> None:
    errors: list[str] = []
    for path, resource in _load_index_documents():
        try:
            Resource.model_validate(resource)
        except Exception as exc:  # pydantic aggregates schema issues in exception text
            errors.append(f"{path.name}: {exc}")

    assert not errors, "\n".join(errors)


def test_resource_ids_are_unique() -> None:
    ids = [resource["id"] for _, resource in _load_index_documents()]
    duplicates = sorted({rid for rid in ids if ids.count(rid) > 1})

    assert not duplicates, f"Duplicate resource IDs found: {duplicates}"


def test_content_ref_paths_exist_and_are_readable() -> None:
    root = _repo_root()
    missing_or_unreadable: list[str] = []

    for path, resource in _load_index_documents():
        content_ref = resource["content_ref"]
        target = root / content_ref
        if not target.is_file():
            missing_or_unreadable.append(
                f"{path.name}: content_ref '{content_ref}' does not point to a file"
            )
            continue

        try:
            target.read_text(encoding="utf-8")
        except OSError as exc:
            missing_or_unreadable.append(
                f"{path.name}: content_ref '{content_ref}' is not readable ({exc})"
            )

    assert not missing_or_unreadable, "\n".join(missing_or_unreadable)


def test_related_ids_resolve_to_existing_resources() -> None:
    docs = _load_index_documents()
    known_ids = {resource["id"] for _, resource in docs}

    unresolved: list[str] = []
    for path, resource in docs:
        related_ids = resource.get("related", [])
        for related_id in related_ids:
            if related_id not in known_ids:
                unresolved.append(
                    f"{path.name}: related id '{related_id}' does not exist"
                )

    assert not unresolved, "\n".join(unresolved)
