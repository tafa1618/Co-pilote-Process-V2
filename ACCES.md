# 🚀 Guide d'Accès - Digital Twin SEP

## URLs Importantes

### ✅ DASHBOARD FRONTEND (À utiliser)
**URL**: http://localhost:5174

C'est ici que vous verrez l'interface avec:
- Le logo NEEMBA CAT
- Les 12 KPIs SEP
- Les graphiques et visualisations

---

### ⚙️ BACKEND API (Pour les développeurs)
**URL**: http://localhost:8000

Le backend ne sert que des données JSON, pas d'interface visuelle.

**Endpoints disponibles**:
- `http://localhost:8000/api/sep/kpis` - Tous les KPIs SEP
- `http://localhost:8000/api/sep/custom-kpis` - KPIs personnalisés  
- `http://localhost:8000/api/sep/insights` - Insights des agents

---

## 🔍 Test Rapide

### 1. Vérifier que le backend fonctionne
Ouvrez dans votre navigateur:
```
http://localhost:8000/api/sep/kpis
```
Vous devriez voir du JSON avec les données des KPIs.

### 2. Ouvrir le Dashboard
Ouvrez dans votre navigateur:
```
http://localhost:5174
```
Vous devriez voir le dashboard NEEMBA CAT.

---

## ❌ Erreur "Not Found"

Si vous voyez "Not Found" sur localhost:8000, c'est **NORMAL** !
Le backend n'a pas de page d'accueil HTML, uniquement des endpoints API.

**👉 Allez sur http://localhost:5174 pour voir le dashboard.**
