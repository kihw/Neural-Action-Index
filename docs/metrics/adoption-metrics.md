# Mesure d'adoption interne NAI

## KPIs demandés

1. **WAU/MAU interne**
   - WAU = utilisateurs actifs uniques sur 7 jours.
   - MAU = utilisateurs actifs uniques sur 30 jours.
   - Ratio d'engagement = WAU / MAU.

2. **Temps moyen pour retrouver un artefact**
   - Mesure: delta entre `search_submitted` et `resource_opened|resource_inserted` pour un même utilisateur/session.
   - Unité: secondes.

3. **Taux d'usage `resolve`**
   - Formule: `resolve_calls / search_calls` (ou `/active_users`, selon lecture produit).

## Événements à journaliser

Schéma minimal:
- `ts` (ISO 8601)
- `user_id`
- `session_id`
- `event_name` (`search_submitted`, `resource_opened`, `resource_inserted`, `resolve_called`)
- `resource_id` (optionnel)
- `query` (optionnel)

## Implémentation recommandée

- Émettre les événements depuis:
  - API (`/search`, `/resolve`, `/resource/{id}`)
  - extension VS Code (commandes `search/open/insert`)
- Stockage MVP:
  - fichier JSONL quotidien (`analytics/events-YYYY-MM-DD.jsonl`)
- Agrégation:
  - script `tools/metrics/compute_adoption_metrics.py`

## Cadence de lecture
- snapshot quotidien auto
- revue hebdo en équipe produit/platform
