from __future__ import annotations

import mimetypes
from pathlib import Path

from backend.core.errors import CoreError, ErrorCode
from backend.core.schema.models import Resource


def detect_mime_type(resource: Resource) -> str:
    mime, _ = mimetypes.guess_type(resource.content_ref)
    return mime or "text/plain"


def resolve_resource_content(resource: Resource, root: Path) -> str:
    path = resource.content_path(root)
    if not path.exists():
        raise CoreError(
            ErrorCode.MISSING_CONTENT_REF,
            "content_ref does not exist",
            context={"resource_id": resource.id, "content_ref": resource.content_ref},
        )

    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CoreError(
            ErrorCode.CONTENT_READ_ERROR,
            "Unable to read resource content",
            context={"resource_id": resource.id, "content_ref": resource.content_ref},
        ) from exc
