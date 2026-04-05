# MVP v0 — Spécification produit (strict)

## 1) Endpoints stricts du MVP

Le MVP expose **uniquement** les 6 endpoints suivants :

1. `GET /recall`
2. `GET /tree`
3. `GET /resource/{id}`
4. `GET /search`
5. `GET /related/{id}`
6. `GET /resolve/{id}`

Tout endpoint hors de cette liste est **hors scope MVP** (ex. `/health`, endpoints d’admin, write API, bulk API).

### Hors scope explicite (MVP v0)

- Écriture/modification/suppression de ressources (`POST`, `PUT`, `PATCH`, `DELETE`).
- Ingestion temps réel et indexation distribuée.
- Gestion avancée des droits (RBAC/ABAC), multi-tenant.
- Pagination avancée (curseur, tri multi-colonnes, filtres combinés complexes).
- Faceting, boosting, reranking sophistiqué, personnalisation de ranking.
- API versioning public (`/v1`, header de version), dépréciation multi-version.
- SLA contractuel, quotas, billing, analytics produit avancées.

---

## 2) Schéma ressource MVP — champs obligatoires / optionnels

### Champs obligatoires

- `id` *(string, pattern type `a.b.c`)*
- `type` *(enum: `action`, `code`, `doc`, `config`, `template`, `reference`)*
- `title` *(string)*
- `category` *(string)*
- `theme` *(string)*
- `description` *(string)*
- `content_ref` *(string)*

### Champs optionnels

- `variables` *(array d’objets)*
  - sous-champs requis par item : `name`, `kind`
  - sous-champs optionnels : `required`, `default`, `description`
- `tags` *(array de strings)*
- `related` *(array de strings d’IDs)*
- `metadata` *(object)*
  - optionnels : `author`, `version`, `updated_at` *(format date)*

### Règle de structure

- `additionalProperties: false` : tout champ non spécifié ci-dessus est interdit dans le schéma MVP.

---

## 3) Règles de succès par endpoint

> Les latences cibles ci-dessous sont des objectifs P95 en environnement nominal MVP (index chargé en mémoire, charge modérée).

### `GET /recall`

- **Succès (200)**
  - Latence cible : **≤ 150 ms**.
  - JSON minimal :

```json
{
  "summary": {
    "total": 0,
    "by_type": {},
    "by_category": {}
  }
}
```

- **Erreurs de base**
  - `500` si erreur interne non récupérable.

### `GET /tree?path=...`

- **Succès (200)**
  - Latence cible : **≤ 200 ms**.
  - JSON minimal :

```json
{
  "path": "category/theme",
  "nodes": []
}
```

- **Erreurs de base**
  - `400` si `path` est invalide (vide, mal formé, inconnu selon règle d’entrée).
  - `500` si erreur interne.

### `GET /resource/{id}`

- **Succès (200)**
  - Latence cible : **≤ 120 ms**.
  - JSON minimal : **objet ressource conforme au schéma MVP** (section 2).

- **Erreurs de base**
  - `404` si `id` inexistant.
  - `400` si `id` mal formé.
  - `500` si erreur interne.

### `GET /search?q=...&limit=...`

- **Succès (200)**
  - Latence cible : **≤ 250 ms**.
  - JSON minimal :

```json
{
  "query": "...",
  "total": 0,
  "results": []
}
```

- **Erreurs de base**
  - `400` si `q` absent/vide ou `limit` hors bornes MVP.
  - `500` si erreur interne.

### `GET /related/{id}`

- **Succès (200)**
  - Latence cible : **≤ 180 ms**.
  - JSON minimal :

```json
{
  "id": "...",
  "related": []
}
```

- **Erreurs de base**
  - `404` si `id` inexistant.
  - `400` si `id` mal formé.
  - `500` si erreur interne.

### `GET /resolve/{id}`

- **Succès (200)**
  - Latence cible : **≤ 300 ms**.
  - JSON minimal :

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

- **Erreurs de base**
  - `404` si `id` inexistant.
  - `500` si `content_ref` cassé/inaccessible ou autre erreur interne.

---

## 4) Non spécifié (à ne pas implémenter implicitement)

Pour éviter les divergences d’implémentation, les points suivants sont explicitement **non spécifiés** en MVP v0 :

- **AuthN/AuthZ**
  - Aucun mécanisme obligatoire défini (API key, JWT, OAuth2, RBAC) dans cette phase.
- **Pagination fine**
  - Pas de curseur, pas de contrat page/size détaillé, pas de tri/filtres avancés standardisés.
- **Versioning API**
  - Pas de convention imposée (`/v1`, header `Accept`, semver endpoint).
- **Politiques recall/ranking**
  - Pas de politique normative figée sur pondérations, scoring, reranking, tie-breakers, personnalisation.

Tant qu’un point reste dans cette section, il ne peut pas être considéré comme “attendu par défaut”.

---

## 5) Checklist de validation fin de phase (Go/No-Go)

### Contrat API

- [ ] Les 6 endpoints stricts sont exposés et accessibles.
- [ ] Aucun endpoint hors scope MVP n’est requis pour le fonctionnement cœur.
- [ ] Les codes d’erreur de base (400/404/500 selon endpoint) sont couverts.

### Schéma de données

- [ ] Toute ressource retournée par `/resource/{id}` respecte le schéma MVP.
- [ ] Les champs obligatoires sont toujours présents.
- [ ] Aucun champ hors schéma (`additionalProperties`) n’est renvoyé.

### Comportement fonctionnel

- [ ] `/search` retourne une structure stable (`query`, `total`, `results`).
- [ ] `/related/{id}` retourne systématiquement une liste `related` (vide possible).
- [ ] `/resolve/{id}` retourne un bloc `resolved` exploitable ou un code erreur explicite.

### Performance cible (P95)

- [ ] `/recall` ≤ 150 ms
- [ ] `/tree` ≤ 200 ms
- [ ] `/resource/{id}` ≤ 120 ms
- [ ] `/search` ≤ 250 ms
- [ ] `/related/{id}` ≤ 180 ms
- [ ] `/resolve/{id}` ≤ 300 ms

### Gouvernance de scope

- [ ] Les sujets “non spécifiés” ne sont pas implémentés comme conventions implicites.
- [ ] Toute extension post-MVP est tracée dans une spec v0.x/v1 dédiée.

## Décision

- **GO** : toutes les cases critiques ci-dessus sont validées.
- **NO-GO** : au moins un bloc critique (contrat, schéma, erreurs de base) n’est pas conforme.
