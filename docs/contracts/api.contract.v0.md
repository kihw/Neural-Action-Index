# API contract v0 (MVP)

Ce document normalise les exemples de requête/réponse des endpoints MVP, les conventions de données, et la stratégie d'évolution vers `v1`.

## 1) Conventions transverses

### 1.1 Convention d'ID

- Format canonique: `domain.topic.item`.
- Regex v0: `^[a-z0-9]+(?:\.[a-z0-9][a-z0-9_-]*){2,}$`
- Règles:
  - segments séparés par `.`
  - min. 3 segments
  - lowercase uniquement
  - `_` et `-` autorisés après le 1er caractère d'un segment

Exemples valides:

- `action.data.csv.clean`
- `docs.system.logs.rotation_policy`
- `config.system.logs.default`

Exemples invalides:

- `Action.data.csv.clean` (majuscule)
- `action..csv.clean` (segment vide)
- `action.csv` (moins de 3 segments)
- `action/data/csv` (séparateur invalide)

### 1.2 Convention `tags`

- Tableau optionnel (par défaut: `[]`)
- Uniques (`uniqueItems=true`)
- Format: lowercase `kebab-case`
- Regex tag: `^[a-z0-9]+(?:-[a-z0-9]+)*$`

Valides: `csv`, `data-cleaning`, `etl-v2`

Invalides: `Data`, `data_cleaning`, `data cleaning`, `#ops`

### 1.3 Convention `content_ref`

- Chemin **relatif** à la racine du repo.
- Interdits:
  - chemins absolus (`/var/tmp/x`)
  - traversée (`../secrets.txt`)
  - URL (`https://...`)

Valides:

- `resources/scripts/clean_csv.sh`
- `resources/docs/log_rotation_policy.md`

Invalides:

- `/resources/scripts/clean_csv.sh`
- `../resources/scripts/clean_csv.sh`
- `https://example.com/script.sh`

### 1.4 Convention `related`

En v0, `related` est un tableau d'IDs de ressources:

```json
{
  "related": [
    "docs.data.csv.extract",
    "code.csv.extract_fields"
  ]
}
```

Règles v0:

- `related` présent dans la ressource (éventuellement `[]`)
- IDs uniques
- même regex que `id`
- ordre stable recommandé (alphabétique) pour des diffs lisibles

---

## 2) Endpoints MVP: requêtes/réponses normalisées

> Scope MVP: `/recall`, `/tree`, `/resource/{id}`, `/search`, `/related/{id}`, `/resolve/{id}`.

## 2.1 `GET /recall`

### Request

```http
GET /recall HTTP/1.1
Accept: application/json
```

### Response `200`

```json
{
  "total": 6,
  "by_type": {
    "action": 1,
    "code": 1,
    "doc": 2,
    "config": 1,
    "template": 0,
    "reference": 1
  },
  "by_category": {
    "data": 2,
    "system": 4
  }
}
```

## 2.2 `GET /tree?path={category[/theme]}`

### Request

```http
GET /tree?path=system/logs HTTP/1.1
Accept: application/json
```

### Response `200`

```json
{
  "path": "system/logs",
  "nodes": [
    {
      "id": "system.logs.rotate",
      "type": "action",
      "title": "Rotate logs"
    },
    {
      "id": "docs.system.logs.rotation_policy",
      "type": "doc",
      "title": "Log rotation policy"
    }
  ]
}
```

### Response `400`

```json
{
  "detail": "Invalid path format. Expected <category> or <category>/<theme>."
}
```

## 2.3 `GET /resource/{id}`

### Request

```http
GET /resource/action.data.csv.clean HTTP/1.1
Accept: application/json
```

### Response `200`

```json
{
  "id": "action.data.csv.clean",
  "type": "action",
  "title": "Clean CSV",
  "category": "data",
  "theme": "csv",
  "description": "Nettoie un CSV avec règles de base.",
  "content_ref": "resources/scripts/clean_csv.sh",
  "tags": ["csv", "data-cleaning"],
  "related": ["code.csv.extract_fields", "docs.data.csv.extract"]
}
```

### Response `404`

```json
{
  "detail": "Unknown resource id: action.data.csv.clean"
}
```

## 2.4 `GET /search?q={query}&limit={n}`

### Request

```http
GET /search?q=csv&limit=20 HTTP/1.1
Accept: application/json
```

### Response `200`

```json
{
  "query": "csv",
  "total": 2,
  "results": [
    {
      "id": "action.data.csv.clean",
      "type": "action",
      "title": "Clean CSV",
      "description": "Nettoie un CSV avec règles de base."
    },
    {
      "id": "code.csv.extract_fields",
      "type": "code",
      "title": "Extract CSV fields",
      "description": "Extrait des colonnes d'un CSV."
    }
  ]
}
```

## 2.5 `GET /related/{id}`

### Request

```http
GET /related/action.data.csv.clean HTTP/1.1
Accept: application/json
```

### Response `200`

```json
{
  "id": "action.data.csv.clean",
  "related": [
    "code.csv.extract_fields",
    "docs.data.csv.extract"
  ]
}
```

### Response `404`

```json
{
  "detail": "Unknown resource id: action.data.csv.clean"
}
```

## 2.6 `GET /resolve/{id}`

### Request

```http
GET /resolve/action.data.csv.clean HTTP/1.1
Accept: application/json
```

### Response `200`

```json
{
  "id": "action.data.csv.clean",
  "type": "action",
  "title": "Clean CSV",
  "category": "data",
  "theme": "csv",
  "description": "Nettoie un CSV avec règles de base.",
  "content_ref": "resources/scripts/clean_csv.sh",
  "related": ["code.csv.extract_fields", "docs.data.csv.extract"],
  "resolved": {
    "content": "#!/usr/bin/env bash\n...",
    "content_type": "text/plain",
    "size": 489
  }
}
```

### Response `500`

```json
{
  "detail": "content_ref does not exist for action.data.csv.clean: resources/scripts/clean_csv.sh"
}
```

---

## 3) Stratégie d'évolution `v0 -> v1`

### 3.1 Principes

1. **Compatibilité backward par défaut** sur les endpoints v0.
2. Les ajouts non-breaking se font d'abord en v0 (champs optionnels, nouveaux endpoints).
3. Toute rupture nécessite version explicite (`v1`) et fenêtre de coexistence.

### 3.2 Règles de rétrocompatibilité

Changements non-breaking (autorisés en v0 mineur):

- ajout de champs optionnels en réponse
- ajout de nouvelles valeurs `type` si clients doivent ignorer l'inconnu
- ajout d'endpoints hors MVP

Changements breaking (réservés à `v1`):

- renommer/supprimer un champ existant
- rendre obligatoire un champ auparavant optionnel
- modifier le type d'un champ (ex: `related: string[] -> object[]`)
- changer la sémantique d'une erreur (`404` vers `200` vide, etc.)

### 3.3 Plan de migration recommandé

1. **Annonce**: publication du contrat `resource.schema.v1.json` et `api.contract.v1.md`.
2. **Coexistence**: maintenir v0 et v1 en parallèle.
3. **Signal**: header de dépréciation (`Deprecation`, `Sunset`) côté v0.
4. **Outillage CI**:
   - validation JSON Schema v0/v1
   - tests de non-régression sur fixtures v0
5. **Retrait v0** après date de sunset communiquée.

---

## 4) Exemples valides/invalides pour CI & onboarding

## 4.1 Ressource valide (v0)

```json
{
  "id": "action.data.csv.clean",
  "type": "action",
  "title": "Clean CSV",
  "category": "data",
  "theme": "csv",
  "description": "Nettoie un CSV avec règles de base.",
  "content_ref": "resources/scripts/clean_csv.sh",
  "tags": ["csv", "data-cleaning"],
  "related": ["code.csv.extract_fields", "docs.data.csv.extract"]
}
```

## 4.2 Ressource invalide (ID + tags + content_ref)

```json
{
  "id": "Action.csv",
  "type": "action",
  "title": "x",
  "category": "Data",
  "theme": "csv",
  "description": "bad",
  "content_ref": "../secret.sh",
  "tags": ["Data_Cleaning", "data-cleaning"],
  "related": ["docs.data.csv.extract", "docs.data.csv.extract"]
}
```

Pourquoi invalide:

- `id` ne respecte pas `domain.topic.item`
- `title` trop court
- `category` non normalisée
- `content_ref` sort du repo
- `tags` contient un format invalide + doublon
- `related` contient des doublons

## 4.3 Cas d'erreur API attendu (onboarding QA)

- `GET /resource/unknown.item.x` -> `404`
- `GET /tree?path=system/logs/extra` -> `400`
- `GET /resolve/<id_avec_content_ref_cassé>` -> `500`

Ces cas doivent être couverts par tests d'intégration pour garantir un contrat stable.
