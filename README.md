# 🚜 Neemba Copilote - Dashboard SEP & Manager Digital Twin

Plateforme d'analyse de performance et d'aide à la décision pour les opérations Neemba CAT. Ce projet combine le suivi des KPIs de productivité, un simulateur de performance (Digital Twin) et un outil de gestion des réunions SEP.

## 🌟 Fonctionnalités Clés

### 1. Dashboard de Productivité
- **Analyse de Performance** : Suivi de la productivité (Rolling 12 mois) par équipe et par salarié.
- **Contrôle d'Exhaustivité** : Système de codes couleur (VERT, ORANGE, ROUGE, BLEU) pour vérifier la saisie complète des heures.
- **Visualisations** : Graphiques d'évolution et matrices de corrélation pour identifier les drivers de performance.

### 2. Manager Digital Twin
- **Simulateur SEP 2025** : Évaluez l'impact de vos KPIs sur votre score global (Foundation vs Growth).
- **Règles métier** : Calcul automatique des niveaux (Bronze/Silver/Gold) et détection des downgrades.
- **Chat AI** : Interaction avec un agent IA pour obtenir des recommandations basées sur les données.

### 3. Meeting SEP (Réunions du Mercredi)
- **Snapshot Automatique** : Vue consolidée des performances hebdomadaires vs N-1.
- **Gestion des Actions Lean** : Création et suivi des actions directement pendant la réunion.
- **Génération de Comptes Rendus** : Export en Markdown prêt à être envoyé par email.

---

## 🏗️ Structure du Projet

- `backend/` : FastAPI, Psycopg 3, Pandas (traitement des données).
- `frontend/` : React + Vite + Tailwind CSS (Branding Neemba CAT).
- `Data/` : Contient les fichiers Excel de productivité (`productivite.xlsx`).

---

## 🛠️ Installation et Démarrage

### Pré-requis
- Python 3.11+
- Node.js & npm
- Docker (pour la base de données)

### 1. Base de Données (Docker)
Pour éviter les conflits locaux, nous utilisons PostgreSQL via Docker sur le port **5433**.
```bash
docker run --name postgres-kpi-5433 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=kpi_db -p 5433:5432 -d postgres:15
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
*Note : Le backend charge automatiquement les données de `Data/productivite.xlsx` au démarrage.*

### 3. Frontend
```bash
cd frontend
npm install
npm run dev -- --port 5174
```

---

## ⚙️ Configuration (.env)

Créez un fichier `.env` dans le dossier `backend/` (voir `.env.example`) :
- `DATABASE_URL` : `postgresql://postgres:postgres@localhost:5433/kpi_db`
- `ADMIN_EMAIL` : Votre email @neemba.com
- `ENV` : `dev`

---

## 🛡️ Sécurité & Accès
- **Domaine Restreint** : Accès limité aux adresses `@neemba.com`.
- **Rôles Admin** : Les fonctions d'upload et de configuration des agents sont réservées aux admins déclarés en variables d'environnement.
- **No-Storage Policy** : Les fichiers uploadés pour analyse ponctuelle sont traités en mémoire sans stockage permanent sur disque.

---

*© 2025 Neemba Group - Advanced Agentic Coding Project*
