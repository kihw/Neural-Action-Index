# MVP extension VS Code NAI (Search / Open / Insert)

## Objectif
Permettre à une équipe de retrouver et réutiliser rapidement des artefacts NAI sans quitter VS Code.

## Périmètre MVP

### 1. Search
- Commande: `NAI: Search Resources`
- UI: QuickPick avec requête texte
- Source: `GET /search?q=<query>&limit=20`
- Affichage résultat:
  - `title`
  - `id`
  - `category/theme`
  - score (optionnel)

### 2. Open
- Depuis Search, action `Open Resource`
- Source: `GET /resource/{id}` puis `GET /resolve/{id}`
- Comportement:
  - ouvre `content_ref` si fichier local
  - fallback: virtual document VS Code avec contenu résolu

### 3. Insert
- Depuis Search, action `Insert Resource Snippet`
- Source: `GET /resolve/{id}`
- Comportement:
  - insère le texte à la position du curseur
  - entête standard ajouté (option config):
    - `<!-- inserted-from: <id> -->`

## Architecture technique

- `extension.ts`
  - register commands
  - orchestration quickpick/actions
- `naiClient.ts`
  - wrapper API HTTP (search/resource/resolve)
- `insertService.ts`
  - logique d'insertion et transformations simples
- `settings`
  - `nai.baseUrl` (default `http://localhost:8000`)
  - `nai.insert.includeHeader` (bool)

## Critères d'acceptation MVP

- Search retourne des résultats en < 700 ms sur index local.
- Open fonctionne pour au moins 95% des ressources avec `content_ref` valide.
- Insert ajoute le contenu résolu sans casser le document courant.
- Logs d'usage émis sur chaque commande (`search`, `open`, `insert`).

## Roadmap post-MVP
- filtre par tags/category/theme
- preview markdown enrichie
- cache local + offline mode
- auth SSO / token user
