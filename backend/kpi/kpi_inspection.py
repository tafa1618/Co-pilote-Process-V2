"""Calculs KPI d'inspection à partir de données préprocessées"""
import pandas as pd
from datetime import date
from typing import Any, Dict


def calculate_inspection_rate(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcule le taux d'inspection global
    
    Args:
        df: DataFrame préprocessé avec colonnes: or_segment, is_inspected
        
    Returns:
        Dict avec: total, inspected, not_inspected, inspection_rate
    """
    if df.empty:
        return {
            "total": 0,
            "inspected": 0,
            "not_inspected": 0,
            "inspection_rate": 0.0,
        }

    # Calcul basé sur les OR uniques
    or_status = df.groupby("or_segment").agg({
        "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
    }).reset_index()
    
    total_or = len(or_status)
    inspected_or = len(or_status[or_status["is_inspected"] == "Inspecté"])
    not_inspected_or = total_or - inspected_or
    inspection_rate = (inspected_or / total_or * 100) if total_or > 0 else 0.0
    
    return {
        "total": total_or,
        "inspected": inspected_or,
        "not_inspected": not_inspected_or,
        "inspection_rate": round(inspection_rate, 2),
    }


def calculate_weekly_delta(
    df_current: pd.DataFrame,
    df_last: pd.DataFrame
) -> Dict[str, float]:
    """Calcule le delta hebdomadaire du taux d'inspection
    
    Args:
        df_current: DataFrame préprocessé pour la période actuelle
        df_last: DataFrame préprocessé pour le mercredi dernier
        
    Returns:
        Dict avec: delta_weekly, inspection_rate_last_wednesday
    """
    current_rate = calculate_inspection_rate(df_current)
    last_rate = calculate_inspection_rate(df_last)
    
    delta_weekly = current_rate["inspection_rate"] - last_rate["inspection_rate"]
    
    return {
        "delta_weekly": round(delta_weekly, 2),
        "inspection_rate_last_wednesday": last_rate["inspection_rate"],
    }


def calculate_by_atelier(df: pd.DataFrame) -> list[Dict[str, Any]]:
    """Calcule le taux d'inspection par atelier
    
    Args:
        df: DataFrame préprocessé avec colonnes: atelier, or_segment, is_inspected
        
    Returns:
        Liste de dicts avec: atelier, total, inspected, rate
    """
    if df.empty or "atelier" not in df.columns or df["atelier"].isna().all():
        return []

    atelier_or_stats = df.groupby(["atelier", "or_segment"]).agg({
        "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
    }).reset_index()
    
    atelier_stats = atelier_or_stats.groupby("atelier").agg({
        "or_segment": "count",
        "is_inspected": lambda x: (x == "Inspecté").sum(),
    }).reset_index()
    atelier_stats.columns = ["atelier", "total", "inspected"]
    atelier_stats["rate"] = (atelier_stats["inspected"] / atelier_stats["total"] * 100).round(2)
    
    return atelier_stats.fillna("").to_dict(orient="records")


def calculate_by_type_materiel(df: pd.DataFrame) -> list[Dict[str, Any]]:
    """Calcule le taux d'inspection par type de matériel
    
    Args:
        df: DataFrame préprocessé avec colonnes: type_materiel, or_segment, is_inspected
        
    Returns:
        Liste de dicts avec: type_materiel, total, inspected, rate
    """
    if df.empty or "type_materiel" not in df.columns or df["type_materiel"].isna().all():
        return []

    type_or_stats = df.groupby(["type_materiel", "or_segment"]).agg({
        "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
    }).reset_index()
    
    type_stats = type_or_stats.groupby("type_materiel").agg({
        "or_segment": "count",
        "is_inspected": lambda x: (x == "Inspecté").sum(),
    }).reset_index()
    type_stats.columns = ["type_materiel", "total", "inspected"]
    type_stats["rate"] = (type_stats["inspected"] / type_stats["total"] * 100).round(2)
    
    return type_stats.fillna("").to_dict(orient="records")


def calculate_by_technicien(df: pd.DataFrame) -> list[Dict[str, Any]]:
    """Calcule le taux d'inspection par technicien
    
    Args:
        df: DataFrame préprocessé avec colonnes: technicien, equipe, or_segment, is_inspected
        
    Returns:
        Liste de dicts avec: technicien, equipe, total_or, inspected_or, rate, triée par rate décroissante
    """
    if df.empty or "technicien" not in df.columns or df["technicien"].isna().all():
        return []

    df_with_tech = df[df["technicien"].notna() & (df["technicien"].astype(str).str.strip() != "")]
    
    if df_with_tech.empty:
        return []

    tech_or_stats = df_with_tech.groupby(["technicien", "or_segment"]).agg({
        "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté",
        "equipe": "first",
    }).reset_index()
    
    tech_stats = tech_or_stats.groupby("technicien").agg({
        "or_segment": "count",
        "is_inspected": lambda x: (x == "Inspecté").sum(),
        "equipe": "first",
    }).reset_index()
    tech_stats.columns = ["technicien", "total_or", "inspected_or", "equipe"]
    tech_stats["rate"] = (tech_stats["inspected_or"] / tech_stats["total_or"] * 100).round(2)
    tech_stats = tech_stats.sort_values("rate", ascending=False)
    
    return tech_stats.fillna("").to_dict(orient="records")


def calculate_full_inspection_analytics(
    df: pd.DataFrame,
    df_last: pd.DataFrame | None = None
) -> Dict[str, Any]:
    """Calcule tous les analytics d'inspection
    
    Args:
        df: DataFrame préprocessé pour la période actuelle
        df_last: DataFrame préprocessé pour le mercredi dernier (optionnel)
        
    Returns:
        Dict complet avec tous les analytics
    """
    # Calculs de base
    rate_data = calculate_inspection_rate(df)
    
    # Delta hebdomadaire
    delta_data = {
        "delta_weekly": 0.0,
        "inspection_rate_last_wednesday": 0.0,
    }
    if df_last is not None and not df_last.empty:
        delta_data = calculate_weekly_delta(df, df_last)
    
    # Statistiques par dimension
    by_atelier = calculate_by_atelier(df)
    by_type_materiel = calculate_by_type_materiel(df)
    by_technicien = calculate_by_technicien(df)
    
    # Statistiques sur les lignes (pour référence)
    total_lines = len(df)
    inspected_lines = len(df[df["is_inspected"] == "Inspecté"])
    not_inspected_lines = len(df[df["is_inspected"] == "Non Inspecté"])
    
    # Records limités
    records = df.head(100).to_dict(orient="records")
    
    return {
        "total": rate_data["total"],
        "inspected": rate_data["inspected"],
        "not_inspected": rate_data["not_inspected"],
        "total_lines": total_lines,
        "inspected_lines": inspected_lines,
        "not_inspected_lines": not_inspected_lines,
        "inspection_rate": rate_data["inspection_rate"],
        "delta_weekly": delta_data["delta_weekly"],
        "inspection_rate_last_wednesday": delta_data["inspection_rate_last_wednesday"],
        "by_atelier": by_atelier,
        "by_type_materiel": by_type_materiel,
        "by_technicien": by_technicien,
        "records": records,
    }

