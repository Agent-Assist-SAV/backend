# Agent Assist SAV — WhatsApp & co (backend)

Assistant de réponse pour équipes SAV, intégré aux messageries (WhatsApp en premier). Il suggère des réponses courtes et contextualisées, appuyées par vos documents (RAG avec citations) et peut déclencher des actions simples (statut commande, RMA, RDV), tout en respectant les règles WhatsApp (fenêtre 24h, templates).

## Pour qui
- SAV/Support de marques e‑commerce, retail, services.
- Plateformes relation client souhaitant un “copilot” prêt à intégrer.

## Ce que le produit apporte
- Gain de temps: autocomplétion inline (Tab accepter, Esc ignorer), 2–3 variantes.
- Fiabilité: réponses fondées sur des sources internes, citations cliquables, mode “silence” si confiance basse.
- Efficacité: détection d’intentions, résumés de fil, multilingue.
- Conformité WhatsApp: gestion automatique des templates hors 24h, messages interactifs.

## Composants produit
- Interface opérateur: zone de saisie avec “ghost text”, panneau Sources, snippets “/retour, /suivi…”, contexte client.
- Moteur d’assistance: recherche hybride (RAG), génération de suggestions, gestion templates, connecteurs SAV (status, RMA, RDV).

## Fonctionnement (en bref)
1) Analyse du message (langue, intention, contexte).
2) Recherche d’extraits pertinents dans vos docs.
3) Génération de 2–3 réponses courtes avec citations.
4) Acceptation par l’agent → options (template, boutons, lien suivi).
5) Journalisation anonymisée pour améliorer la qualité.

## Tech stack (backend)

Cette application backend est une API REST/streaming écrite en Python pour piloter le moteur d'assistance SAV.

- Langage
	- Python 3.11+ (compatible 3.10/3.11) — runtime principal
- Framework web
	- FastAPI — routes, validation, SSE/WS et documentation OpenAPI auto-générée
- Infrastructure & conteneurisation
	- Docker — conteneurisation
	- Helm — déploiement Kubernetes
- IA & intégrations
	- Provider OVH/Mistral (implementation dans `src/ai/providers/ovh.py`) — usage d'une API compatible OpenAI en streaming

## Scripts d'exécution et déploiement
Le dossier `scripts` contient des scripts pour exécuter, build et déployer l'application.

**La première étape est de configurer les variables d'environnement nécessaires** en créant un fichier `.env` à partir du modèle `.env.template`. Pour cela, utilisez le script `set-env.sh` qui vous guidera dans la création du fichier `.env`:
```bash
./scripts/set-env.sh
```

### Exécution
Il est possible de lancer l'application en local (avec FastAPI) ou en conteneur Docker. Lancer l'application en local:
```bash
./scripts/run-python.sh
```
Ou lancer avec Docker:
```bash
./scripts/run-docker.sh
```
### Build l'image Docker
Pour construire l'image Docker de l'application, utilisez le script `build.sh`:
```bash
./scripts/build.sh [tag]
```

Où `[tag]` est optionnel (par défaut `latest`). Optionnellement, le script propose de pousser l'image vers Docker Hub après la construction.

### Déploiement avec Helm
Un chart Helm est inclus dans `helm/backend-chart` pour déployer l'application sur un cluster Kubernetes. Pour déployer ou mettre à jour l'application, utilisez le script `deploy.sh`:

```bash
./scripts/deploy.sh
```

Soyez sûr d'avoir un cluster Kubernetes accessible et `kubectl` configuré.