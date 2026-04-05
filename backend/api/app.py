from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from backend.core.indexer.catalog import ResourceCatalog
from backend.core.resolver.service import resolve_resource_content, summarize_catalog

ROOT = Path(__file__).resolve().parents[2]
catalog = ResourceCatalog(ROOT)
catalog.refresh()

app = FastAPI(title="Neural Action Index", version="0.1.0")


@app.get("/recall")
def recall() -> dict:
    return summarize_catalog(catalog)


@app.get("/tree")
def tree(path: str | None = Query(default=None, description="category[/theme]")) -> dict:
    try:
        raw_tree = catalog.tree(path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    nodes = [
        {"category": category, "themes": themes}
        for category, themes in sorted(raw_tree.items())
    ]
    return {"path": path or "", "nodes": nodes}


@app.get("/resource/{id}")
def get_resource(id: str) -> dict:
    try:
        resource = catalog.get(id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return resource.model_dump()


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)) -> dict:
    hits = catalog.search(q, limit=limit)
    return {
        "query": q,
        "total": len(hits),
        "results": [hit.model_dump() for hit in hits],
    }


@app.get("/related/{id}")
def related(id: str) -> dict:
    try:
        resources = catalog.related(id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "id": id,
        "related": [resource.model_dump() for resource in resources],
    }


@app.get("/resolve/{id}")
def resolve(id: str) -> dict:
    try:
        resource = catalog.get(id)
        content = resolve_resource_content(resource, ROOT)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "id": resource.id,
        "content_ref": resource.content_ref,
        "resolved": {"mime_type": "text/plain", "content": content},
    }
