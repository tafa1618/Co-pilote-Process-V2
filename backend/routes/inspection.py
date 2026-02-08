"""Routes pour l'inspection rate"""
from fastapi import APIRouter, HTTPException, Request
from datetime import date
import pandas as pd
from services.inspection_service import calculate_inspection_analytics
from utils.quarters import get_current_quarter_dates, get_quarter_dates
from database import get_conn

router = APIRouter(prefix="/kpi/inspection", tags=["inspection"])


@router.get("/analytics")
async def get_inspection_analytics(request: Request, year: int | None = None, quarter: int | None = None, team: str | None = None):
    """Récupère les analytics d'inspection pour un trimestre donné avec delta hebdomadaire"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    # Déterminer le trimestre à utiliser
    if year is None or quarter is None:
        start_date, end_date = get_current_quarter_dates()
        today = date.today()
        year = today.year
        month = today.month
        if month in [1, 2, 3]:
            quarter = 1
        elif month in [4, 5, 6]:
            quarter = 2
        elif month in [7, 8, 9]:
            quarter = 3
        else:
            quarter = 4
    else:
        start_date, end_date = get_quarter_dates(year, quarter)

    # Calculer la date du mercredi dernier
    today = date.today()
    current_weekday = today.weekday()
    
    if current_weekday == 2:
        last_wednesday = today - pd.Timedelta(days=7)
    elif current_weekday > 2:
        days_back = current_weekday - 2
        last_wednesday = today - pd.Timedelta(days=days_back)
    else:
        days_back = 7 - (2 - current_weekday)
        last_wednesday = today - pd.Timedelta(days=days_back)

    analytics = calculate_inspection_analytics(start_date, end_date, last_wednesday, team)
    
    return {
        "period": f"Q{quarter} {year}",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total": analytics["total"],
        "inspected": analytics["inspected"],
        "not_inspected": analytics["not_inspected"],
        "inspection_rate": analytics["inspection_rate"],
        "delta_weekly": analytics["delta_weekly"],
        "inspection_rate_last_wednesday": analytics["inspection_rate_last_wednesday"],
        "last_wednesday_date": last_wednesday.isoformat(),
        "by_atelier": analytics["by_atelier"],
        "by_type_materiel": analytics["by_type_materiel"],
        "by_technicien": analytics["by_technicien"],
        "records": analytics["records"],
    }


@router.get("/snapshot")
async def get_inspection_snapshot(request: Request):
    """Retourne un snapshot des KPIs d'inspection pour le trimestre actuel"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    start_date, end_date = get_current_quarter_dates()
    today = date.today()
    current_weekday = today.weekday()
    
    if current_weekday == 2:
        last_wednesday = today - pd.Timedelta(days=7)
    elif current_weekday > 2:
        days_back = current_weekday - 2
        last_wednesday = today - pd.Timedelta(days=days_back)
    else:
        days_back = 7 - (2 - current_weekday)
        last_wednesday = today - pd.Timedelta(days=days_back)
    
    analytics = calculate_inspection_analytics(start_date, end_date, last_wednesday)
    
    return {
        "inspection_rate": analytics["inspection_rate"],
        "delta_weekly": analytics["delta_weekly"],
        "total": analytics["total"],
        "inspected": analytics["inspected"],
        "not_inspected": analytics["not_inspected"],
    }


@router.get("/quarters")
async def get_available_quarters(request: Request):
    """Retourne la liste des trimestres disponibles dans les données"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT 
                    EXTRACT(YEAR FROM date_facture)::integer as year,
                    EXTRACT(QUARTER FROM date_facture)::integer as quarter
                FROM inspection_record
                ORDER BY year DESC, quarter DESC
                """
            )
            quarters = cur.fetchall()

    return {
        "quarters": [
            {"year": int(row[0]), "quarter": int(row[1]), "label": f"Q{int(row[1])} {int(row[0])}"}
            for row in quarters
        ]
    }


@router.get("/teams")
async def get_available_teams(request: Request):
    """Retourne la liste des équipes disponibles dans les données d'inspection"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT equipe
                FROM inspection_record
                WHERE equipe IS NOT NULL AND equipe != ''
                ORDER BY equipe ASC
                """
            )
            teams = cur.fetchall()

    return {
        "teams": [row[0] for row in teams if row[0]]
    }


@router.get("/history")
async def get_inspection_history(request: Request):
    """Retourne l'historique trimestriel (Q actuel, Q-1, Q-2, Q-3) pour visualisation"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    today = date.today()
    current_year = today.year
    current_quarter = (today.month - 1) // 3 + 1
    
    history = []
    
    for i in range(4):
        q = current_quarter - i
        y = current_year
        
        while q <= 0:
            q += 4
            y -= 1
        
        start_date, end_date = get_quarter_dates(y, q)
        analytics = calculate_inspection_analytics(start_date, end_date, None)
        
        history.append({
            "year": y,
            "quarter": q,
            "label": f"Q{q} {y}",
            "inspection_rate": analytics["inspection_rate"],
            "total": analytics["total"],
            "inspected": analytics["inspected"],
            "not_inspected": analytics["not_inspected"],
        })
    
    return {"history": history}

