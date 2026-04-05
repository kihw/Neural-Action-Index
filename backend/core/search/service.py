from __future__ import annotations

from collections.abc import Iterable

from backend.core.schema.models import Resource, SearchHit
from backend.core.search.hybrid import fuse_scores
from backend.core.search.interfaces import SearchDocument
from backend.core.search.lexical import BM25SearchEngine
from backend.core.search.vector import SentenceTransformerEngine


class SearchService:
    def __init__(self, resources: Iterable[Resource]):
        self._resources = {resource.id: resource for resource in resources}
        self._documents = [self._resource_to_document(resource) for resource in resources]
        self._lexical_engine = BM25SearchEngine(self._documents)
        self._vector_engine = SentenceTransformerEngine(self._documents)

    @property
    def vector_enabled(self) -> bool:
        return self._vector_engine.is_enabled

    @staticmethod
    def _resource_to_document(resource: Resource) -> SearchDocument:
        return SearchDocument(
            id=resource.id,
            title=resource.title,
            body=" ".join(
                [
                    resource.description,
                    resource.category,
                    resource.theme,
                    " ".join(resource.tags),
                ]
            ),
            metadata={
                "type": resource.type.value,
                "category": resource.category,
                "theme": resource.theme,
            },
        )

    def search(self, query: str, *, limit: int = 20) -> list[SearchHit]:
        lexical_scores = self._lexical_engine.score(query, limit=limit * 2)
        vector_scores = self._vector_engine.score(query, limit=limit * 2)
        fused_scores, reasons = fuse_scores(lexical_scores, vector_scores)

        ranked_ids = sorted(fused_scores, key=lambda doc_id: fused_scores[doc_id], reverse=True)[
            :limit
        ]

        hits: list[SearchHit] = []
        for doc_id in ranked_ids:
            resource = self._resources[doc_id]
            hits.append(
                SearchHit(
                    id=resource.id,
                    title=resource.title,
                    type=resource.type,
                    category=resource.category,
                    theme=resource.theme,
                    description=resource.description,
                    score=fused_scores[doc_id],
                    match_reasons=reasons.get(doc_id, []),
                )
            )
        return hits
