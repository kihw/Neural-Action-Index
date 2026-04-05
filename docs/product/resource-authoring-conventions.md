# Conventions d'ajout de ressources (YAML, tags et summary)

## 1) Convention YAML minimale

Tous les fichiers `resources/index/*.yml` doivent inclure:
- `id` (stable, lisible, versionnable)
- `type`
- `title`
- `category`
- `theme`
- `description` (summary)
- `content_ref` (chemin relatif vers le contenu réel)

Template recommandé: `resources/templates/resource.add.template.yaml`.

## 2) Convention d'ID

Format conseillé:

`<team>.<domain>.<topic>.<name>`

Exemples:
- `data.analytics.retention.cohort_definition`
- `security.incident.suspicious_login.playbook`

Règles:
- minuscules uniquement
- séparateur `.` pour les niveaux logiques
- `_` ou `-` toléré dans les segments si nécessaire

## 3) Convention de tags

Structure clé:valeur pour faciliter le filtrage:
- `domain:<domain>`
- `theme:<theme>`
- `intent:<how-to|runbook|reference|decision|template>`
- `audience:<eng|data|product|ops|all>`
- `maturity:<draft|mvp|stable|deprecated>`

Exemple:

```yaml
tags:
  - domain:data
  - theme:pipelines
  - intent:runbook
  - audience:data
  - maturity:stable
```

## 4) Convention de summary (`description`)

Format recommandé en 1 phrase:

`[Contexte] + [Action/artefact] + [Résultat attendu]`

Exemple:
- "En cas d'échec Airflow, ce runbook décrit le diagnostic initial pour rétablir le DAG en moins de 15 minutes."

Checklist qualité summary:
- explicite et actionnable
- <= 180 caractères idéalement
- sans jargon local non défini

## 5) Critères de validation avant merge

- `content_ref` existe réellement.
- les IDs `related` existent.
- tags couvrent domain/theme/intent.
- `updated_at` est à jour.
