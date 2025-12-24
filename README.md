# SIGNARE KPI - Monorepo

## Structure
- `backend/` : FastAPI (CORS, middleware email @neemba.com, upload en mémoire via Pandas, rôle Admin = `ADMIN_EMAIL`).
- `frontend/` : React + Vite + Tailwind (mobile-first noir/or, icônes Lucide, login simulé + dashboard + zone d’upload visible uniquement pour l’admin).
- `docker-compose.yml` : backend, frontend et PostgreSQL.

## Lancer tout avec Docker
```bash
docker compose up --build
```

Variables utiles :
- `ADMIN_EMAIL` : email admin (RBAC, upload autorisé).
- `VITE_BACKEND_URL` : URL du backend côté frontend (par défaut `http://localhost:8000`).

## Rappels Sécurité
- No-Storage Policy : aucun fichier téléversé n’est écrit sur disque, traitement en mémoire (`io.BytesIO` + Pandas).
- Domaine restreint : seuls les emails `@neemba.com` sont acceptés.
- L’admin (variable d’environnement) est le seul à pouvoir uploader.