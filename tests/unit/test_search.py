from pathlib import Path

from backend.core.indexer.catalog import ResourceCatalog
from backend.core.search.regression import REGRESSION_QUERIES, mrr_at_k, ndcg_at_k


def test_search_returns_match_reasons() -> None:
    root = Path(__file__).resolve().parents[2]
    catalog = ResourceCatalog(root)
    catalog.refresh()

    hits = catalog.search("rotation logs", limit=5)

    assert hits
    assert hits[0].match_reasons
    assert any(reason.startswith("lexical(bm25)=") for reason in hits[0].match_reasons)


def test_regression_metrics_do_not_regress() -> None:
    root = Path(__file__).resolve().parents[2]
    catalog = ResourceCatalog(root)
    catalog.refresh()

    predictions: list[list[str]] = []
    truths: list[tuple[str, ...]] = []

    for test_query in REGRESSION_QUERIES:
        hits = catalog.search(test_query.query, limit=10)
        predictions.append([hit.id for hit in hits])
        truths.append(test_query.relevant_ids)

    mrr = mrr_at_k(predictions, truths, k=10)
    ndcg = ndcg_at_k(predictions, truths, k=10)

    assert mrr >= 0.65
    assert ndcg >= 0.70
