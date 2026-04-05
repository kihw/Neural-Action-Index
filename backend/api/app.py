from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.errors import CoreError, ErrorCode
from backend.core.indexer.catalog import ResourceCatalog
from backend.core.resolver.service import detect_mime_type, resolve_resource_content, summarize_catalog
from backend.core.schema.models import ApiTrace, ResourceResponse

ROOT = Path(__file__).resolve().parents[2]
catalog = ResourceCatalog(ROOT)
catalog.refresh()


app = FastAPI(title="Neural Action Index", version="0.1.0")

FRONTEND_DIR = ROOT / "frontend"
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


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
    mode = "hybrid" if catalog.vector_search_enabled else "lexical"
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
