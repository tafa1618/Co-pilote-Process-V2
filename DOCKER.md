# SEP Digital Twin - Docker Setup

## Démarrage rapide

```bash
# Lancer tous les services
docker-compose up --build

# En arrière-plan
docker-compose up -d --build

# Arrêter les services
docker-compose down
```

## Services

- **Backend**: http://localhost:8000
  - API SEP KPIs: `/api/sep/kpis`
  - API Custom KPIs: `/api/sep/custom-kpis`
  - API Insights: `/api/sep/insights`

- **Frontend**: http://localhost:5173
  - Dashboard SEP avec branding Neemba

## Logs

```bash
# Voir les logs
docker-compose logs -f

# Logs backend uniquement
docker-compose logs -f backend

# Logs frontend uniquement
docker-compose logs -f frontend
```

## Rebuild

```bash
# Rebuild backend après modifications
docker-compose up --build backend

# Rebuild tout
docker-compose up --build
```
