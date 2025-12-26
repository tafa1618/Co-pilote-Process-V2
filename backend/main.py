import os
from io import BytesIO
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import psycopg


# ==================================================
# CONFIG SÉCURITÉ
# ==================================================
ADMIN_EMAIL = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or ""
ENV = os.environ.get("ENV", "dev")
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://kpi_user:kpi_pass@db:5432/kpi_db"

EXEMPT_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/favicon.ico",
}

if ENV != "prod":
    EXEMPT_PATHS.add("/kpi/productivite/analytics")


# ==================================================
# APP
# ==================================================
app = FastAPI(title="KPI Automation Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LATEST_PRODUCTIVITY_DF: pd.DataFrame | None = None
POINTAGE_SCHEMA = """
CREATE TABLE IF NOT EXISTS pointage (
    jour date NOT NULL,
    technicien text NOT NULL,
    equipe text,
    facturable numeric NOT NULL,
    heures_total numeric NOT NULL,
    inserted_at timestamp without time zone DEFAULT now(),
    CONSTRAINT pointage_pk PRIMARY KEY (technicien, jour)
);
"""


def get_conn():
    try:
        return psycopg.connect(DATABASE_URL)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"DB connection failed: {exc}") from exc


def ensure_schema():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(POINTAGE_SCHEMA)
        conn.commit()


@app.on_event("startup")
def _startup():
    ensure_schema()


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
# HEALTH
# ==================================================
@app.get("/health")
async def health():
    return {"status": "ok"}


# ==================================================
# DATA PREPARATION
# ==================================================
def _prepare_productivity_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    # Date
    df["Saisie heures - Date"] = pd.to_datetime(
        df["Saisie heures - Date"], errors="coerce"
    )
    df = df.dropna(subset=["Saisie heures - Date"])

    # Normalisation heures
    if "Hr_Totale" in df.columns:
        hr_col = "Hr_Totale"
    elif "Hr_travaillée" in df.columns:
        hr_col = "Hr_travaillée"
    else:
        raise HTTPException(
            status_code=400,
            detail="Colonne heures manquante (Hr_Totale ou Hr_travaillée)",
        )

    df["heures_travaillees"] = (
        pd.to_numeric(df[hr_col], errors="coerce")
        .fillna(0)
    )

    df["Facturable"] = pd.to_numeric(
        df["Facturable"], errors="coerce"
    ).fillna(0)

    # Features temporelles
    df["jour"] = df["Saisie heures - Date"].dt.day
    df["weekday"] = df["Saisie heures - Date"].dt.weekday
    df["mois"] = df["Saisie heures - Date"].dt.strftime("%b")
    df["month_num"] = df["Saisie heures - Date"].dt.month
    df["mois_period"] = df["Saisie heures - Date"].dt.to_period("M").astype(str)

    # KPI
    df["productivite"] = (
        df["Facturable"] / df["heures_travaillees"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    return df


# ==================================================
# ENDPOINT ANALYTICS
# ==================================================
def _load_from_db() -> pd.DataFrame | None:
    try:
        with get_conn() as conn:
            df_db = pd.read_sql_query(
                "SELECT jour, technicien, equipe, facturable, heures_total FROM pointage",
                conn,
            )
        if df_db.empty:
            return None
        df_db["Saisie heures - Date"] = pd.to_datetime(df_db["jour"])
        df_db["Facturable"] = pd.to_numeric(df_db["facturable"], errors="coerce").fillna(0)
        df_db["Hr_Totale"] = pd.to_numeric(df_db["heures_total"], errors="coerce").fillna(0)
        df_db = df_db.rename(columns={"technicien": "Salarié - Nom", "equipe": "Salarié - Equipe(Nom)"})
        return _prepare_productivity_df(df_db)
    except Exception:
        return None


@app.get("/kpi/productivite/analytics")
async def get_productivity():
    global LATEST_PRODUCTIVITY_DF

    db_df = _load_from_db()
    if db_df is not None:
        df = db_df
    elif LATEST_PRODUCTIVITY_DF is not None:
        df = LATEST_PRODUCTIVITY_DF.copy()
    else:
        raise HTTPException(
            status_code=400,
            detail="Aucune donnée chargée. Veuillez importer un fichier.",
        )

    # =========================
    # GLOBAL KPI
    # =========================
    total_hours = float(df["heures_travaillees"].sum())
    total_fact = float(df["Facturable"].sum())
    global_prod = total_fact / total_hours if total_hours else 0.0

    # =========================
    # MONTHLY
    # =========================
    monthly = (
        df.groupby(["month_num", "mois"])["productivite"]
        .mean()
        .reset_index()
        .sort_values("month_num")[["mois", "productivite"]]
    )

    # =========================
    # TECHNICIENS / ÉQUIPES
    # =========================
    technicians = (
        df.groupby("Salarié - Nom")["productivite"]
        .mean()
        .reset_index()
        .sort_values("productivite", ascending=False)
    )

    teams = (
        df.groupby("Salarié - Equipe(Nom)")["productivite"]
        .mean()
        .reset_index()
    )

    # =========================
    # CORRÉLATION ÉQUIPES
    # =========================
    monthly_avg = df.groupby("mois")["productivite"].mean()

    team_month = (
        df.groupby(["mois", "Salarié - Equipe(Nom)"])["productivite"]
        .mean()
        .reset_index()
    )

    pivot_corr = team_month.pivot(
        index="mois",
        columns="Salarié - Equipe(Nom)",
        values="productivite"
    )

    correlations = pivot_corr.corrwith(monthly_avg).dropna().sort_values(ascending=False)

    correlation_driver = (
        {
            "equipe": correlations.index[0],
            "score": float(correlations.iloc[0]),
        }
        if not correlations.empty
        else None
    )

    # =========================
    # EXHAUSTIVITÉ
    # =========================
    def statut_pointage(h, wd):
        if wd >= 5:
            return "Weekend OK" if h == 0 else "Travail weekend"
        if h == 0:
            return "Non conforme"
        if h < 8:
            return "Incomplet"
        if h == 8:
            return "Conforme"
        return "Surpointage"

    exhaustivity = {"periods": [], "per_period": {}}

    for period in sorted(df["mois_period"].unique()):
        df_p = df[df["mois_period"] == period]

        agg = (
            df_p.groupby(
                ["Salarié - Nom", "Salarié - Equipe(Nom)", "jour", "weekday"],
                as_index=False,
            )
            .agg(heures=("heures_travaillees", "sum"))
        )

        agg["statut"] = agg.apply(
            lambda r: statut_pointage(r["heures"], r["weekday"]), axis=1
        )

        statuts = {}
        heures = {}
        teams_map = {}

        for _, r in agg.iterrows():
            tech = r["Salarié - Nom"]
            day = str(int(r["jour"]))

            statuts.setdefault(tech, {})[day] = r["statut"]
            heures.setdefault(tech, {})[day] = float(r["heures"])
            teams_map[tech] = r["Salarié - Equipe(Nom)"]

        exhaustivity["periods"].append(period)
        exhaustivity["per_period"][period] = {
            "statuts": statuts,
            "heures": heures,
            "teams": teams_map,
        }

    # =========================
    # RESPONSE
    # =========================
    return {
        "global": {
            "total_hours": round(total_hours, 2),
            "total_facturable": round(total_fact, 2),
            "productivite": round(global_prod, 4),
        },
        "monthly": monthly.to_dict(orient="records"),
        "teams": teams.to_dict(orient="records"),
        "technicians": technicians.to_dict(orient="records"),
        "correlation": correlation_driver,
        "exhaustivity": exhaustivity,
    }


# ==================================================
# UPLOAD DATA
# ==================================================
@app.post("/kpi/productivite/upload")
async def upload_kpi(request: Request, file: UploadFile = File(...)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")

    if ADMIN_PASSWORD:
        provided = request.headers.get("X-Admin-Password") or ""
        if provided != ADMIN_PASSWORD:
            raise HTTPException(status_code=403, detail="Mot de passe admin invalide")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        raise HTTPException(status_code=400, detail="Format non supporté")

    buffer = BytesIO(await file.read())

    try:
        df = pd.read_excel(buffer) if suffix != ".csv" else pd.read_csv(buffer)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    required = {
        "Saisie heures - Date",
        "Salarié - Nom",
        "Salarié - Equipe(Nom)",
        "Facturable",
    }

    if not required.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes: {required - set(df.columns)}",
        )

    df_prepared = _prepare_productivity_df(df)

    # Agrégation par technicien / jour
    grouped = (
        df_prepared.groupby(["Saisie heures - Date", "Salarié - Nom", "Salarié - Equipe(Nom)"], as_index=False)
        .agg(
            facturable=("Facturable", "sum"),
            heures_total=("heures_travaillees", "sum"),
        )
    )

    rows = [
        (
            r["Saisie heures - Date"].date(),
            r["Salarié - Nom"],
            r["Salarié - Equipe(Nom)"],
            float(r["facturable"]),
            float(r["heures_total"]),
        )
        for _, r in grouped.iterrows()
    ]

    ensure_schema()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(POINTAGE_SCHEMA)
            cur.executemany(
                """
                INSERT INTO pointage (jour, technicien, equipe, facturable, heures_total)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (technicien, jour)
                DO UPDATE SET
                    equipe = EXCLUDED.equipe,
                    facturable = EXCLUDED.facturable,
                    heures_total = EXCLUDED.heures_total,
                    inserted_at = now();
                """,
                rows,
            )
        conn.commit()

    global LATEST_PRODUCTIVITY_DF
    LATEST_PRODUCTIVITY_DF = df_prepared

    return {
        "message": "Données agrégées et sauvegardées en base (1 ligne par technicien/jour)",
        "rows": len(grouped),
        "owner": user["email"],
    }
