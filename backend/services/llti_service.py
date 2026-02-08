"""Service pour la gestion du KPI LLTI (Lead Time to Invoice)"""
from datetime import date
from typing import Any, Dict
import pandas as pd
from preprocessing.preprocessing_llti import (
    preprocess_uploaded_llti_file,
    preprocess_llti,
)
from database import get_conn
from kpi.kpi_llti import calculate_all_llti_analytics


LATEST_LLTI_DF: pd.DataFrame | None = None


def load_raw_llti_data() -> pd.DataFrame | None:
    """Charge les données brutes LLTI depuis la base de données"""
    try:
        with get_conn() as conn:
            df_db = pd.read_sql_query(
                """
                SELECT or_segment, numero_facture, date_facture, date_pointage,
                       client, sn_equipement, constructeur, llti_jours
                FROM llti_record
                ORDER BY date_facture DESC
                """,
                conn,
            )
        if df_db.empty:
            return None
        
        # Renommer pour correspondre aux colonnes attendues par le preprocessing
        df_db = df_db.rename(columns={
            "or_segment": "N° OR (Segment)",
            "numero_facture": "N° Facture (Lignes)",
            "date_facture": "Date Facture (Lignes)",
            "date_pointage": "Pointage dernière date (Segment)",
            "client": "Nom Client OR (or)",
            "sn_equipement": "Numéro série Equipement (Segment)",
            "constructeur": "Constructeur de l'équipement",
        })
        
        return df_db
    except Exception as exc:
        print(f"⚠️ Erreur chargement LLTI depuis DB: {exc}")
        return None


def load_from_db() -> pd.DataFrame | None:
    """Charge et preprocess les données LLTI depuis la base de données"""
    df_raw = load_raw_llti_data()
    if df_raw is None:
        return None
    # Les colonnes sont déjà renommées dans load_raw_llti_data pour correspondre au preprocessing
    # Le preprocessing filtre sur trimestre en cours, Caterpillar, etc.
    return preprocess_llti(df_raw)


def process_uploaded_file(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un fichier uploadé"""
    return preprocess_uploaded_llti_file(df)


def get_latest_df() -> pd.DataFrame | None:
    """Retourne le dernier DataFrame chargé en mémoire"""
    return LATEST_LLTI_DF


def set_latest_df(df: pd.DataFrame):
    """Définit le dernier DataFrame chargé"""
    global LATEST_LLTI_DF
    LATEST_LLTI_DF = df


def calculate_all_llti_analytics_from_db() -> Dict[str, Any]:
    """Calcule tous les analytics LLTI depuis la base de données"""
    df = load_from_db()
    if df is None or df.empty:
        return {
            "global": {
                "moyenne_llti": 0.0,
                "mediane_llti": 0.0,
                "total_factures": 0,
                "status": "N/A",
            },
            "by_client": [],
            "by_or": [],
            "distribution": {
                "excellent": 0,
                "advanced": 0,
                "emerging": 0,
                "a_ameliorer": 0,
            },
        }
    return calculate_all_llti_analytics(df)

