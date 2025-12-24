import os
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

ADMIN_EMAIL = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()

app = FastAPI(title="KPI Automation Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXEMPT_PATHS = {"/health", "/docs", "/openapi.json"}


@app.middleware("http")
async def email_guard(request: Request, call_next):
    """
    Vérifie que l'email utilisateur est autorisé et expose le rôle via request.state.user.
    """
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

    response = await call_next(request)
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_kpi(file: UploadFile = File(...), request: Request | None = None):
    """
    Charge un fichier CSV/Excel en mémoire (BytesIO) et simule une insertion DB.
    Interdit toute écriture disque conformément à la No-Storage Policy.
    """
    user = getattr(request.state, "user", None) if request else None
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Seul l'administrateur peut téléverser")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        raise HTTPException(status_code=400, detail="Format de fichier non supporté (csv, xlsx)")

    raw_content = await file.read()
    buffer = BytesIO(raw_content)

    try:
        if suffix == ".csv":
            frame = pd.read_csv(buffer)
        else:
            frame = pd.read_excel(buffer)
    except Exception as exc:  # pragma: no cover - protection runtime
        raise HTTPException(status_code=400, detail=f"Lecture impossible: {exc}") from exc

    inserted_rows = len(frame.index)
    preview_columns = list(frame.columns)[:5]

    return {
        "message": "Insertion simulée en base (aucune écriture disque effectuée)",
        "kpi": {
            "rows": inserted_rows,
            "columns": preview_columns,
            "role": user["role"],
            "owner": user["email"],
        },
    }

