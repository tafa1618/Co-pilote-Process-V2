"""Point d'entrée principal de l'application FastAPI - Version refactorisée"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import ADMIN_EMAIL, ADMIN_PASSWORD, EXEMPT_PATHS, ALLOWED_ADMINS
from database import ensure_schema
from routes import inspection, upload, lean_actions, meeting_summary, llti, productivity_kpi
# from routes import productivity_old  # Disabled - legacy routes with incompatible imports

# ==================================================
# APP
# ==================================================
app = FastAPI(title="KPI Automation Backend", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# MIDDLEWARE AUTH
# ==================================================
@app.middleware("http")
async def email_guard(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    if request.url.path in EXEMPT_PATHS:
        return await call_next(request)

    raw_email = request.headers.get("x-user-email") or request.headers.get("X-User-Email")
    email = (raw_email or "").strip().lower()

    if not email or not email.endswith("@neemba.com"):
        raise HTTPException(
            status_code=401,
            detail="Email non autorisé (domaine @neemba.com requis)",
        )

    role = "admin" if ADMIN_EMAIL and email == ADMIN_EMAIL else "guest"
    request.state.user = {"email": email, "role": role}

    return await call_next(request)


# ==================================================
# STARTUP
# ==================================================
@app.on_event("startup")
def _startup():
    ensure_schema()


# ==================================================
# HEALTH
# ==================================================
@app.get("/health")
async def health():
    return {"status": "ok"}


# ==================================================
# ROUTES
# ==================================================
# app.include_router(productivity_old.router)  # Disabled - legacy routes
app.include_router(productivity_kpi.router)  # New Productivity KPI endpoints
app.include_router(inspection.router)
app.include_router(llti.router)
app.include_router(upload.router)
app.include_router(lean_actions.router)
app.include_router(meeting_summary.router)

from agents.mock_agent import MockAgentService
@app.get("/api/analyze/mock", tags=["Analysis"])
def get_mock_analysis():
    return MockAgentService.get_analysis()

# SEP Digital Twin Endpoints
@app.get("/api/sep/kpis", tags=["SEP"])
def get_sep_kpis():
    """Get all SEP KPIs (12 official metrics)"""
    from services.mock_sep_data import MockSEPDataService
    return MockSEPDataService.get_sep_kpis()

@app.get("/api/sep/custom-kpis", tags=["SEP"])
def get_custom_kpis():
    """Get custom internal KPIs"""
    from services.mock_sep_data import MockSEPDataService
    return MockSEPDataService.get_custom_kpis()

@app.get("/api/sep/insights", tags=["SEP"])
def get_agent_insights():
    """Get agent insights and recommendations"""
    from services.mock_sep_data import MockSEPDataService
    return MockSEPDataService.get_agent_insights()

