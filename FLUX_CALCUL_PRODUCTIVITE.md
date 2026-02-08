# FLUX COMPLET : Calcul de Productivité

## 1. STRUCTURE DE LA BASE DE DONNÉES

```sql
CREATE TABLE pointage (
    jour date NOT NULL,                    -- Date du pointage
    technicien text NOT NULL,              -- Nom du technicien
    equipe text,                           -- Nom de l'équipe
    facturable numeric NOT NULL,           -- Somme des heures facturables (déjà agrégée)
    heures_total numeric NOT NULL,         -- Somme des heures totales (déjà agrégée)
    inserted_at timestamp,                 -- Date d'insertion
    CONSTRAINT pointage_pk PRIMARY KEY (technicien, jour)  -- 1 ligne par technicien/jour
);
```

**IMPORTANT** : La DB stocke des données **DÉJÀ AGRÉGÉES** (1 ligne = 1 technicien + 1 jour).

---

## 2. UPLOAD D'UN FICHIER (Endpoint `/kpi/productivite/upload`)

### Étape 1 : Lecture du fichier
```python
df = pd.read_excel(buffer)  # ou pd.read_csv(buffer)
# Le fichier peut contenir PLUSIEURS lignes par technicien/jour
```

### Étape 2 : Préparation des données
```python
df_prepared = _prepare_productivity_df(df)
```

**Dans `_prepare_productivity_df`** :
- Parse les dates
- Convertit `Hr_Totale` → `heures_travaillees` (remplace NaN par 0)
- Convertit `Facturable` (remplace NaN par 0)
- Calcule `productivite` ligne par ligne : `Facturable / heures_travaillees` (⚠️ **NON UTILISÉ** dans les calculs finaux)

### Étape 3 : Agrégation AVANT sauvegarde en DB
```python
grouped = df_prepared.groupby([
    "Saisie heures - Date", 
    "Salarié - Nom", 
    "Salarié - Equipe(Nom)"
]).agg(
    facturable=("Facturable", "sum"),      # SOMME des facturables
    heures_total=("heures_travaillees", "sum")  # SOMME des heures
)
# Résultat : 1 ligne par technicien/jour
```

### Étape 4 : Sauvegarde en DB
```python
INSERT INTO pointage (jour, technicien, equipe, facturable, heures_total)
VALUES (date, technicien, equipe, SOMME_facturable, SOMME_heures)
ON CONFLICT (technicien, jour) DO UPDATE ...
```

**RÉSULTAT** : La DB contient des valeurs **DÉJÀ SOMMÉES** par technicien/jour.

---

## 3. CHARGEMENT DEPUIS LA DB (Fonction `_load_from_db`)

```python
SELECT jour, technicien, equipe, facturable, heures_total 
FROM pointage
```

**Puis** :
- `df_db["Hr_Totale"] = df_db["heures_total"]`  # Renomme la colonne
- `df_db["Facturable"] = df_db["facturable"]`  # Déjà numérique
- Appelle `_prepare_productivity_df(df_db)`

**Dans `_prepare_productivity_df`** :
- Les valeurs sont **DÉJÀ AGRÉGÉES** (1 ligne = 1 technicien/jour)
- Calcule `heures_travaillees` depuis `Hr_Totale` (qui vient de `heures_total`)
- Calcule `productivite` ligne par ligne (⚠️ **NON UTILISÉ**)

**RÉSULTAT** : DataFrame avec 1 ligne par technicien/jour, valeurs déjà sommées.

---

## 4. CALCUL DES KPIs (Endpoint `/kpi/productivite/analytics`)

### 4.1 Productivité Globale
```python
total_hours = df["heures_travaillees"].sum()      # SOMME de toutes les heures
total_fact = df["Facturable"].sum()                # SOMME de tout le facturable
global_prod = total_fact / total_hours             # ✅ CORRECT : sum/sum
```

### 4.2 Productivité Mensuelle
```python
monthly_agg = df.groupby(["month_num", "mois"]).agg(
    facturable=("Facturable", "sum"),              # SOMME par mois
    heures=("heures_travaillees", "sum")           # SOMME par mois
)
monthly_agg["productivite"] = (
    monthly_agg["facturable"] / monthly_agg["heures"]  # ✅ CORRECT : sum/sum
)
```

### 4.3 Productivité par Technicien
```python
tech_agg = df.groupby("Salarié - Nom").agg(
    facturable=("Facturable", "sum"),              # SOMME par technicien
    heures=("heures_travaillees", "sum")            # SOMME par technicien
)
tech_agg["productivite"] = (
    tech_agg["facturable"] / tech_agg["heures"]    # ✅ CORRECT : sum/sum
)
```

### 4.4 Productivité par Équipe
```python
team_agg = df.groupby("Salarié - Equipe(Nom)").agg(
    facturable=("Facturable", "sum"),              # SOMME par équipe
    heures=("heures_travaillees", "sum")            # SOMME par équipe
)
team_agg["productivite"] = (
    team_agg["facturable"] / team_agg["heures"]    # ✅ CORRECT : sum/sum
)
```

---

## ⚠️ PROBLÈMES POTENTIELS IDENTIFIÉS

### Problème 1 : Double agrégation ?
- **Upload** : Agrège par technicien/jour → sauvegarde en DB
- **Chargement** : Charge depuis DB (déjà agrégé) → fait des sum/sum
- **Résultat** : ✅ Correct car on somme des valeurs déjà agrégées par jour

### Problème 2 : Calcul ligne par ligne inutile
- `_prepare_productivity_df` calcule `productivite` ligne par ligne
- Cette colonne **N'EST PAS UTILISÉE** dans les calculs finaux (on fait sum/sum)
- ✅ Pas de problème, juste inutile

### Problème 3 : Vérification des données
- Si le fichier uploadé a des lignes avec `Hr_Totale = 0`, elles sont incluses dans l'agrégation
- Si `Facturable = 0` et `Hr_Totale = 0`, la ligne contribue à 0/0 = 0 (correct)
- Si `Facturable > 0` et `Hr_Totale = 0`, on obtient inf → remplacé par 0

---

## 🔍 POINTS À VÉRIFIER

1. **Les valeurs dans le fichier uploadé sont-elles correctes ?**
   - Vérifier que `Hr_Totale` et `Facturable` sont bien numériques
   - Vérifier qu'il n'y a pas de valeurs négatives

2. **L'agrégation lors de l'upload est-elle correcte ?**
   - Vérifier que toutes les lignes du même technicien/jour sont bien sommées

3. **Le chargement depuis la DB est-il correct ?**
   - Vérifier que `heures_total` de la DB correspond bien à `Hr_Totale` du fichier original

4. **Les calculs sum/sum sont-ils corrects ?**
   - Vérifier que les groupby fonctionnent correctement

---

## 📊 EXEMPLE CONCRET

### Fichier uploadé (3 lignes pour le même technicien le même jour) :
```
Date        | Technicien | Facturable | Hr_Totale
2024-01-15  | Jean       | 4.0        | 4.0
2024-01-15  | Jean       | 2.0        | 2.0
2024-01-15  | Jean       | 2.0        | 2.0
```

### Après agrégation (avant sauvegarde en DB) :
```
Date        | Technicien | Facturable | heures_total
2024-01-15  | Jean       | 8.0        | 8.0
```

### Enregistré en DB :
```sql
jour='2024-01-15', technicien='Jean', facturable=8.0, heures_total=8.0
```

### Chargé depuis DB :
```
Saisie heures - Date | Salarié - Nom | Facturable | Hr_Totale | heures_travaillees
2024-01-15           | Jean          | 8.0        | 8.0       | 8.0
```

### Calcul productivité :
```
Productivité = sum(Facturable) / sum(heures_travaillees)
             = 8.0 / 8.0
             = 1.0 (100%)
```

✅ **CORRECT** !

