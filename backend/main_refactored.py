"""Point d'entrée principal de l'application FastAPI - Version refactorisée"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import ADMIN_EMAIL, ADMIN_PASSWORD, EXEMPT_PATHS, ALLOWED_ADMINS
from database import ensure_schema
from routes import productivity, inspection, upload, lean_actions, meeting_summary

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
app.include_router(productivity.router)
app.include_router(inspection.router)
app.include_router(upload.router)
app.include_router(lean_actions.router)
app.include_router(meeting_summary.router)

