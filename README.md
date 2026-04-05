# Neural Action Index (NAI) — Blueprint MVP

Ce dépôt contient un blueprint prêt à coder pour un moteur d'accès neuronal à un annuaire explicite de ressources techniques.

## Démarrage rapide

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn backend.api.app:app --reload
```

## Arborescence

- `resources/index/`: métadonnées des ressources (YAML).
- `resources/demo_vault/`: vault de démonstration (60 ressources multi-domaines) prêt pour ateliers et onboarding.
- `resources/templates/resource.add.template.yaml`: template standard pour créer une nouvelle ressource.
- `docs/product/resource-authoring-conventions.md`: conventions YAML, tags et summary.
- `docs/product/vscode-extension-mvp.md`: définition du MVP extension VS Code (`search/open/insert`).
- `docs/onboarding/team-onboarding-30min.md`: script d'onboarding équipe (30 minutes).
- `docs/metrics/adoption-metrics.md` + `tools/metrics/compute_adoption_metrics.py`: mesure WAU/MAU, temps de retrieval et usage `resolve`.
- `resources/scripts|code|docs|configs|templates/`: contenu réel référencé par `content_ref`.
- `backend/core/schema/`: modèles de données.
- `backend/core/indexer/`: chargement, validation, catalogage.
- `backend/core/resolver/`: résolution de contenu.
- `backend/api/`: endpoints FastAPI (`recall/tree/get/search/related/resolve`).
- `docs/contracts/`: contrats JSON (schéma ressource + contrat API).

## Endpoints MVP

- `GET /recall`
- `GET /tree?path=<category[/theme]>`
- `GET /resource/{id}`
- `GET /search?q=<query>&limit=20`
- `GET /related/{id}`
- `GET /resolve/{id}`

## Prochaine étape recommandée

1. Remplacer le moteur de recherche substring par un moteur hybride lexical + embeddings.
2. Ajouter une persistance SQLite/PostgreSQL pour caches et statistiques.
3. Ajouter des tests d'intégrité (`related`, `content_ref`) en CI.
