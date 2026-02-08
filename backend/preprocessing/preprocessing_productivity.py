"""Preprocessing des données de productivité"""
import pandas as pd
from fastapi import HTTPException
from database import get_conn

# Constantes de colonnes (alignées avec le code Streamlit fourni)
COL_TECHNICIEN = "Salarié - Nom"
COL_EQUIPE = "Salarié - Equipe(Nom)"
COL_FACTURABLE = "Facturable"
COL_HEURES_TOTALE = "Hr_travaillée"  # Nom de la colonne brute dans le fichier Excel
COL_DATE = "Saisie heures - Date"

# Noms de colonnes standardisés après preprocessing
STANDARDIZED_HEURES = "Heures_travaillées"
STANDARDIZED_FACTURABLE = "Heures_facturables"
STANDARDIZED_MOIS = "Mois"
STANDARDIZED_MOIS_PERIODE = "Mois_periode"
STANDARDIZED_JOUR = "Jour"
STANDARDIZED_JOUR_SEMAINE = "Jour_semaine"


def load_raw_productivity_data() -> pd.DataFrame | None:
    """Charge les données brutes de productivité depuis la base de données"""
    try:
        with get_conn() as conn:
            df_db = pd.read_sql_query(
                "SELECT jour, technicien, equipe, facturable, heures_total FROM pointage",
                conn,
            )
        if df_db.empty:
            return None
        
        # Renommer les colonnes de la DB pour correspondre aux constantes
        df_db = df_db.rename(columns={
            "jour": COL_DATE,
            "technicien": COL_TECHNICIEN,
            "equipe": COL_EQUIPE,
            "facturable": COL_FACTURABLE,
            "heures_total": COL_HEURES_TOTALE,
        })
        
        return df_db
    except Exception as exc:
        print(f"⚠️ Erreur chargement productivité depuis DB: {exc}")
        return None


def preprocess_productivity_df(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un DataFrame de productivité brut (depuis la DB)
    Args:
        df: DataFrame brut avec les colonnes de la DB (jour, technicien, equipe, facturable, heures_total)
    Returns:
        DataFrame préprocessé avec les colonnes standardisées
    """
    if df.empty:
        return df

    df = df.copy()

    # Assurer les types corrects
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")
    df[COL_HEURES_TOTALE] = pd.to_numeric(df[COL_HEURES_TOTALE], errors="coerce")
    df[COL_FACTURABLE] = pd.to_numeric(df[COL_FACTURABLE], errors="coerce").fillna(0)

    # Supprimer les lignes avec des dates ou heures totales invalides
    df = df.dropna(subset=[COL_DATE, COL_HEURES_TOTALE])

    # Créer les colonnes standardisées
    df[STANDARDIZED_HEURES] = df[COL_HEURES_TOTALE]
    df[STANDARDIZED_FACTURABLE] = df[COL_FACTURABLE]
    df[STANDARDIZED_MOIS] = df[COL_DATE].dt.to_period("M").astype(str)  # Ex: "2023-01"
    df[STANDARDIZED_MOIS_PERIODE] = df[COL_DATE].dt.to_period("M")  # Ex: 2023-01
    df[STANDARDIZED_JOUR] = df[COL_DATE].dt.day
    df[STANDARDIZED_JOUR_SEMAINE] = df[COL_DATE].dt.weekday  # 0=lundi, 6=dimanche

    # Calculer la productivité par ligne (peut être utile pour des agrégations ultérieures)
    df["productivite_ligne"] = (
        df[STANDARDIZED_FACTURABLE] / df[STANDARDIZED_HEURES]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    return df


def preprocess_uploaded_productivity_file(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un DataFrame de productivité brut (depuis un fichier uploadé)
    Args:
        df: DataFrame brut tel que lu depuis le fichier Excel/CSV
    Returns:
        DataFrame préprocessé avec les colonnes standardisées
    """
    if df.empty:
        return df

    df = df.copy()

    # Vérifier les colonnes requises pour l'upload
    required_cols = {COL_DATE, COL_TECHNICIEN, COL_EQUIPE, COL_FACTURABLE, COL_HEURES_TOTALE}
    if not required_cols.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes dans le fichier de productivité: {required_cols - set(df.columns)}",
        )

    # Assurer les types corrects
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")
    df[COL_HEURES_TOTALE] = pd.to_numeric(df[COL_HEURES_TOTALE], errors="coerce")
    df[COL_FACTURABLE] = pd.to_numeric(df[COL_FACTURABLE], errors="coerce").fillna(0)

    # Supprimer les lignes avec des dates ou heures totales invalides
    df = df.dropna(subset=[COL_DATE, COL_HEURES_TOTALE])

    # Créer les colonnes standardisées
    df[STANDARDIZED_HEURES] = df[COL_HEURES_TOTALE]
    df[STANDARDIZED_FACTURABLE] = df[COL_FACTURABLE]
    df[STANDARDIZED_MOIS] = df[COL_DATE].dt.to_period("M").astype(str)
    df[STANDARDIZED_MOIS_PERIODE] = df[COL_DATE].dt.to_period("M")
    df[STANDARDIZED_JOUR] = df[COL_DATE].dt.day
    df[STANDARDIZED_JOUR_SEMAINE] = df[COL_DATE].dt.weekday

    df["productivite_ligne"] = (
        df[STANDARDIZED_FACTURABLE] / df[STANDARDIZED_HEURES]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    return df
