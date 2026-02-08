# Configuration des Emails Autorisés (ALLOWED_ADMINS)

## 📍 Emplacements

La liste `ALLOWED_ADMINS` doit être définie à **3 endroits** pour que le contrôle d'accès fonctionne correctement :

### 1. Backend (`backend/main.py`)
**Ligne 73-77**

```python
# Liste des emails autorisés pour accéder à SuiviSepMeeting
ALLOWED_ADMINS = [
    (os.environ.get("ADMIN_EMAIL") or "").strip().lower(),
    # Exemple : ajouter d'autres emails autorisés ici
    # "manager@neemba.com",
    # "directeur@neemba.com",
    # "superviseur@neemba.com",
]
ALLOWED_ADMINS = [e for e in ALLOWED_ADMINS if e]  # Filtrer les valeurs vides
```

### 2. Frontend - App.tsx (`frontend/src/App.tsx`)
**Ligne 9-11**

```typescript
const ALLOWED_ADMINS = [
  (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase(),
  // Exemple : ajouter d'autres emails autorisés ici
  // "manager@neemba.com",
  // "directeur@neemba.com",
  // "superviseur@neemba.com",
].filter(Boolean);
```

### 3. Frontend - SuiviSepMeeting.tsx (`frontend/src/pages/SuiviSepMeeting.tsx`)
**Ligne 189-192**

```typescript
const ALLOWED_ADMINS = [
  DEFAULT_EMAIL,
  // Exemple : ajouter d'autres emails autorisés ici
  // "manager@neemba.com",
  // "directeur@neemba.com",
  // "superviseur@neemba.com",
].filter(Boolean);
```

---

## ✅ Comment ajouter un email autorisé

### Méthode 1 : Ajout direct dans le code (recommandé pour développement)

1. **Ouvrir les 3 fichiers** mentionnés ci-dessus
2. **Décommenter et modifier** les lignes d'exemple, ou ajouter directement :

**Backend (`backend/main.py`)** :
```python
ALLOWED_ADMINS = [
    (os.environ.get("ADMIN_EMAIL") or "").strip().lower(),
    "manager@neemba.com",        # ← Ajoutez ici
    "directeur@neemba.com",      # ← Ajoutez ici
]
```

**Frontend (`frontend/src/App.tsx`)** :
```typescript
const ALLOWED_ADMINS = [
  (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase(),
  "manager@neemba.com",        // ← Ajoutez ici
  "directeur@neemba.com",      // ← Ajoutez ici
].filter(Boolean);
```

**Frontend (`frontend/src/pages/SuiviSepMeeting.tsx`)** :
```typescript
const ALLOWED_ADMINS = [
  DEFAULT_EMAIL,
  "manager@neemba.com",        // ← Ajoutez ici
  "directeur@neemba.com",       // ← Ajoutez ici
].filter(Boolean);
```

3. **Reconstruire les services** :
```bash
docker compose up -d --build
```

### Méthode 2 : Via variables d'environnement (recommandé pour production)

Pour le backend, vous pouvez utiliser la variable d'environnement `ADMIN_EMAIL` qui est automatiquement ajoutée.

Pour ajouter plusieurs emails via variables d'environnement, vous devrez modifier le code pour parser une liste (ex: `ALLOWED_ADMINS_CSV="email1@neemba.com,email2@neemba.com"`).

---

## ⚠️ Important

1. **Les 3 listes doivent être identiques** pour que le contrôle d'accès fonctionne correctement
2. **Les emails doivent être en minuscules** (le code les convertit automatiquement)
3. **Les emails doivent se terminer par `@neemba.com`** (vérifié par le middleware d'authentification)
4. **Après modification, reconstruire les services** Docker pour appliquer les changements

---

## 🔍 Vérification

Pour vérifier si un email est autorisé :

1. **Backend** : Les endpoints `/api/lean-actions/*` vérifient `ALLOWED_ADMINS`
2. **Frontend** : La page `SuiviSepMeeting` affiche "Accès Restreint" si l'email n'est pas dans la liste
3. **Navigation** : Le bouton "Suivi SEP Meeting" n'apparaît que si l'utilisateur est autorisé

---

## 📝 Exemple complet

Si vous voulez autoriser 3 personnes :
- `admin@neemba.com` (déjà dans ADMIN_EMAIL)
- `manager@neemba.com`
- `directeur@neemba.com`

**Backend** :
```python
ALLOWED_ADMINS = [
    (os.environ.get("ADMIN_EMAIL") or "").strip().lower(),
    "manager@neemba.com",
    "directeur@neemba.com",
]
```

**Frontend (App.tsx et SuiviSepMeeting.tsx)** :
```typescript
const ALLOWED_ADMINS = [
  (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase(),
  "manager@neemba.com",
  "directeur@neemba.com",
].filter(Boolean);
```

