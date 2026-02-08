"""Preprocessing des données LLTI (Lead Time to Invoice)"""
import pandas as pd
from datetime import datetime
from fastapi import HTTPException


# Constantes de colonnes
COL_OR_SEGMENT = "N° OR (Segment)"
COL_NUM_FACTURE = "N° Facture (Lignes)"
COL_DATE_FACTURE = "Date Facture (Lignes)"
COL_POINTAGE_DERNIERE_DATE = "Pointage dernière date (Segment)"
COL_NOM_CLIENT = "Nom Client OR (or)"
COL_NUM_SERIE = "Numéro série Equipement (Segment)"
COL_CONSTRUCTEUR = "Constructeur de l'équipement"

# Colonnes standardisées après preprocessing
STANDARDIZED_LLTI_JOURS = "LLTI_jours"


def preprocess_uploaded_llti_file(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess un DataFrame LLTI brut (depuis un fichier uploadé)
    Prépare le dataset LLTI (Lead Time Facturation Service)
    - Trimestre en cours
    - Facture par facture
    - Matériels Caterpillar uniquement
    - Dossiers avec pointage
    
    Args:
        df: DataFrame brut tel que lu depuis le fichier Excel/CSV
    Returns:
        DataFrame préprocessé avec LLTI_jours calculé
    """
    df = df.copy()

    # ==================================================
    # COLONNES NÉCESSAIRES
    # ==================================================
    required_cols = [
        COL_OR_SEGMENT,
        COL_NUM_FACTURE,
        COL_DATE_FACTURE,
        COL_POINTAGE_DERNIERE_DATE,
        COL_NOM_CLIENT,
        COL_NUM_SERIE,
        COL_CONSTRUCTEUR,
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes dans le fichier LLTI: {missing}",
        )

    df = df[required_cols].copy()

    # ==================================================
    # TYPAGE DATES
    # ==================================================
    df[COL_DATE_FACTURE] = pd.to_datetime(
        df[COL_DATE_FACTURE], errors="coerce"
    )
    df[COL_POINTAGE_DERNIERE_DATE] = pd.to_datetime(
        df[COL_POINTAGE_DERNIERE_DATE], errors="coerce"
    )

    # ==================================================
    # FILTRE : MATÉRIELS CATERPILLAR UNIQUEMENT
    # ==================================================
    df = df[
        df[COL_CONSTRUCTEUR]
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("CATERPILLAR")
    ]

    # ==================================================
    # FILTRE : FACTURES AVEC POINTAGE
    # ==================================================
    df = df[
        df[COL_POINTAGE_DERNIERE_DATE].notna()
        & df[COL_DATE_FACTURE].notna()
    ]

    # ==================================================
    # FILTRE : TRIMESTRE EN COURS
    # ==================================================
    today = pd.Timestamp.today().normalize()
    trimestre_debut = today.to_period("Q").start_time

    df = df[df[COL_DATE_FACTURE] >= trimestre_debut]

    # ==================================================
    # DÉDUPLICATION FACTURE PAR FACTURE
    # ==================================================
    df = (
        df.sort_values(COL_POINTAGE_DERNIERE_DATE)
        .drop_duplicates(subset=[COL_NUM_FACTURE], keep="last")
    )

    # ==================================================
    # CALCUL LLTI (jours)
    # ==================================================
    df[STANDARDIZED_LLTI_JOURS] = (
        df[COL_DATE_FACTURE] - df[COL_POINTAGE_DERNIERE_DATE]
    ).dt.days

    # ==================================================
    # NETTOYAGE FINAL
    # ==================================================
    df = df[df[STANDARDIZED_LLTI_JOURS] >= 0]

    return df.reset_index(drop=True)


def preprocess_llti(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess un DataFrame LLTI brut (depuis la base de données)
    Même logique que preprocess_uploaded_llti_file mais pour les données déjà en DB
    
    Args:
        df: DataFrame brut avec les colonnes renommées depuis la DB
    Returns:
        DataFrame préprocessé avec LLTI_jours calculé
    """
    df = df.copy()

    # Les colonnes sont déjà renommées dans load_raw_llti_data()
    # On applique les mêmes filtres et calculs
    
    # ==================================================
    # TYPAGE DATES
    # ==================================================
    df[COL_DATE_FACTURE] = pd.to_datetime(
        df[COL_DATE_FACTURE], errors="coerce"
    )
    df[COL_POINTAGE_DERNIERE_DATE] = pd.to_datetime(
        df[COL_POINTAGE_DERNIERE_DATE], errors="coerce"
    )

    # ==================================================
    # FILTRE : MATÉRIELS CATERPILLAR UNIQUEMENT
    # ==================================================
    df = df[
        df[COL_CONSTRUCTEUR]
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("CATERPILLAR")
    ]

    # ==================================================
    # FILTRE : FACTURES AVEC POINTAGE
    # ==================================================
    df = df[
        df[COL_POINTAGE_DERNIERE_DATE].notna()
        & df[COL_DATE_FACTURE].notna()
    ]

    # ==================================================
    # FILTRE : TRIMESTRE EN COURS
    # ==================================================
    today = pd.Timestamp.today().normalize()
    trimestre_debut = today.to_period("Q").start_time

    df = df[df[COL_DATE_FACTURE] >= trimestre_debut]

    # ==================================================
    # DÉDUPLICATION FACTURE PAR FACTURE
    # ==================================================
    df = (
        df.sort_values(COL_POINTAGE_DERNIERE_DATE)
        .drop_duplicates(subset=[COL_NUM_FACTURE], keep="last")
    )

    # Si LLTI_jours n'existe pas encore, le calculer
    if STANDARDIZED_LLTI_JOURS not in df.columns:
        # ==================================================
        # CALCUL LLTI (jours)
        # ==================================================
        df[STANDARDIZED_LLTI_JOURS] = (
            df[COL_DATE_FACTURE] - df[COL_POINTAGE_DERNIERE_DATE]
        ).dt.days
    
    # ==================================================
    # NETTOYAGE FINAL
    # ==================================================
    df = df[df[STANDARDIZED_LLTI_JOURS] >= 0]

    return df.reset_index(drop=True)
