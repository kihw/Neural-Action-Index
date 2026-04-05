from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HybridWeights:
    lexical: float = 0.70
    vector: float = 0.30


def fuse_scores(
    lexical_scores: dict[str, float],
    vector_scores: dict[str, float],
    *,
    weights: HybridWeights = HybridWeights(),
) -> tuple[dict[str, float], dict[str, list[str]]]:
    """
    Fusion formula:
      final_score(d) = (w_lex * s_lex(d)) + (w_vec * s_vec(d))
    where each engine score is normalized in [0, 1].
    """
    merged_ids = set(lexical_scores) | set(vector_scores)
    scores: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}

    for doc_id in merged_ids:
        lex_score = lexical_scores.get(doc_id, 0.0)
        vec_score = vector_scores.get(doc_id, 0.0)
        final_score = (weights.lexical * lex_score) + (weights.vector * vec_score)

        reason_parts: list[str] = [f"fusion={final_score:.4f}"]
        if lex_score > 0:
            reason_parts.append(f"lexical(bm25)={lex_score:.4f}")
        if vec_score > 0:
            reason_parts.append(f"vector(st)={vec_score:.4f}")

        scores[doc_id] = final_score
        reasons[doc_id] = reason_parts

    return scores, reasons
