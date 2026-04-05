from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SearchDocument:
    id: str
    title: str
    body: str
    metadata: dict[str, str]


class SearchEngine(Protocol):
    name: str

    def score(self, query: str, *, limit: int = 20) -> dict[str, float]:
        """Return normalized scores per document id."""
