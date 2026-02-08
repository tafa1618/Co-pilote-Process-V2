"""Routes pour le KPI LLTI (Lead Time to Invoice)"""
from fastapi import APIRouter, HTTPException, Request
from services.llti_service import calculate_all_llti_analytics_from_db, load_from_db, get_latest_df

router = APIRouter(prefix="/kpi/llti", tags=["llti"])


@router.get("/analytics")
async def get_llti_analytics(request: Request):
    """Récupère les analytics LLTI (trimestre en cours)"""
    analytics = calculate_all_llti_analytics_from_db()
    return analytics


@router.get("/snapshot")
async def get_llti_snapshot(request: Request):
    """Récupère un snapshot LLTI pour les KPIs globaux"""
    analytics = calculate_all_llti_analytics_from_db()
    global_data = analytics.get("global", {})
    
    return {
        "moyenne_llti": global_data.get("moyenne_llti", 0.0),
        "status": global_data.get("status", "N/A"),
        "total_factures": global_data.get("total_factures", 0),
    }

