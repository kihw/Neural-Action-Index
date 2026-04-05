from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionQuery:
    query: str
    relevant_ids: tuple[str, ...]


REGRESSION_QUERIES: tuple[RegressionQuery, ...] = (
    RegressionQuery(
        query="rotation logs linux",
        relevant_ids=("system.logs.rotate", "docs.system.logs.rotation_policy"),
    ),
    RegressionQuery(
        query="configuration par défaut logs",
        relevant_ids=("config.system.logs.default",),
    ),
    RegressionQuery(
        query="extraire champs csv",
        relevant_ids=("action.data.csv.clean", "code.csv.extract_fields"),
    ),
)


def mrr_at_k(predictions: list[list[str]], truths: list[tuple[str, ...]], k: int = 10) -> float:
    rr_sum = 0.0
    for predicted, expected in zip(predictions, truths, strict=True):
        rank = 0
        expected_set = set(expected)
        for idx, doc_id in enumerate(predicted[:k], start=1):
            if doc_id in expected_set:
                rank = idx
                break
        if rank > 0:
            rr_sum += 1.0 / rank
    return rr_sum / len(predictions)


def ndcg_at_k(predictions: list[list[str]], truths: list[tuple[str, ...]], k: int = 10) -> float:
    def _dcg(ranked_docs: list[str], relevant: set[str]) -> float:
        score = 0.0
        for idx, doc_id in enumerate(ranked_docs[:k], start=1):
            rel = 1.0 if doc_id in relevant else 0.0
            if rel > 0:
                score += rel / math.log2(idx + 1)
        return score

    total = 0.0
    for predicted, expected in zip(predictions, truths, strict=True):
        relevant = set(expected)
        dcg = _dcg(predicted, relevant)
        ideal = _dcg(list(expected), relevant)
        total += 0.0 if ideal == 0 else dcg / ideal
    return total / len(predictions)
