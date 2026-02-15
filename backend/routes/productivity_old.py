"""Routes pour la productivité"""
from fastapi import APIRouter, HTTPException, Request
from services.productivity_service_legacy import (
    load_from_db,
    get_latest_df,
    set_latest_df,
    process_uploaded_file,
    calculate_all_productivity_analytics,
)
from kpi.kpi_productivity import calculate_exhaustivity

router = APIRouter(prefix="/kpi/productivite", tags=["productivity"])


@router.get("/analytics")
async def get_productivity(request: Request):
    """Récupère les analytics de productivité"""
    db_df = load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
    elif get_latest_df() is not None and not get_latest_df().empty:
        df = get_latest_df().copy()
    else:
        raise HTTPException(
            status_code=400,
            detail="Aucune donnée chargée. Veuillez importer un fichier.",
        )

    analytics = calculate_all_productivity_analytics(df)
    return analytics


@router.get("/exhaustivite")
async def get_exhaustivite(equipe: str, mois_periode: str):
    """Récupère l'exhaustivité (statuts de pointage) pour une équipe et un mois
    
    Args:
        equipe: Nom de l'équipe à auditer
        mois_periode: Mois au format période (ex: "2025-01")
    """
    db_df = load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
    elif get_latest_df() is not None and not get_latest_df().empty:
        df = get_latest_df().copy()
    else:
        raise HTTPException(
            status_code=400,
            detail="Aucune donnée chargée. Veuillez importer un fichier.",
        )
    
    exhaust = calculate_exhaustivity(df, equipe=equipe, mois_periode=mois_periode)
    return exhaust


@router.get("/debug")
async def debug_productivity():
    """Endpoint de debug pour inspecter les données et calculs"""
    db_df = load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
        source = "database"
    elif get_latest_df() is not None and not get_latest_df().empty:
        df = get_latest_df().copy()
        source = "memory"
    else:
        return {"error": "Aucune donnée chargée"}
    
    # Informations sur le DataFrame
    info = {
        "source": source,
        "total_rows": len(df),
        "columns": list(df.columns),
        "date_range": {
            "min": str(df["Saisie heures - Date"].min()) if not df.empty else None,
            "max": str(df["Saisie heures - Date"].max()) if not df.empty else None,
        },
        "sample_data": df.head(5).to_dict(orient="records") if not df.empty else [],
    }
    
    # Vérifications des valeurs
    checks = {
        "facturable": {
            "sum": float(df["Facturable"].sum()),
            "min": float(df["Facturable"].min()),
            "max": float(df["Facturable"].max()),
            "null_count": int(df["Facturable"].isna().sum()),
            "zero_count": int((df["Facturable"] == 0).sum()),
        },
        "heures_travaillees": {
            "sum": float(df["heures_travaillees"].sum()),
            "min": float(df["heures_travaillees"].min()),
            "max": float(df["heures_travaillees"].max()),
            "null_count": int(df["heures_travaillees"].isna().sum()),
            "zero_count": int((df["heures_travaillees"] == 0).sum()),
        },
        "productivite_calculee": {
            "global": float(df["Facturable"].sum() / df["heures_travaillees"].sum()) if df["heures_travaillees"].sum() > 0 else 0.0,
            "mean": float(df["productivite"].mean()) if "productivite" in df.columns else None,
        }
    }
    
    # Agrégation par technicien (top 5)
    import pandas as pd
    tech_agg = (
        df.groupby("Salarié - Nom")
        .agg(
            facturable=("Facturable", "sum"),
            heures=("heures_travaillees", "sum")
        )
        .reset_index()
    )
    tech_agg["productivite"] = (
        tech_agg["facturable"] / tech_agg["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    tech_agg = tech_agg.sort_values("productivite", ascending=False).head(5)
    
    return {
        "info": info,
        "checks": checks,
        "top_technicians": tech_agg.to_dict(orient="records"),
    }

