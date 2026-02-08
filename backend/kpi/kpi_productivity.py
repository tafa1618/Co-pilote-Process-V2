"""Calculs KPI de productivité à partir de données préprocessées
Basé sur la logique du code Streamlit fourni"""
import pandas as pd
from typing import Dict, Any, List


# ==================================================
# CONSTANTES COLONNES (selon code Streamlit)
# ==================================================
COL_TECHNICIEN = "Salarié - Nom"
COL_EQUIPE = "Salarié - Equipe(Nom)"
COL_FACTURABLE = "Facturable"
COL_HEURES = "Hr_travaillée"  # Note: dans le code actuel c'est "Hr_Totale", à harmoniser
COL_DATE = "Saisie heures - Date"


def calculate_global_productivity(df: pd.DataFrame) -> Dict[str, float]:
    """Calcule les KPIs globaux de productivité
    
    Formule: Productivité = Heures_facturables / Heures_travaillées
    
    Args:
        df: DataFrame préprocessé avec colonnes: Heures_travaillées, Heures_facturables
        
    Returns:
        Dict avec: total_hours, total_facturable, productivite (en ratio, pas %)
    """
    if df.empty:
        return {
            "total_hours": 0.0,
            "total_facturable": 0.0,
            "productivite": 0.0,
        }

    total_trav = float(df["Heures_travaillées"].sum())
    total_fact = float(df["Heures_facturables"].sum())
    prod_global = total_fact / total_trav if total_trav > 0 else 0.0

    return {
        "total_hours": round(total_trav, 2),
        "total_facturable": round(total_fact, 2),
        "productivite": round(prod_global, 4),  # Ratio (ex: 0.85 pour 85%)
    }


def calculate_technician_productivity(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Calcule la productivité par technicien
    
    Args:
        df: DataFrame préprocessé avec colonnes: Salarié - Nom, Heures_travaillées, Heures_facturables
        
    Returns:
        Liste de dicts avec: Salarié - Nom, heures_trav, heures_fact, Productivité, triée par productivité décroissante
    """
    if df.empty:
        return []

    prod_tech = (
        df.groupby(COL_TECHNICIEN)
        .agg(
            heures_trav=("Heures_travaillées", "sum"),
            heures_fact=("Heures_facturables", "sum")
        )
        .reset_index()
    )

    prod_tech["Productivité"] = (
        prod_tech["heures_fact"] / prod_tech["heures_trav"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    prod_tech = prod_tech.sort_values("Productivité", ascending=False)

    return prod_tech.to_dict(orient="records")


def calculate_monthly_productivity(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Calcule la productivité mensuelle globale
    
    Args:
        df: DataFrame préprocessé avec colonnes: Mois, Heures_travaillées, Heures_facturables
        
    Returns:
        Liste de dicts avec: Mois, heures_trav, heures_fact, Productivité globale, triée par Mois
    """
    if df.empty:
        return []

    prod_mois_global = (
        df.groupby("Mois")
        .agg(
            heures_trav=("Heures_travaillées", "sum"),
            heures_fact=("Heures_facturables", "sum")
        )
        .reset_index()
        .sort_values("Mois")
    )

    prod_mois_global["Productivité globale"] = (
        prod_mois_global["heures_fact"] / prod_mois_global["heures_trav"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    return prod_mois_global.to_dict(orient="records")


def calculate_team_productivity(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Calcule la productivité par équipe
    
    Args:
        df: DataFrame préprocessé avec colonnes: Salarié - Equipe(Nom), Heures_travaillées, Heures_facturables
        
    Returns:
        Liste de dicts avec: Salarié - Equipe(Nom), heures_trav, heures_fact, Productivité
    """
    if df.empty:
        return []

    team_agg = (
        df.groupby(COL_EQUIPE)
        .agg(
            heures_trav=("Heures_travaillées", "sum"),
            heures_fact=("Heures_facturables", "sum")
        )
        .reset_index()
    )

    team_agg["Productivité"] = (
        team_agg["heures_fact"] / team_agg["heures_trav"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    return team_agg.to_dict(orient="records")


def calculate_team_monthly_productivity(df: pd.DataFrame, equipe: str) -> List[Dict[str, Any]]:
    """Calcule la productivité mensuelle pour une équipe spécifique
    
    Args:
        df: DataFrame préprocessé avec colonnes: Salarié - Equipe(Nom), Mois, Heures_travaillées, Heures_facturables
        equipe: Nom de l'équipe à analyser
        
    Returns:
        Liste de dicts avec: Mois, heures_trav, heures_fact, Productivité équipe
    """
    if df.empty:
        return []

    df_eq = df[df[COL_EQUIPE] == equipe]

    if df_eq.empty:
        return []

    prod_mois_eq = (
        df_eq.groupby("Mois")
        .agg(
            heures_trav=("Heures_travaillées", "sum"),
            heures_fact=("Heures_facturables", "sum")
        )
        .reset_index()
        .sort_values("Mois")
    )

    prod_mois_eq["Productivité équipe"] = (
        prod_mois_eq["heures_fact"] / prod_mois_eq["heures_trav"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    return prod_mois_eq.to_dict(orient="records")


def calculate_correlation_driver(df: pd.DataFrame) -> Dict[str, Any] | None:
    """Calcule l'équipe driver (corrélation avec la productivité globale mensuelle)
    
    Args:
        df: DataFrame préprocessé avec colonnes: Mois, Salarié - Equipe(Nom), Heures_travaillées, Heures_facturables
        
    Returns:
        Dict avec: equipe, score (corrélation), ou None si pas de corrélation
    """
    if df.empty:
        return None

    # Série globale mensuelle (référence)
    global_ts = (
        df.groupby("Mois")
        .agg(
            heures_trav=("Heures_travaillées", "sum"),
            heures_fact=("Heures_facturables", "sum")
        )
        .reset_index()
        .sort_values("Mois")
    )

    global_ts["Productivité globale"] = (
        global_ts["heures_fact"] / global_ts["heures_trav"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    # Équipes analysées
    equipes_corr = sorted(df[COL_EQUIPE].dropna().unique())
    correlations = []

    for equipe in equipes_corr:
        df_eq = df[df[COL_EQUIPE] == equipe]

        eq_ts = (
            df_eq.groupby("Mois")
            .agg(
                heures_trav=("Heures_travaillées", "sum"),
                heures_fact=("Heures_facturables", "sum")
            )
            .reset_index()
            .sort_values("Mois")
        )

        eq_ts["Productivité équipe"] = (
            eq_ts["heures_fact"] / eq_ts["heures_trav"]
        ).replace([float("inf"), -float("inf")], 0).fillna(0)

        # Fusion équipe vs global
        merged = pd.merge(
            global_ts[["Mois", "Productivité globale"]],
            eq_ts[["Mois", "Productivité équipe"]],
            on="Mois",
            how="inner"
        )

        if len(merged) < 2:  # Besoin d'au moins 2 points pour corrélation
            continue

        # Corrélation
        corr = merged["Productivité globale"].corr(merged["Productivité équipe"])

        if not pd.isna(corr):
            correlations.append({
                "Équipe": equipe,
                "Corrélation": corr
            })

    if not correlations:
        return None

    corr_df = pd.DataFrame(correlations)
    equipe_driver = corr_df.sort_values("Corrélation", ascending=False).iloc[0]

    return {
        "equipe": equipe_driver["Équipe"],
        "score": float(equipe_driver["Corrélation"]),
    }


def calculate_exhaustivity(
    df: pd.DataFrame,
    equipe: str,
    mois_periode: str
) -> Dict[str, Any]:
    """Calcule l'exhaustivité des pointages pour une équipe et un mois
    
    Args:
        df: DataFrame préprocessé avec colonnes: Salarié - Nom, Salarié - Equipe(Nom), 
            Saisie heures - Date, Hr_Totale (pour l'agrégation quotidienne)
        equipe: Nom de l'équipe à auditer
        mois_periode: Mois au format période (ex: "2025-01")
        
    Returns:
        Dict avec: pivot_statut, pivot_heures, color_map, techniciens, jours
    """
    if df.empty:
        return {
            "pivot_statut": pd.DataFrame(),
            "pivot_heures": pd.DataFrame(),
            "color_map": {},
            "techniciens": [],
            "jours": [],
        }

    # Filtrer par équipe et mois
    df_cal = df[
        (df[COL_EQUIPE] == equipe) &
        (df["Mois_periode"] == mois_periode)
    ].copy()

    if df_cal.empty:
        return {
            "pivot_statut": pd.DataFrame(),
            "pivot_heures": pd.DataFrame(),
            "color_map": {},
            "techniciens": [],
            "jours": [],
        }

    # Agrégation : 1 ligne / jour / technicien
    # Note: Le code Streamlit utilise "Hr_Totale" pour l'agrégation quotidienne
    daily = (
        df_cal
        .groupby([COL_DATE, COL_TECHNICIEN], as_index=False)
        .agg(
            heures=("Hr_Totale", "sum")  # Utilise Hr_Totale pour l'agrégation quotidienne
        )
    )

    daily["Jour"] = daily[COL_DATE].dt.day
    daily["Jour_semaine"] = daily[COL_DATE].dt.weekday  # 0=lundi

    # Règles métier exhaustivité
    def statut_pointage(h, wd):
        if wd >= 5:  # samedi / dimanche
            return "Weekend OK" if h == 0 else "Travail weekend"
        if h == 0:
            return "Non conforme"
        if h < 8:
            return "Incomplet"
        if h == 8:
            return "Conforme"
        return "Surpointage"

    daily["Statut"] = daily.apply(
        lambda r: statut_pointage(r["heures"], r["Jour_semaine"]),
        axis=1
    )

    # Pivot sécurisé
    pivot_statut = daily.pivot_table(
        index=COL_TECHNICIEN,
        columns="Jour",
        values="Statut",
        aggfunc="first"
    )

    pivot_heures = daily.pivot_table(
        index=COL_TECHNICIEN,
        columns="Jour",
        values="heures",
        aggfunc="sum"
    )

    # Mapping couleurs
    color_map = {
        "Non conforme": "#d73027",
        "Incomplet": "#fee08b",
        "Conforme": "#1a9850",
        "Surpointage": "#4575b4",
        "Weekend OK": "#f0f0f0",
        "Travail weekend": "#984ea3"
    }

    return {
        "pivot_statut": pivot_statut,
        "pivot_heures": pivot_heures,
        "color_map": color_map,
        "techniciens": pivot_statut.index.tolist(),
        "jours": pivot_statut.columns.tolist(),
    }
