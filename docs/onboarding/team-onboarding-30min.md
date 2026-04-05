# Script d'onboarding équipe (30 minutes)

## Objectif session
Rendre chaque participant autonome sur: retrouver, ouvrir et réutiliser un artefact via NAI.

## Pré-requis (avant session)
- API NAI lancée localement.
- VS Code + extension NAI MVP installée.
- accès au demo vault.

## Déroulé minuté

### 0:00–0:05 — Contexte
- Problème: perte de temps à retrouver docs/scripts/standards.
- Promesse NAI: "retrouver en secondes, réutiliser en contexte".

### 0:05–0:12 — Démo guidée
Cas réel: incident "rotation logs saturée".
1. Search `rotation logs`.
2. Open `docs.system.logs.rotation_policy`.
3. Open `system.logs.rotate`.
4. Insert d'un snippet dans un runbook incident.

### 0:12–0:20 — Exercice en binôme
Mission:
- retrouver une ressource analytics (cohorts)
- retrouver un template interview produit
- insérer un artefact dans une note de travail

Critère de succès: 3 artefacts retrouvés en < 6 minutes.

### 0:20–0:26 — Ajout d'une nouvelle ressource
- créer un YAML à partir de `resources/templates/resource.add.template.yaml`
- appliquer conventions tags/summary
- vérifier `content_ref` + `related`

### 0:26–0:30 — Debrief + adoption
- points de friction
- 1 engagement d'usage par personne (au moins 3 recherches/jour la première semaine)

## Cas d'usage réel recommandé (runbook incident)

Scénario: erreur de parsing CSV en production.
- Search: `csv extract`
- Open: `docs.data.csv.extract`
- Open: `code.csv.extract_fields`
- Insert: snippet parsing robuste + note d'usage

Résultat attendu:
- réduction du temps de diagnostic
- standardisation de la réponse incident
