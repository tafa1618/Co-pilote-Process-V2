"""Utilitaires pour les calculs de trimestres"""
from datetime import date
import pandas as pd


def get_current_quarter_dates() -> tuple[date, date]:
    """Retourne la date de début et de fin du trimestre actuel."""
    today = date.today()
    year = today.year
    month = today.month
    
    # Déterminer le trimestre
    if month in [1, 2, 3]:
        start_month = 1
        end_month = 3
    elif month in [4, 5, 6]:
        start_month = 4
        end_month = 6
    elif month in [7, 8, 9]:
        start_month = 7
        end_month = 9
    else:  # 10, 11, 12
        start_month = 10
        end_month = 12
    
    start_date = date(year, start_month, 1)
    
    # Date de fin = dernier jour du dernier mois du trimestre
    if end_month == 12:
        end_date = date(year, 12, 31)
    else:
        # Premier jour du mois suivant - 1 jour
        next_month = end_month + 1
        end_date = date(year, next_month, 1) - pd.Timedelta(days=1)
    
    return start_date, end_date


def get_quarter_dates(year: int, quarter: int) -> tuple[date, date]:
    """Retourne la date de début et de fin d'un trimestre spécifique."""
    if quarter == 1:
        start_month = 1
        end_month = 3
    elif quarter == 2:
        start_month = 4
        end_month = 6
    elif quarter == 3:
        start_month = 7
        end_month = 9
    elif quarter == 4:
        start_month = 10
        end_month = 12
    else:
        raise ValueError(f"Trimestre invalide: {quarter}. Doit être entre 1 et 4.")
    
    start_date = date(year, start_month, 1)
    
    # Date de fin = dernier jour du dernier mois du trimestre
    if end_month == 12:
        end_date = date(year, 12, 31)
    else:
        next_month = end_month + 1
        end_date = date(year, next_month, 1) - pd.Timedelta(days=1)
    
    return start_date, end_date

