from __future__ import annotations

import os
from collections.abc import Iterable

from backend.core.search.interfaces import SearchDocument, SearchEngine


class SentenceTransformerEngine(SearchEngine):
    name = "sentence-transformers"

    def __init__(self, documents: Iterable[SearchDocument]):
        self.documents = list(documents)
        self._doc_ids = [doc.id for doc in self.documents]
        self._enabled = os.getenv("NAI_ENABLE_VECTOR_SEARCH", "false").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._is_ready = False
        self._doc_embeddings = None
        self._model = None

        if self._enabled:
            self._initialize_embeddings()

    @property
    def is_enabled(self) -> bool:
        return self._enabled and self._is_ready

    def _initialize_embeddings(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            from sentence_transformers.util import cos_sim
        except ImportError:
            self._enabled = False
            return

        self._cos_sim = cos_sim
        self._model = SentenceTransformer(
            os.getenv("NAI_VECTOR_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
        corpus = [f"{doc.title}. {doc.body}" for doc in self.documents]
        self._doc_embeddings = self._model.encode(corpus, normalize_embeddings=True)
        self._is_ready = True

    def score(self, query: str, *, limit: int = 20) -> dict[str, float]:
        if not self.is_enabled or not query.strip():
            return {}

        query_embedding = self._model.encode(query, normalize_embeddings=True)
        similarities = self._cos_sim(query_embedding, self._doc_embeddings)[0]

        ranked = sorted(
            zip(self._doc_ids, similarities, strict=False),
            key=lambda item: float(item[1]),
            reverse=True,
        )[:limit]
        scores = {doc_id: float(sim) for doc_id, sim in ranked if float(sim) > 0}
        if not scores:
            return {}

        max_score = max(scores.values())
        return {doc_id: value / max_score for doc_id, value in scores.items()}
