# Démarrage Rapide - Backend SEP

## Option 1: Docker (Recommandé)

```bash
# Démarrer uniquement le backend
docker-compose up backend --build

# Ou en arrière-plan
docker-compose up -d backend --build
```

## Option 2: Python Direct (Sans Docker)

```bash
# Installer Flask
pip install flask flask-cors

# Démarrer le serveur
python backend/sep_server.py
```

## Option 3: Avec l'environnement virtuel existant

```bash
# Activer l'environnement
backend\.venv\Scripts\activate

# Installer Flask
pip install flask flask-cors

# Démarrer le serveur
python backend/sep_server.py
```

## Vérification

Une fois démarré, vous devriez voir:
```
🚀 SEP Mock Server starting on http://localhost:8000
📊 Endpoints:
   - GET /api/sep/kpis
   - GET /api/sep/custom-kpis
   - GET /api/sep/insights
```

Testez avec: http://localhost:8000/api/sep/kpis

## Frontend

Le frontend est déjà sur http://localhost:5174 (ou 5173)
