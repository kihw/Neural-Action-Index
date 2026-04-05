from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from backend.core.errors import CoreError, ErrorCode
from backend.core.indexer.catalog import ResourceCatalog
from backend.core.resolver.service import detect_mime_type, resolve_resource_content
from backend.core.schema.models import ApiTrace, ResourceResponse

ROOT = Path(__file__).resolve().parents[2]
catalog = ResourceCatalog(ROOT)
catalog.refresh()

app = FastAPI(title="Neural Action Index", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/recall")
def recall() -> dict:
    return catalog.recall()


@app.get("/tree")
def tree(path: str | None = Query(default=None, description="category[/theme]")) -> dict:
    try:
        return catalog.tree(path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/resource/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: str) -> ResourceResponse:
    try:
        resource = catalog.get(resource_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ResourceResponse(
        resource=resource,
        trace=[ApiTrace(source="catalog", detail="resource metadata fetched")],
    )


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)) -> dict:
    hits = catalog.search(q, limit=limit)
    return {
        "query": q,
        "count": len(hits),
        "results": [hit.model_dump() for hit in hits],
        "trace": [
            {"source": "lexical-mvp", "detail": "substring matching over indexed fields"}
        ],
    }


@app.get("/related/{resource_id}")
def related(resource_id: str) -> dict:
    try:
        resources = catalog.related(resource_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "id": resource_id,
        "count": len(resources),
        "results": [resource.model_dump() for resource in resources],
    }


@app.get("/resolve/{resource_id}", response_model=ResourceResponse)
def resolve(resource_id: str) -> ResourceResponse:
    try:
        resource = catalog.get(resource_id)
        content = resolve_resource_content(resource, ROOT)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CoreError as exc:
        status_code = 404 if exc.code == ErrorCode.MISSING_CONTENT_REF else 500
        raise HTTPException(status_code=status_code, detail=exc.error.model_dump()) from exc

    mime_type = detect_mime_type(resource)

    return ResourceResponse(
        resource=resource,
        resolved_content=content,
        confidence=1.0,
        trace=[
            ApiTrace(source="catalog", detail="resource metadata fetched"),
            ApiTrace(source="resolver", detail=f"resolved from {resource.content_ref} ({mime_type})"),
        ],
    )
