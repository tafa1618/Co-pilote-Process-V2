"""
Productivity KPI API Routes
REST endpoints for productivity and exhaustivity data
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from services.productivity_service import productivity_service

router = APIRouter(prefix="/api/productivity", tags=["Productivity KPI"])


@router.on_event("startup")
async def startup_event():
    """Initialize productivity service on startup"""
    try:
        productivity_service.initialize()
    except Exception as e:
        logger.error(f"Error during productivity service startup: {e}")


@router.get("/daily")
async def get_productivity_daily(
    salarie_id: Optional[int] = Query(None, description="Employee ID"),
    equipe: Optional[str] = Query(None, description="Team name"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get daily productivity data
    
    Returns productivity metrics aggregated by employee and day.
    Supports filtering by employee, team, and date range.
    """
    try:
        data = productivity_service.get_productivity_daily(
            salarie_id=salarie_id,
            equipe=equipe,
            start_date=start_date,
            end_date=end_date
        )
        return {
            "success": True,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team")
async def get_productivity_team(
    period: str = Query("monthly", description="Aggregation period: daily, weekly, monthly"),
    equipe: Optional[str] = Query(None, description="Team name"),
    year: Optional[int] = Query(None, description="Year filter"),
    month: Optional[int] = Query(None, description="Month filter (1-12)")
):
    """
    Get team productivity aggregated by period
    
    Returns productivity metrics aggregated by team and time period.
    Supports daily, weekly, and monthly aggregations.
    """
    if period not in ['daily', 'weekly', 'monthly']:
        raise HTTPException(status_code=400, detail="Period must be 'daily', 'weekly', or 'monthly'")
    
    try:
        data = productivity_service.get_productivity_team(
            period=period,
            equipe=equipe,
            year=year,
            month=month
        )
        return {
            "success": True,
            "period": period,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exhaustivity/summary")
async def get_exhaustivity_summary(
    by: str = Query("team", description="Aggregation level: global, team, employee, month"),
    equipe: Optional[str] = Query(None, description="Team name"),
    year: Optional[int] = Query(None, description="Year filter"),
    month: Optional[int] = Query(None, description="Month filter (1-12)")
):
    """
    Get exhaustivity summary
    
    Returns exhaustivity compliance rates and anomaly counts.
    Supports aggregation by global, team, employee, or month.
    """
    if by not in ['global', 'team', 'employee', 'month']:
        raise HTTPException(status_code=400, detail="by must be 'global', 'team', 'employee', or 'month'")
    
    try:
        data = productivity_service.get_exhaustivity_summary(
            by=by,
            equipe=equipe,
            year=year,
            month=month
        )
        return {
            "success": True,
            "aggregation": by,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exhaustivity/anomalies")
async def get_exhaustivity_anomalies(
    types: Optional[str] = Query(None, description="Comma-separated anomaly types: ROUGE,ORANGE,BLEU"),
    equipe: Optional[str] = Query(None, description="Team name"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of records", le=1000)
):
    """
    Get exhaustivity anomalies
    
    Returns days with anomalous timesheet entries:
    - ROUGE: Missing timesheets (0h on working day)
    - ORANGE: Incomplete days (<8h)
    - BLEU: Overtime days (>8h)
    """
    anomaly_types = None
    if types:
        anomaly_types = [t.strip().upper() for t in types.split(',')]
        invalid = [t for t in anomaly_types if t not in ['ROUGE', 'ORANGE', 'BLEU']]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid anomaly types: {invalid}")
    
    try:
        data = productivity_service.get_exhaustivity_anomalies(
            anomaly_types=anomaly_types,
            equipe=equipe,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return {
            "success": True,
            "types": anomaly_types or ['ROUGE', 'ORANGE', 'BLEU'],
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams")
async def get_teams():
    """
    Get list of all teams
    
    Returns a sorted list of all team names in the dataset.
    """
    try:
        teams = productivity_service.get_teams_list()
        return {
            "success": True,
            "count": len(teams),
            "data": teams
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employees")
async def get_employees(
    equipe: Optional[str] = Query(None, description="Filter by team name")
):
    """
    Get list of all employees
    
    Returns employee details (ID, name, team).
    Optionally filter by team.
    """
    try:
        employees = productivity_service.get_employees_list(equipe=equipe)
        return {
            "success": True,
            "count": len(employees),
            "data": employees
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
