"""Calculs KPI LLTI (Lead Time to Invoice)"""
import pandas as pd
from typing import Dict, Any, List

# Constantes
STANDARDIZED_LLTI_JOURS = "LLTI_jours"

# Seuils de performance
EXCELLENT_THRESHOLD = 7  # < 7 jours
ADVANCED_THRESHOLD = 17  # >= 7 et < 17 jours
EMERGING_THRESHOLD = 21  # >= 17 et <= 21 jours


def calculate_global_llti(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule le KPI global LLTI (moyenne et médiane)
    
    Args:
        df: DataFrame préprocessé avec colonne LLTI_jours
    Returns:
        Dict avec: moyenne_llti, mediane_llti, total_factures, status
    """
    if df.empty or STANDARDIZED_LLTI_JOURS not in df.columns:
        return {
            "moyenne_llti": 0.0,
            "mediane_llti": 0.0,
            "total_factures": 0,
            "status": "N/A",
        }
    
    moyenne = float(df[STANDARDIZED_LLTI_JOURS].mean())
    mediane = float(df[STANDARDIZED_LLTI_JOURS].median())
    # Nombre de factures uniques (pas le nombre de lignes)
    col_facture = "N° Facture (Lignes)"
    if col_facture in df.columns:
        total = int(df[col_facture].nunique())
    else:
        total = len(df)
    
    # Catégorisation basée sur la moyenne
    if moyenne < EXCELLENT_THRESHOLD:
        status = "Excellent"
    elif moyenne < ADVANCED_THRESHOLD:
        status = "Advanced"
    elif moyenne <= EMERGING_THRESHOLD:
        status = "Emerging"
    else:
        status = "À améliorer"
    
    return {
        "moyenne_llti": round(moyenne, 1),
        "mediane_llti": round(mediane, 0),
        "total_factures": total,
        "status": status,
    }


def calculate_llti_by_client(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calcule le LLTI par client
    
    Args:
        df: DataFrame préprocessé avec colonnes LLTI_jours et Nom Client OR (or)
    Returns:
        Liste de dicts avec: client, moyenne_llti, total_factures
    """
    if df.empty:
        return []
    
    col_client = "Nom Client OR (or)"
    if col_client not in df.columns:
        return []
    
    by_client = (
        df.groupby(col_client)
        .agg(
            moyenne_llti=(STANDARDIZED_LLTI_JOURS, "mean"),
            total_factures=(STANDARDIZED_LLTI_JOURS, "count")
        )
        .reset_index()
        .sort_values("moyenne_llti")
    )
    
    by_client["moyenne_llti"] = by_client["moyenne_llti"].round(2)
    
    return by_client.to_dict(orient="records")


def calculate_llti_by_or(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calcule le LLTI par OR (Order of Repair)
    
    Args:
        df: DataFrame préprocessé avec colonnes LLTI_jours et N° OR (Segment)
    Returns:
        Liste de dicts avec: or_numero, llti_jours, date_facture, date_pointage
    """
    if df.empty:
        return []
    
    col_or = "N° OR (Segment)"
    if col_or not in df.columns:
        return []
    
    cols_to_keep = [
        col_or,
        "N° Facture (Lignes)",
        "Date Facture (Lignes)",
        "Pointage dernière date (Segment)",
        STANDARDIZED_LLTI_JOURS,
    ]
    
    available_cols = [c for c in cols_to_keep if c in df.columns]
    result_df = df[available_cols].copy()
    
    # Renommer pour l'API
    result_df = result_df.rename(columns={
        col_or: "or_numero",
        "N° Facture (Lignes)": "num_facture",
        "Date Facture (Lignes)": "date_facture",
        "Pointage dernière date (Segment)": "date_pointage",
        STANDARDIZED_LLTI_JOURS: "llti_jours",
    })
    
    # Convertir les dates en string pour JSON
    for col in ["date_facture", "date_pointage"]:
        if col in result_df.columns:
            result_df[col] = result_df[col].dt.strftime("%Y-%m-%d")
    
    result_df = result_df.sort_values("llti_jours", ascending=False)  # Tri décroissant comme dans Streamlit
    
    return result_df.to_dict(orient="records")


def calculate_llti_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """
    Calcule la distribution des LLTI par catégorie
    
    Args:
        df: DataFrame préprocessé avec colonne LLTI_jours
    Returns:
        Dict avec: excellent, advanced, emerging, a_améliorer
    """
    if df.empty or STANDARDIZED_LLTI_JOURS not in df.columns:
        return {
            "excellent": 0,
            "advanced": 0,
            "emerging": 0,
            "a_ameliorer": 0,
        }
    
    excellent = len(df[df[STANDARDIZED_LLTI_JOURS] < EXCELLENT_THRESHOLD])
    advanced = len(df[(df[STANDARDIZED_LLTI_JOURS] >= EXCELLENT_THRESHOLD) & 
                      (df[STANDARDIZED_LLTI_JOURS] < ADVANCED_THRESHOLD)])
    emerging = len(df[(df[STANDARDIZED_LLTI_JOURS] >= ADVANCED_THRESHOLD) & 
                      (df[STANDARDIZED_LLTI_JOURS] <= EMERGING_THRESHOLD)])
    a_ameliorer = len(df[df[STANDARDIZED_LLTI_JOURS] > EMERGING_THRESHOLD])
    
    return {
        "excellent": int(excellent),
        "advanced": int(advanced),
        "emerging": int(emerging),
        "a_ameliorer": int(a_ameliorer),
    }


def calculate_all_llti_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule tous les analytics LLTI à partir d'un DataFrame préprocessé
    
    Args:
        df: DataFrame préprocessé avec colonne LLTI_jours
    Returns:
        Dict avec tous les analytics
    """
    return {
        "global": calculate_global_llti(df),
        "by_client": calculate_llti_by_client(df),
        "by_or": calculate_llti_by_or(df),
        "distribution": calculate_llti_distribution(df),
    }
