# API Contract v0 (MVP)

Ce contrat décrit les **6 endpoints stricts** du MVP.

## Endpoints

1. `GET /recall`
2. `GET /tree?path=<category[/theme]>`
3. `GET /resource/{id}`
4. `GET /search?q=<query>&limit=<1..100>`
5. `GET /related/{id}`
6. `GET /resolve/{id}`

## Formes de réponse

### `GET /recall` (200)

```json
{
  "summary": {
    "total": 0,
    "by_type": {},
    "by_category": {}
  }
}
```

### `GET /tree` (200)

```json
{
  "path": "category/theme",
  "nodes": []
}
```

`400` si `path` invalide.

### `GET /resource/{id}` (200)

Retourne un objet `resource` conforme au schéma MVP (`docs/contracts/resource.schema.json`).

`404` si `id` inexistant.

### `GET /search` (200)

```json
{
  "query": "...",
  "total": 0,
  "results": []
}
```

`400` si `q` absent/vide ou `limit` hors bornes.

### `GET /related/{id}` (200)

```json
{
  "id": "...",
  "related": []
}
```

`404` si `id` inexistant.

### `GET /resolve/{id}` (200)

```json
{
  "id": "...",
  "content_ref": "...",
  "resolved": {
    "mime_type": "text/plain",
    "content": "..."
  }
}
```

`404` si `id` inexistant, `500` si `content_ref` non résoluble.
