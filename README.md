# Neemba Copilote - Monorepo

## Structure
- `backend/` : FastAPI (CORS, middleware email @neemba.com, upload en mémoire via Pandas, rôle Admin = `ADMIN_EMAIL` + mot de passe `ADMIN_PASSWORD` pour l’upload).
- `frontend/` : React + Vite + Tailwind (mobile-first noir/jaune #FFD700, icônes Lucide, login simulé + dashboard + zone d’upload visible uniquement pour l’admin).
- `docker-compose.yml` : backend, frontend et PostgreSQL.

## Lancer tout avec Docker
```bash
docker compose up --build
```

Variables utiles :
- `ADMIN_EMAIL` : email admin (RBAC, upload autorisé).
- `ADMIN_PASSWORD` : mot de passe admin exigé sur l’endpoint `/upload` via header `X-Admin-Password`.
- `VITE_BACKEND_URL` : URL du backend côté frontend (par défaut `http://localhost:8000`).
- `VITE_ADMIN_EMAIL` : email admin attendu côté frontend.
- `VITE_ADMIN_PASSWORD` : mot de passe admin à saisir côté frontend (propagé dans `X-Admin-Password`).

## Rappels Sécurité
- No-Storage Policy : aucun fichier téléversé n’est écrit sur disque, traitement en mémoire (`io.BytesIO` + Pandas).
- Domaine restreint : seuls les emails `@neemba.com` sont acceptés.
- L’admin (variable d’environnement) est le seul à pouvoir uploader.