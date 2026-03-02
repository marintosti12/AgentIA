# Agent IA - Apprentissage des Ouvertures aux Echecs

POC (Proof of Concept) d'un agent IA pour la Federation Francaise des Echecs (FFE).

Cet agent intelligent accompagne les jeunes espoirs dans l'apprentissage des ouvertures aux echecs en proposant :

- Les meilleurs coups issus de la theorie des ouvertures
- Le contexte des ouvertures via des parties historiques
- Des videos explicatives pertinentes (YouTube)
- Une evaluation de la position par Stockfish lorsque la partie s'ecarte de la theorie

## Architecture

- **Backend** : FastAPI + LangGraph
- **Frontend** : Angular avec ngx-chessboard
- **Base vectorielle** : Milvus (recherche semantique sur les donnees Wikichess)
- **Base de donnees** : MongoDB
- **Moteur d'echecs** : Stockfish
- **APIs externes** : Lichess (ouvertures, parties), YouTube Data API

## Prerequis

- Docker et Docker Compose
- Git

## Demarrage rapide

```bash
# Cloner le depot
git clone <url-du-depot>
cd AgentIA

# Lancer les services
docker compose up --build
```

Le backend FastAPI sera accessible sur `http://localhost:8000`.

## Structure du projet

```
AgentIA/
├── backend/          # API FastAPI + Agent LangGraph
│   ├── app/
│   │   ├── main.py
│   │   └── api/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Application Angular
├── docker-compose.yml
├── .env
└── Readme.md
```

## Endpoints

- `GET /api/v1/healthcheck` - Verification du bon fonctionnement du service

## Variables d'environnement

Copiez `.env.example` en `.env` et configurez les variables selon votre environnement.
