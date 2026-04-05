from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ResourceType(str, Enum):
    ACTION = "action"
    CODE = "code"
    DOC = "doc"
    CONFIG = "config"
    TEMPLATE = "template"
    REFERENCE = "reference"


class VariableSpec(BaseModel):
    name: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    required: bool = True
    default: Any | None = None
    description: str | None = None


class Metadata(BaseModel):
    author: str | None = None
    version: str | None = None
    updated_at: date | None = None


class Resource(BaseModel):
    id: str = Field(min_length=3, pattern=r"^[a-z0-9]+(\.[a-z0-9_\-]+)+$")
    type: ResourceType
    title: str = Field(min_length=3)
    category: str = Field(min_length=1)
    theme: str = Field(min_length=1)
    description: str = Field(min_length=5)
    content_ref: str = Field(min_length=1)
    variables: list[VariableSpec] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=Metadata)

    @field_validator("related")
    @classmethod
    def unique_related(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    def content_path(self, root: Path) -> Path:
        return root / self.content_ref


class RecallNode(BaseModel):
    key: str
    count: int


class SearchHit(BaseModel):
    id: str
    title: str
    type: ResourceType
    category: str
    theme: str
    description: str
    score: float
    match_reasons: list[str] = Field(default_factory=list)


class ApiTrace(BaseModel):
    source: str
    detail: str


class ResourceResponse(BaseModel):
    resource: Resource
    resolved_content: str | None = None
    confidence: float = 1.0
    trace: list[ApiTrace] = Field(default_factory=list)
