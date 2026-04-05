from pathlib import Path

import pytest

from backend.core.errors import CoreError, ErrorCode
from backend.core.indexer.loader import load_resources, validate_resources
from backend.core.resolver.service import detect_mime_type
from backend.core.schema.models import Resource, ResourceType


@pytest.fixture()
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_index_resources_are_statically_valid(project_root: Path) -> None:
    resources = load_resources(project_root / "resources" / "index")
    validate_resources(project_root, resources)


def test_validate_resources_rejects_duplicate_ids(project_root: Path) -> None:
    resource = Resource(
        id="test.sample.one",
        type=ResourceType.DOC,
        title="Sample",
        category="test",
        theme="sample",
        description="Sample resource",
        content_ref="resources/docs/log_rotation_policy.md",
    )

    with pytest.raises(CoreError) as exc:
        validate_resources(project_root, [resource, resource])

    assert exc.value.code == ErrorCode.DUPLICATE_RESOURCE_ID


def test_validate_resources_rejects_missing_related(project_root: Path) -> None:
    resource = Resource(
        id="test.sample.one",
        type=ResourceType.DOC,
        title="Sample",
        category="test",
        theme="sample",
        description="Sample resource",
        content_ref="resources/docs/log_rotation_policy.md",
        related=["does.not.exist"],
    )

    with pytest.raises(CoreError) as exc:
        validate_resources(project_root, [resource])

    assert exc.value.code == ErrorCode.MISSING_RELATED_RESOURCE


def test_validate_resources_rejects_missing_content_ref(project_root: Path) -> None:
    resource = Resource(
        id="test.sample.one",
        type=ResourceType.DOC,
        title="Sample",
        category="test",
        theme="sample",
        description="Sample resource",
        content_ref="resources/docs/does_not_exist.md",
    )

    with pytest.raises(CoreError) as exc:
        validate_resources(project_root, [resource])

    assert exc.value.code == ErrorCode.MISSING_CONTENT_REF


def test_detect_mime_type() -> None:
    resource = Resource(
        id="test.sample.one",
        type=ResourceType.DOC,
        title="Sample",
        category="test",
        theme="sample",
        description="Sample resource",
        content_ref="resources/docs/log_rotation_policy.md",
    )

    assert detect_mime_type(resource) == "text/markdown"
