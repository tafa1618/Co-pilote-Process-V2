"""Service pour la gestion de la productivité"""
import pandas as pd
from database import get_conn
from preprocessing.preprocessing_productivity import (
    load_raw_productivity_data,
    preprocess_productivity_df,
    preprocess_uploaded_productivity_file,
)
from kpi.kpi_productivity import (
    calculate_global_productivity,
    calculate_monthly_productivity,
    calculate_team_productivity,
    calculate_technician_productivity,
    calculate_team_monthly_productivity,
    calculate_correlation_driver,
    calculate_exhaustivity,
)

LATEST_PRODUCTIVITY_DF: pd.DataFrame | None = None


def load_from_db() -> pd.DataFrame | None:
    """Charge et preprocess les données de productivité depuis la base de données"""
    df_raw = load_raw_productivity_data()
    if df_raw is None:
        return None
    return preprocess_productivity_df(df_raw)


def process_uploaded_file(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un fichier uploadé"""
    return preprocess_uploaded_productivity_file(df)


def get_latest_df() -> pd.DataFrame | None:
    """Retourne le dernier DataFrame chargé en mémoire"""
    return LATEST_PRODUCTIVITY_DF


def set_latest_df(df: pd.DataFrame):
    """Définit le dernier DataFrame chargé"""
    global LATEST_PRODUCTIVITY_DF
    LATEST_PRODUCTIVITY_DF = df


def calculate_all_productivity_analytics(df: pd.DataFrame) -> dict:
    """Calcule tous les analytics de productivité à partir d'un DataFrame préprocessé"""
    return {
        "global": calculate_global_productivity(df),
        "monthly": calculate_monthly_productivity(df),
        "teams": calculate_team_productivity(df),
        "technicians": calculate_technician_productivity(df),
        "correlation": calculate_correlation_driver(df),
        # Note: exhaustivity nécessite equipe et mois_periode, donc pas inclus ici
        # Il sera calculé séparément dans l'endpoint dédié
    }

