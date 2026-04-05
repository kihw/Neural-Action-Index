from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable

from backend.core.search.interfaces import SearchDocument, SearchEngine

try:
    from rank_bm25 import BM25Okapi  # type: ignore
except ImportError:  # pragma: no cover
    class BM25Okapi:  # fallback when dependency is unavailable in sandbox
        def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
            self.corpus = corpus
            self.k1 = k1
            self.b = b
            self.doc_freqs = [Counter(doc) for doc in corpus]
            self.doc_len = [len(doc) for doc in corpus]
            self.avgdl = sum(self.doc_len) / max(len(self.doc_len), 1)
            self.idf = self._build_idf(corpus)

        def _build_idf(self, corpus: list[list[str]]) -> dict[str, float]:
            n_docs = len(corpus)
            dfs: Counter[str] = Counter()
            for doc in corpus:
                dfs.update(set(doc))
            return {
                term: math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                for term, df in dfs.items()
            }

        def get_scores(self, query_tokens: list[str]) -> list[float]:
            scores: list[float] = []
            for idx, freqs in enumerate(self.doc_freqs):
                dl = self.doc_len[idx]
                denom_base = self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1e-9))
                score = 0.0
                for term in query_tokens:
                    tf = freqs.get(term, 0)
                    if tf == 0:
                        continue
                    idf = self.idf.get(term, 0.0)
                    score += idf * ((tf * (self.k1 + 1)) / (tf + denom_base))
                scores.append(score)
            return scores


_TOKEN_PATTERN = re.compile(r"[a-z0-9_\-.]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())


class BM25SearchEngine(SearchEngine):
    name = "bm25"

    def __init__(self, documents: Iterable[SearchDocument]):
        self.documents = list(documents)
        self._doc_ids = [doc.id for doc in self.documents]
        self._corpus = [_tokenize(f"{doc.id} {doc.title} {doc.body}") for doc in self.documents]
        self._model = BM25Okapi(self._corpus)

    def score(self, query: str, *, limit: int = 20) -> dict[str, float]:
        tokens = _tokenize(query)
        if not tokens:
            return {}

        raw_scores = self._model.get_scores(tokens)
        if len(raw_scores) == 0:
            return {}

        max_score = max(raw_scores)
        if max_score <= 0:
            return {}

        paired = sorted(
            zip(self._doc_ids, raw_scores, strict=False),
            key=lambda item: item[1],
            reverse=True,
        )[:limit]
        return {doc_id: float(score / max_score) for doc_id, score in paired if score > 0}
