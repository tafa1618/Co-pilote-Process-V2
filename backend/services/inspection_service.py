"""Service pour la gestion de l'inspection rate"""
from datetime import date
from typing import Any, Dict
import pandas as pd
from preprocessing.preprocessing_inspection import (
    load_raw_inspection_data,
    preprocess_inspection_df,
    preprocess_uploaded_inspection_file,
)
from kpi.kpi_inspection import calculate_full_inspection_analytics


def load_inspection_from_db(start_date: date | None = None, end_date: date | None = None, team: str | None = None) -> pd.DataFrame | None:
    """Charge et preprocess les données d'inspection depuis la base de données"""
    df_raw = load_raw_inspection_data(start_date, end_date, team)
    if df_raw is None:
        return None
    return preprocess_inspection_df(df_raw)


def process_uploaded_file(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un fichier uploadé"""
    return preprocess_uploaded_inspection_file(df)


def calculate_inspection_analytics(start_date: date, end_date: date, last_wednesday: date | None = None, team: str | None = None) -> Dict[str, Any]:
    """Fonction utilitaire pour calculer les analytics d'inspection (utilisée par tous les composants)
    
    Logique de calcul :
    - Taux d'inspection = (Nombre d'OR uniques avec Is Inspected = "Inspecté") / (Nombre Total d'OR uniques facturés) * 100
    - C'est un KPI trimestriel basé sur les OR, pas sur les lignes individuelles
    """
    # Charger et preprocess les données depuis la base
    df = load_inspection_from_db(start_date, end_date, team)
    
    if df is None or df.empty:
        return {
            "total": 0,
            "inspected": 0,
            "not_inspected": 0,
            "inspection_rate": 0.0,
            "delta_weekly": 0.0,
            "inspection_rate_last_wednesday": 0.0,
            "by_atelier": [],
            "by_type_materiel": [],
            "by_technicien": [],
            "records": [],
        }
    
    # Charger les données du mercredi dernier si nécessaire
    df_last = None
    if last_wednesday:
        df_last = load_inspection_from_db(start_date, last_wednesday, team)
    
    # Utiliser le module kpi pour calculer tous les analytics
    return calculate_full_inspection_analytics(df, df_last)

