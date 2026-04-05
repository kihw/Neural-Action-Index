from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    INVALID_RESOURCE = "INVALID_RESOURCE"
    DUPLICATE_RESOURCE_ID = "DUPLICATE_RESOURCE_ID"
    MISSING_RELATED_RESOURCE = "MISSING_RELATED_RESOURCE"
    MISSING_CONTENT_REF = "MISSING_CONTENT_REF"
    CONTENT_READ_ERROR = "CONTENT_READ_ERROR"


class ApiError(BaseModel):
    code: ErrorCode
    message: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)


class CoreError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.error = ApiError(code=code, message=message, context=context or {})
        super().__init__(message)

    @property
    def code(self) -> ErrorCode:
        return self.error.code

    @property
    def context(self) -> dict[str, Any]:
        return self.error.context
