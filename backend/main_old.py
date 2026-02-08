import os
from io import BytesIO
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import psycopg
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


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
    "/kpi/inspection/analytics",
    "/kpi/inspection/quarters",
    "/kpi/inspection/snapshot",
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
    or_numero text,
    inserted_at timestamp without time zone DEFAULT now(),
    CONSTRAINT pointage_pk PRIMARY KEY (technicien, jour)
);
"""

LEAN_ACTION_SCHEMA = """
CREATE TABLE IF NOT EXISTS lean_action (
    id SERIAL PRIMARY KEY,
    date_ouverture date NOT NULL DEFAULT CURRENT_DATE,
    date_cloture_prevue date,
    probleme text NOT NULL,
    owner text NOT NULL,
    statut text NOT NULL DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'Clôturé')),
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);
"""

MEETING_SUMMARY_SCHEMA = """
CREATE TABLE IF NOT EXISTS meeting_summary (
    id SERIAL PRIMARY KEY,
    meeting_date date NOT NULL DEFAULT CURRENT_DATE,
    productivite_globale numeric,
    total_heures numeric,
    total_facturable numeric,
    actions_ouvertes integer DEFAULT 0,
    actions_critiques integer DEFAULT 0,
    notes_discussion text,
    pdf_path text,
    created_by text NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);
"""

INSPECTION_RECORD_SCHEMA = """
CREATE TABLE IF NOT EXISTS inspection_record (
    id SERIAL PRIMARY KEY,
    sn text NOT NULL,
    or_segment text,
    type_materiel text,
    atelier text,
    date_facture date NOT NULL,
    is_inspected text NOT NULL CHECK (is_inspected IN ('Inspecté', 'Non Inspecté')),
    technicien text,
    equipe text,
    inserted_at timestamp without time zone DEFAULT now(),
    CONSTRAINT inspection_record_sn_date_unique UNIQUE (sn, date_facture)
);
"""

# Liste des emails autorisés pour accéder à SuiviSepMeeting
# ⚠️ IMPORTANT : Ajoutez les emails autorisés dans cette liste
ALLOWED_ADMINS = [
    (os.environ.get("ADMIN_EMAIL") or "").strip().lower(),
    # Exemple : ajouter d'autres emails autorisés ici
    # "manager@neemba.com",
    # "directeur@neemba.com",
    # "superviseur@neemba.com",
]
ALLOWED_ADMINS = [e for e in ALLOWED_ADMINS if e]  # Filtrer les valeurs vides


def get_conn():
    try:
        return psycopg.connect(DATABASE_URL)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"DB connection failed: {exc}") from exc


def ensure_schema():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(POINTAGE_SCHEMA)
            cur.execute(LEAN_ACTION_SCHEMA)
            cur.execute(MEETING_SUMMARY_SCHEMA)
            cur.execute(INSPECTION_RECORD_SCHEMA)
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
# UTILITAIRES TRIMESTRE
# ==================================================
def get_current_quarter_dates() -> tuple[date, date]:
    """Retourne la date de début et de fin du trimestre actuel."""
    today = date.today()
    year = today.year
    month = today.month
    
    # Déterminer le trimestre
    if month in [1, 2, 3]:
        quarter = 1
        start_month = 1
        end_month = 3
    elif month in [4, 5, 6]:
        quarter = 2
        start_month = 4
        end_month = 6
    elif month in [7, 8, 9]:
        quarter = 3
        start_month = 7
        end_month = 9
    else:  # 10, 11, 12
        quarter = 4
        start_month = 10
        end_month = 12
    
    start_date = date(year, start_month, 1)
    
    # Date de fin = dernier jour du dernier mois du trimestre
    if end_month == 12:
        end_date = date(year, 12, 31)
    else:
        # Premier jour du mois suivant - 1 jour
        next_month = end_month + 1
        end_date = date(year, next_month, 1) - pd.Timedelta(days=1)
    
    return start_date, end_date


def get_quarter_dates(year: int, quarter: int) -> tuple[date, date]:
    """Retourne la date de début et de fin d'un trimestre spécifique."""
    if quarter == 1:
        start_month = 1
        end_month = 3
    elif quarter == 2:
        start_month = 4
        end_month = 6
    elif quarter == 3:
        start_month = 7
        end_month = 9
    elif quarter == 4:
        start_month = 10
        end_month = 12
    else:
        raise ValueError(f"Trimestre invalide: {quarter}. Doit être entre 1 et 4.")
    
    start_date = date(year, start_month, 1)
    
    # Date de fin = dernier jour du dernier mois du trimestre
    if end_month == 12:
        end_date = date(year, 12, 31)
    else:
        next_month = end_month + 1
        end_date = date(year, next_month, 1) - pd.Timedelta(days=1)
    
    return start_date, end_date


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

    # Normalisation heures - uniquement Hr_Totale
    if "Hr_Totale" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="Colonne Hr_Totale manquante (obligatoire)",
        )

    # Remplacer les valeurs vides/NaN par 0 pour les heures
    # pd.to_numeric avec errors="coerce" convertit les valeurs invalides en NaN, puis fillna(0) les remplace par 0
    df["heures_travaillees"] = (
        pd.to_numeric(df["Hr_Totale"], errors="coerce")
        .fillna(0)
    )

    # Remplacer les valeurs vides/NaN par 0 pour le facturable
    df["Facturable"] = (
        pd.to_numeric(df["Facturable"], errors="coerce")
        .fillna(0)
    )

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


def _load_inspection_from_db(start_date: date | None = None, end_date: date | None = None) -> pd.DataFrame | None:
    """Charge les données d'inspection depuis la base de données"""
    try:
        with get_conn() as conn:
            query = "SELECT sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe FROM inspection_record"
            params = []
            if start_date and end_date:
                query += " WHERE date_facture >= %s AND date_facture <= %s"
                params = [start_date, end_date]
            query += " ORDER BY date_facture DESC"
            
            df = pd.read_sql_query(query, conn, params=params if params else None)
            return df if not df.empty else None
    except Exception as exc:
        print(f"⚠️ Erreur chargement inspection depuis DB: {exc}")
        return None


def _calculate_inspection_analytics(start_date: date, end_date: date, last_wednesday: date | None = None, team: str | None = None) -> Dict[str, Any]:
    """Fonction utilitaire pour calculer les analytics d'inspection (utilisée par tous les composants)
    
    Logique de calcul :
    - Taux d'inspection = (Nombre d'OR uniques avec Is Inspected = "Inspecté") / (Nombre Total d'OR uniques facturés) * 100
    - C'est un KPI trimestriel basé sur les OR, pas sur les lignes individuelles
    """
    # Charger les données depuis la base
    df = _load_inspection_from_db(start_date, end_date)
    
    if df is None or df.empty:
        return {
            "total": 0,
            "inspected": 0,
            "not_inspected": 0,
            "inspection_rate": 0.0,
            "delta_weekly": 0.0,
            "inspection_rate_last_wednesday": 0.0,
            "by_atelier": [],
            "by_type_materiel": [],
            "by_technicien": [],
            "records": [],
        }
    
    # Filtrer les lignes avec or_segment valide (non vide)
    df_with_or = df[df["or_segment"].notna() & (df["or_segment"].astype(str).str.strip() != "")]
    
    # Filtrer par équipe si spécifié
    if team:
        # Filtrer par équipe du technicien
        df_with_or = df_with_or[
            (df_with_or["equipe"].notna() & (df_with_or["equipe"].astype(str).str.strip().str.lower() == team.lower()))
        ]
    
    if df_with_or.empty:
        return {
            "total": 0,
            "inspected": 0,
            "not_inspected": 0,
            "inspection_rate": 0.0,
            "delta_weekly": 0.0,
            "inspection_rate_last_wednesday": 0.0,
            "by_atelier": [],
            "by_type_materiel": [],
            "by_technicien": [],
            "records": [],
        }
    
    # Calcul basé sur les OR uniques (pas les lignes)
    # Pour chaque OR, déterminer son statut : si au moins une ligne est "Inspecté", l'OR est considéré comme inspecté
    or_status = df_with_or.groupby("or_segment").agg({
        "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
    }).reset_index()
    
    # Nombre total d'OR uniques facturés dans le trimestre
    total_or = len(or_status)
    
    # Nombre d'OR avec au moins une ligne "Inspecté"
    inspected_or = len(or_status[or_status["is_inspected"] == "Inspecté"])
    
    # Nombre d'OR non inspectés
    not_inspected_or = total_or - inspected_or
    
    # Taux d'inspection = (OR Inspectés / Total OR) * 100
    inspection_rate = (inspected_or / total_or * 100) if total_or > 0 else 0.0
    
    # Calcul du delta hebdomadaire si last_wednesday est fourni
    delta_weekly = 0.0
    inspection_rate_last_wednesday = 0.0
    if last_wednesday:
        df_last = _load_inspection_from_db(start_date, last_wednesday)
        if df_last is not None and not df_last.empty:
            df_last_with_or = df_last[df_last["or_segment"].notna() & (df_last["or_segment"].astype(str).str.strip() != "")]
            if not df_last_with_or.empty:
                or_status_last = df_last_with_or.groupby("or_segment").agg({
                    "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
                }).reset_index()
                total_or_last = len(or_status_last)
                inspected_or_last = len(or_status_last[or_status_last["is_inspected"] == "Inspecté"])
                inspection_rate_last_wednesday = (inspected_or_last / total_or_last * 100) if total_or_last > 0 else 0.0
                delta_weekly = inspection_rate - inspection_rate_last_wednesday
    
    # Pour les statistiques par atelier et type, on utilise toujours les lignes (pas les OR uniques)
    # car on veut voir la répartition des inspections par atelier/type
    total_lines = len(df)
    inspected_lines = len(df[df["is_inspected"] == "Inspecté"])
    not_inspected_lines = len(df[df["is_inspected"] == "Non Inspecté"])
    
    # Par atelier - basé sur les OR uniques par atelier
    by_atelier = []
    if "atelier" in df_with_or.columns and not df_with_or["atelier"].isna().all():
        # Pour chaque atelier, compter les OR uniques inspectés vs total
        atelier_or_stats = df_with_or.groupby(["atelier", "or_segment"]).agg({
            "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
        }).reset_index()
        
        atelier_stats = atelier_or_stats.groupby("atelier").agg({
            "or_segment": "count",  # Total OR par atelier
            "is_inspected": lambda x: (x == "Inspecté").sum(),  # OR inspectés par atelier
        }).reset_index()
        atelier_stats.columns = ["atelier", "total", "inspected"]
        atelier_stats["rate"] = (atelier_stats["inspected"] / atelier_stats["total"] * 100).round(2)
        by_atelier = atelier_stats.fillna("").to_dict(orient="records")
    
    # Par type de matériel - basé sur les OR uniques par type
    by_type_materiel = []
    if "type_materiel" in df_with_or.columns and not df_with_or["type_materiel"].isna().all():
        # Pour chaque type, compter les OR uniques inspectés vs total
        type_or_stats = df_with_or.groupby(["type_materiel", "or_segment"]).agg({
            "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté"
        }).reset_index()
        
        type_stats = type_or_stats.groupby("type_materiel").agg({
            "or_segment": "count",  # Total OR par type
            "is_inspected": lambda x: (x == "Inspecté").sum(),  # OR inspectés par type
        }).reset_index()
        type_stats.columns = ["type_materiel", "total", "inspected"]
        type_stats["rate"] = (type_stats["inspected"] / type_stats["total"] * 100).round(2)
        by_type_materiel = type_stats.fillna("").to_dict(orient="records")
    
    # Analyse par technicien - basé sur les OR uniques par technicien
    by_technicien = []
    if "technicien" in df_with_or.columns and not df_with_or["technicien"].isna().all():
        # Filtrer les lignes avec technicien valide
        df_with_tech = df_with_or[df_with_or["technicien"].notna() & (df_with_or["technicien"].astype(str).str.strip() != "")]
        
        if not df_with_tech.empty:
            # Pour chaque technicien, compter les OR uniques qu'il a traités
            tech_or_stats = df_with_tech.groupby(["technicien", "or_segment"]).agg({
                "is_inspected": lambda x: "Inspecté" if (x == "Inspecté").any() else "Non Inspecté",
                "equipe": "first",  # Prendre la première équipe pour ce technicien/OR
            }).reset_index()
            
            tech_stats = tech_or_stats.groupby("technicien").agg({
                "or_segment": "count",  # Total OR traités par technicien
                "is_inspected": lambda x: (x == "Inspecté").sum(),  # OR inspectés par technicien
                "equipe": "first",  # Équipe du technicien
            }).reset_index()
            tech_stats.columns = ["technicien", "total_or", "inspected_or", "equipe"]
            tech_stats["rate"] = (tech_stats["inspected_or"] / tech_stats["total_or"] * 100).round(2)
            tech_stats = tech_stats.sort_values("rate", ascending=False)
            by_technicien = tech_stats.fillna("").to_dict(orient="records")
    
    # Limiter les records à 100 pour la réponse
    records = df.head(100).to_dict(orient="records")
    
    return {
        "total": total_or,  # Nombre total d'OR uniques
        "inspected": inspected_or,  # Nombre d'OR inspectés
        "not_inspected": not_inspected_or,  # Nombre d'OR non inspectés
        "total_lines": total_lines,  # Nombre total de lignes (pour référence)
        "inspected_lines": inspected_lines,  # Nombre de lignes inspectées (pour référence)
        "not_inspected_lines": not_inspected_lines,  # Nombre de lignes non inspectées (pour référence)
        "inspection_rate": round(inspection_rate, 2),
        "delta_weekly": round(delta_weekly, 2),
        "inspection_rate_last_wednesday": round(inspection_rate_last_wednesday, 2),
        "by_atelier": by_atelier,
        "by_type_materiel": by_type_materiel,
        "by_technicien": by_technicien,
        "records": records,
    }


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


def _build_exhaustivity(df: pd.DataFrame, month: str | None = None, team: str | None = None) -> dict:
    # Calculer les périodes AVANT de filtrer pour avoir tous les mois disponibles
    periods = sorted(df["mois_period"].unique()) if not df.empty else []
    
    target_df = df
    if month:
        target_df = target_df[target_df["mois_period"] == month]

    exhaustivity = {"periods": periods, "statuts": {}, "heures": {}, "teams": {}}

    if target_df.empty:
        return exhaustivity

    if team:
        target_df = target_df[target_df["Salarié - Equipe(Nom)"] == team]

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

    agg = (
        target_df.groupby(
            ["Salarié - Nom", "Salarié - Equipe(Nom)", "jour", "weekday"],
            as_index=False,
        )
        .agg(heures=("heures_travaillees", "sum"))
    )
    agg["statut"] = agg.apply(lambda r: statut_pointage(r["heures"], r["weekday"]), axis=1)

    for _, r in agg.iterrows():
        tech = r["Salarié - Nom"]
        day = str(int(r["jour"]))
        exhaustivity["statuts"].setdefault(tech, {})[day] = r["statut"]
        exhaustivity["heures"].setdefault(tech, {})[day] = float(r["heures"])
        exhaustivity["teams"][tech] = r["Salarié - Equipe(Nom)"]

    return exhaustivity


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


@app.get("/kpi/productivite/debug")
async def debug_productivity():
    """Endpoint de debug pour inspecter les données et calculs"""
    global LATEST_PRODUCTIVITY_DF
    
    db_df = _load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
        source = "database"
    elif LATEST_PRODUCTIVITY_DF is not None and not LATEST_PRODUCTIVITY_DF.empty:
        df = LATEST_PRODUCTIVITY_DF.copy()
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


@app.get("/kpi/productivite/analytics")
async def get_productivity():
    global LATEST_PRODUCTIVITY_DF

    db_df = _load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
    elif LATEST_PRODUCTIVITY_DF is not None and not LATEST_PRODUCTIVITY_DF.empty:
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
    monthly_agg = (
        df.groupby(["month_num", "mois"])
        .agg(
            facturable=("Facturable", "sum"),
            heures=("heures_travaillees", "sum")
        )
        .reset_index()
    )
    monthly_agg["productivite"] = (
        monthly_agg["facturable"] / monthly_agg["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    monthly = monthly_agg.sort_values("month_num")[["mois", "productivite"]]

    # =========================
    # TECHNICIENS / ÉQUIPES
    # =========================
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
    technicians = tech_agg.sort_values("productivite", ascending=False)[["Salarié - Nom", "productivite"]]

    team_agg = (
        df.groupby("Salarié - Equipe(Nom)")
        .agg(
            facturable=("Facturable", "sum"),
            heures=("heures_travaillees", "sum")
        )
        .reset_index()
    )
    team_agg["productivite"] = (
        team_agg["facturable"] / team_agg["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    teams = team_agg[["Salarié - Equipe(Nom)", "productivite"]]

    # =========================
    # CORRÉLATION ÉQUIPES
    # =========================
    # Calculer la productivité mensuelle globale avec sum/sum
    monthly_agg_corr = (
        df.groupby("mois")
        .agg(
            facturable=("Facturable", "sum"),
            heures=("heures_travaillees", "sum")
        )
    )
    monthly_avg = (
        monthly_agg_corr["facturable"] / monthly_agg_corr["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    # Calculer la productivité par équipe/mois avec sum/sum
    team_month_agg = (
        df.groupby(["mois", "Salarié - Equipe(Nom)"])
        .agg(
            facturable=("Facturable", "sum"),
            heures=("heures_travaillees", "sum")
        )
        .reset_index()
    )
    team_month_agg["productivite"] = (
        team_month_agg["facturable"] / team_month_agg["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    team_month = team_month_agg[["mois", "Salarié - Equipe(Nom)", "productivite"]]

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
# EXHAUSTIVITÉ DÉDIÉE (FILTRABLE)
# ==================================================
@app.get("/kpi/productivite/exhaustivite")
async def get_exhaustivite(month: str | None = None, team: str | None = None):
    db_df = _load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
    elif LATEST_PRODUCTIVITY_DF is not None and not LATEST_PRODUCTIVITY_DF.empty:
        df = LATEST_PRODUCTIVITY_DF.copy()
    else:
        raise HTTPException(status_code=400, detail="Aucune donnée chargée. Veuillez importer un fichier.")
    exhaust = _build_exhaustivity(df, month=month, team=team)
    return exhaust


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
        # Pour les fichiers Excel, vérifier s'il y a plusieurs onglets
        if suffix in {".xlsx", ".xls"}:
            excel_file = pd.ExcelFile(buffer)
            sheet_names = excel_file.sheet_names
            
            # Chercher l'onglet de productivité (premier onglet ou celui avec les colonnes attendues)
            df = None
            inspection_df = None
            
            for sheet_name in sheet_names:
                sheet_df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # Vérifier si c'est un onglet de productivité
                if {"Saisie heures - Date", "Salarié - Nom", "Facturable"}.issubset(set(sheet_df.columns)):
                    df = sheet_df
                # Vérifier si c'est un onglet d'inspection
                elif {"sn", "date_facture", "is_inspected"}.issubset(set(sheet_df.columns)) or \
                     {"SN", "Date Facture", "Is Inspected"}.issubset(set(sheet_df.columns)):
                    inspection_df = sheet_df
            
            # Si pas trouvé, prendre le premier onglet comme productivité
            if df is None and sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_names[0])
        else:
            # Pour CSV, on ne peut traiter qu'un seul type à la fois
            df = pd.read_csv(buffer)
            inspection_df = None
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erreur lecture fichier: {str(exc)}")

    # Traiter les données de productivité
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

    # Vérifier que la colonne Hr_Totale est présente
    if "Hr_Totale" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="Colonne Hr_Totale manquante (obligatoire)",
        )

    df_prepared = _prepare_productivity_df(df)

    # Vérifier si la colonne "OR (Numéro)" existe
    or_col = None
    for col in df_prepared.columns:
        if "or" in col.lower() and ("numéro" in col.lower() or "numero" in col.lower()):
            or_col = col
            break
    
    # Agrégation par technicien / jour
    groupby_cols = ["Saisie heures - Date", "Salarié - Nom", "Salarié - Equipe(Nom)"]
    if or_col:
        groupby_cols.append(or_col)
    
    grouped = (
        df_prepared.groupby(groupby_cols, as_index=False)
        .agg(
            facturable=("Facturable", "sum"),
            heures_total=("heures_travaillees", "sum"),
        )
    )

    rows = []
    for _, r in grouped.iterrows():
        rows.append((
            r["Saisie heures - Date"].date(),
            r["Salarié - Nom"],
            r["Salarié - Equipe(Nom)"],
            float(r["facturable"]),
            float(r["heures_total"]),
            str(r.get(or_col, "")) if or_col else None,
        ))

    ensure_schema()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(POINTAGE_SCHEMA)
            cur.executemany(
                """
                INSERT INTO pointage (jour, technicien, equipe, facturable, heures_total, or_numero)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (technicien, jour)
                DO UPDATE SET
                    equipe = EXCLUDED.equipe,
                    facturable = EXCLUDED.facturable,
                    heures_total = EXCLUDED.heures_total,
                    or_numero = EXCLUDED.or_numero,
                    inserted_at = now();
                """,
                rows,
            )
        conn.commit()

    global LATEST_PRODUCTIVITY_DF
    LATEST_PRODUCTIVITY_DF = df_prepared

    # Traiter les données d'inspection si présentes
    inspection_rows = 0
    if inspection_df is not None:
        try:
            # Normaliser les noms de colonnes (insensible à la casse)
            inspection_df.columns = inspection_df.columns.str.strip()
            col_mapping = {}
            for col in inspection_df.columns:
                col_lower = col.lower()
                if "sn" in col_lower or "serial" in col_lower:
                    col_mapping[col] = "sn"
                elif "date" in col_lower and "facture" in col_lower:
                    col_mapping[col] = "date_facture"
                elif "inspect" in col_lower:
                    col_mapping[col] = "is_inspected"
                elif "or" in col_lower and "segment" in col_lower:
                    col_mapping[col] = "or_segment"
                elif "type" in col_lower and "materiel" in col_lower:
                    col_mapping[col] = "type_materiel"
                elif "atelier" in col_lower:
                    col_mapping[col] = "atelier"
            
            inspection_df = inspection_df.rename(columns=col_mapping)
            
            # Normaliser les données
            inspection_df["date_facture"] = pd.to_datetime(inspection_df["date_facture"], errors="coerce")
            inspection_df = inspection_df.dropna(subset=["date_facture", "sn"])
            inspection_df["is_inspected"] = inspection_df["is_inspected"].astype(str).str.strip()
            
            # Préparer les données pour insertion
            inspection_rows_data = []
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for _, row in inspection_df.iterrows():
                        or_segment = str(row.get("or_segment", "") or "").strip()
                        technicien = None
                        equipe = None
                        
                        # Chercher le technicien avec le plus d'heures sur l'OR
                        if or_segment:
                            cur.execute(
                                """
                                SELECT technicien, equipe, SUM(heures_total) as total_heures
                                FROM pointage
                                WHERE or_numero = %s OR or_numero LIKE %s
                                GROUP BY technicien, equipe
                                ORDER BY total_heures DESC
                                LIMIT 1
                                """,
                                (or_segment, f"%{or_segment}%"),
                            )
                            result = cur.fetchone()
                            if result:
                                technicien = result[0]
                                equipe = result[1]
                        
                        inspection_rows_data.append((
                            str(row["sn"]),
                            or_segment,
                            str(row.get("type_materiel", "") or ""),
                            str(row.get("atelier", "") or ""),
                            row["date_facture"].date(),
                            str(row["is_inspected"]),
                            technicien,
                            equipe,
                        ))
            
            # Insérer les données d'inspection
            if inspection_rows_data:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.executemany(
                            """
                            INSERT INTO inspection_record (sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (sn, date_facture)
                            DO UPDATE SET
                                or_segment = EXCLUDED.or_segment,
                                type_materiel = EXCLUDED.type_materiel,
                                atelier = EXCLUDED.atelier,
                                is_inspected = EXCLUDED.is_inspected,
                                technicien = EXCLUDED.technicien,
                                equipe = EXCLUDED.equipe,
                                inserted_at = now();
                            """,
                            inspection_rows_data,
                        )
                    conn.commit()
                inspection_rows = len(inspection_rows_data)
        except Exception as exc:
            # Ne pas faire échouer l'upload de productivité si l'inspection échoue
            print(f"⚠️ Erreur traitement inspection: {exc}")

    return {
        "message": "Données agrégées et sauvegardées en base (1 ligne par technicien/jour)",
        "kpi": {
            "rows": len(grouped),
            "columns": list(df_prepared.columns),
            "role": user["role"],
            "owner": user["email"],
        },
        "inspection": {
            "rows": inspection_rows,
            "processed": inspection_df is not None,
        } if inspection_df is not None else None,
    }


# ==================================================
# KPI INSPECTION RATE
# ==================================================
@app.post("/kpi/inspection/upload")
async def upload_inspection(request: Request, file: UploadFile = File(...)):
    """Upload des données d'inspection"""
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

    # Colonnes requises
    required = {"sn", "date_facture", "is_inspected"}
    if not required.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes: {required - set(df.columns)}",
        )

    # Normaliser les colonnes optionnelles
    df["or_segment"] = df.get("or_segment", "")
    df["type_materiel"] = df.get("type_materiel", "")
    df["atelier"] = df.get("atelier", "")

    # Normaliser date_facture
    df["date_facture"] = pd.to_datetime(df["date_facture"], errors="coerce")
    df = df.dropna(subset=["date_facture"])

    # Normaliser is_inspected
    df["is_inspected"] = df["is_inspected"].astype(str).str.strip()
    # Valider que les valeurs sont correctes
    valid_values = {"Inspecté", "Non Inspecté"}
    invalid = set(df["is_inspected"].unique()) - valid_values
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Valeurs invalides pour is_inspected: {invalid}. Valeurs attendues: {valid_values}",
        )

    # Pour chaque ligne, chercher le technicien avec le plus d'heures sur l'OR
    ensure_schema()
    rows = []
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                or_segment = str(row.get("or_segment", "") or "").strip()
                technicien = None
                equipe = None
                
                # Si on a un OR segment, chercher le technicien avec le plus d'heures
                if or_segment:
                    cur.execute(
                        """
                        SELECT technicien, equipe, SUM(heures_total) as total_heures
                        FROM pointage
                        WHERE or_numero = %s OR or_numero LIKE %s
                        GROUP BY technicien, equipe
                        ORDER BY total_heures DESC
                        LIMIT 1
                        """,
                        (or_segment, f"%{or_segment}%"),
                    )
                    result = cur.fetchone()
                    if result:
                        technicien = result[0]
                        equipe = result[1]
                
                rows.append((
                    str(row["sn"]),
                    or_segment,
                    str(row.get("type_materiel", "") or ""),
                    str(row.get("atelier", "") or ""),
                    row["date_facture"].date(),
                    str(row["is_inspected"]),
                    technicien,
                    equipe,
                ))

    # Insérer en base
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO inspection_record (sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sn, date_facture)
                DO UPDATE SET
                    or_segment = EXCLUDED.or_segment,
                    type_materiel = EXCLUDED.type_materiel,
                    atelier = EXCLUDED.atelier,
                    is_inspected = EXCLUDED.is_inspected,
                    technicien = EXCLUDED.technicien,
                    equipe = EXCLUDED.equipe,
                    inserted_at = now();
                """,
                rows,
            )
        conn.commit()

    return {"message": "Données d'inspection enregistrées", "rows": len(rows)}


@app.get("/kpi/inspection/analytics")
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

    # Calculer la date du mercredi dernier (pour le delta hebdomadaire)
    today = date.today()
    # weekday(): 0 = lundi, 1 = mardi, 2 = mercredi, 3 = jeudi, 4 = vendredi, 5 = samedi, 6 = dimanche
    current_weekday = today.weekday()
    
    if current_weekday == 2:  # Si on est mercredi
        # Le mercredi dernier est il y a 7 jours
        last_wednesday = today - pd.Timedelta(days=7)
    elif current_weekday > 2:  # Jeudi, vendredi, samedi, dimanche
        # Le mercredi dernier est dans la semaine actuelle
        days_back = current_weekday - 2
        last_wednesday = today - pd.Timedelta(days=days_back)
    else:  # Lundi ou mardi
        # Le mercredi dernier est la semaine dernière
        days_back = 7 - (2 - current_weekday)
        last_wednesday = today - pd.Timedelta(days=days_back)

    # Utiliser la fonction utilitaire commune pour calculer les analytics
    analytics = _calculate_inspection_analytics(start_date, end_date, last_wednesday, team)
    
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


@app.get("/kpi/inspection/snapshot")
async def get_inspection_snapshot(request: Request):
    """Retourne un snapshot des KPIs d'inspection pour le trimestre actuel (utilisé par KpiSnapshot et CR)"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    # Calculer le trimestre actuel
    start_date, end_date = get_current_quarter_dates()
    today = date.today()
    current_weekday = today.weekday()
    
    # Calculer le mercredi dernier
    if current_weekday == 2:
        last_wednesday = today - pd.Timedelta(days=7)
    elif current_weekday > 2:
        days_back = current_weekday - 2
        last_wednesday = today - pd.Timedelta(days=days_back)
    else:
        days_back = 7 - (2 - current_weekday)
        last_wednesday = today - pd.Timedelta(days=days_back)
    
    # Utiliser la fonction utilitaire commune
    analytics = _calculate_inspection_analytics(start_date, end_date, last_wednesday)
    
    return {
        "inspection_rate": analytics["inspection_rate"],
        "delta_weekly": analytics["delta_weekly"],
        "total": analytics["total"],
        "inspected": analytics["inspected"],
        "not_inspected": analytics["not_inspected"],
    }


@app.get("/kpi/inspection/quarters")
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


@app.get("/kpi/inspection/teams")
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


@app.get("/kpi/inspection/history")
async def get_inspection_history(request: Request):
    """Retourne l'historique trimestriel (Q actuel, Q-1, Q-2, Q-3) pour visualisation"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    today = date.today()
    current_year = today.year
    current_quarter = (today.month - 1) // 3 + 1
    
    history = []
    
    # Calculer les 4 trimestres (Q actuel + 3 précédents)
    for i in range(4):
        q = current_quarter - i
        y = current_year
        
        # Gérer le passage d'année
        while q <= 0:
            q += 4
            y -= 1
        
        start_date, end_date = get_quarter_dates(y, q)
        analytics = _calculate_inspection_analytics(start_date, end_date, None)
        
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


# ==================================================
# LEAN ACTION ENDPOINTS
# ==================================================
@app.get("/api/lean-actions")
async def get_lean_actions(request: Request):
    """Récupère toutes les actions lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes, 
                           created_at, updated_at
                    FROM lean_action
                    ORDER BY date_ouverture DESC, id DESC
                """)
                rows = cur.fetchall()
                actions = [
                    {
                        "id": r[0],
                        "date_ouverture": r[1].isoformat() if r[1] else None,
                        "date_cloture_prevue": r[2].isoformat() if r[2] else None,
                        "probleme": r[3],
                        "owner": r[4],
                        "statut": r[5],
                        "notes": r[6],
                        "created_at": r[7].isoformat() if r[7] else None,
                        "updated_at": r[8].isoformat() if r[8] else None,
                    }
                    for r in rows
                ]
        return {"actions": actions}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {exc}")


@app.post("/api/lean-actions")
async def create_lean_action(request: Request, action: Dict[str, Any]):
    """Crée une nouvelle action lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    probleme = action.get("probleme", "").strip()
    if not probleme:
        raise HTTPException(status_code=400, detail="Le problème est obligatoire")
    
    owner = action.get("owner", email).strip() or email
    date_ouverture = action.get("date_ouverture")
    date_cloture_prevue = action.get("date_cloture_prevue")
    statut = action.get("statut", "Ouvert")
    notes = action.get("notes", "").strip()
    
    if statut not in ["Ouvert", "Clôturé"]:
        statut = "Ouvert"
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lean_action 
                    (date_ouverture, date_cloture_prevue, probleme, owner, statut, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes, 
                              created_at, updated_at
                """, (date_ouverture, date_cloture_prevue, probleme, owner, statut, notes))
                row = cur.fetchone()
                conn.commit()
                return {
                    "id": row[0],
                    "date_ouverture": row[1].isoformat() if row[1] else None,
                    "date_cloture_prevue": row[2].isoformat() if row[2] else None,
                    "probleme": row[3],
                    "owner": row[4],
                    "statut": row[5],
                    "notes": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None,
                }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {exc}")


@app.put("/api/lean-actions/{action_id}")
async def update_lean_action(request: Request, action_id: int, action: Dict[str, Any]):
    """Met à jour une action lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    updates = []
    params = []
    
    if "date_cloture_prevue" in action:
        updates.append("date_cloture_prevue = %s")
        params.append(action["date_cloture_prevue"])
    
    if "probleme" in action:
        updates.append("probleme = %s")
        params.append(action["probleme"].strip())
    
    if "owner" in action:
        updates.append("owner = %s")
        params.append(action["owner"].strip())
    
    if "statut" in action:
        statut = action["statut"]
        if statut in ["Ouvert", "Clôturé"]:
            updates.append("statut = %s")
            params.append(statut)
    
    if "notes" in action:
        updates.append("notes = %s")
        params.append(action["notes"].strip())
    
    if not updates:
        raise HTTPException(status_code=400, detail="Aucune modification fournie")
    
    updates.append("updated_at = now()")
    params.append(action_id)
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE lean_action
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes,
                              created_at, updated_at
                """, params)
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Action non trouvée")
                conn.commit()
                return {
                    "id": row[0],
                    "date_ouverture": row[1].isoformat() if row[1] else None,
                    "date_cloture_prevue": row[2].isoformat() if row[2] else None,
                    "probleme": row[3],
                    "owner": row[4],
                    "statut": row[5],
                    "notes": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None,
                }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {exc}")


@app.delete("/api/lean-actions/{action_id}")
async def delete_lean_action(request: Request, action_id: int):
    """Supprime une action lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM lean_action WHERE id = %s RETURNING id", (action_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Action non trouvée")
                conn.commit()
        return {"message": "Action supprimée", "id": action_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {exc}")


# ==================================================
# COMPTES RENDUS (CR) - Génération automatique
# ==================================================
def generate_meeting_summary(meeting_date: date | None = None) -> Dict[str, Any]:
    """Génère un snapshot des KPIs et actions pour une réunion (utilise la logique commune)"""
    if meeting_date is None:
        meeting_date = date.today()
    
    # Charger les données de productivité
    db_df = _load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
    elif LATEST_PRODUCTIVITY_DF is not None and not LATEST_PRODUCTIVITY_DF.empty:
        df = LATEST_PRODUCTIVITY_DF.copy()
    else:
        return {
            "error": "Aucune donnée disponible",
            "meeting_date": meeting_date.isoformat(),
        }
    
    # Calculer les KPIs globaux
    total_hours = float(df["heures_travaillees"].sum())
    total_fact = float(df["Facturable"].sum())
    global_prod = total_fact / total_hours if total_hours else 0.0
    
    # Calculer les KPIs d'inspection (utilise la fonction commune)
    start_date, end_date = get_current_quarter_dates()
    today = date.today()
    current_weekday = today.weekday()
    
    # Calculer le mercredi dernier
    if current_weekday == 2:
        last_wednesday = today - pd.Timedelta(days=7)
    elif current_weekday > 2:
        days_back = current_weekday - 2
        last_wednesday = today - pd.Timedelta(days=days_back)
    else:
        days_back = 7 - (2 - current_weekday)
        last_wednesday = today - pd.Timedelta(days=days_back)
    
    inspection_analytics = _calculate_inspection_analytics(start_date, end_date, last_wednesday)
    
    # Récupérer les actions ouvertes et critiques
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) as ouvertes,
                           COUNT(*) FILTER (WHERE statut = 'Ouvert' AND date_cloture_prevue < CURRENT_DATE) as critiques
                    FROM lean_action
                    WHERE statut = 'Ouvert'
                """)
                row = cur.fetchone()
                actions_ouvertes = row[0] if row else 0
                actions_critiques = row[1] if row else 0
    except Exception:
        actions_ouvertes = 0
        actions_critiques = 0
    
    return {
        "meeting_date": meeting_date.isoformat(),
        "productivite_globale": round(global_prod * 100, 2),
        "total_heures": round(total_hours, 2),
        "total_facturable": round(total_fact, 2),
        "inspection_rate": inspection_analytics["inspection_rate"],
        "inspection_delta_weekly": inspection_analytics["delta_weekly"],
        "actions_ouvertes": actions_ouvertes,
        "actions_critiques": actions_critiques,
    }


def create_pdf_summary(summary_data: Dict[str, Any], actions: List[Dict[str, Any]], notes: str = "") -> BytesIO:
    """Crée un PDF structuré du compte rendu"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FFD700'),
        spaceAfter=30,
        alignment=1,  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#000000'),
        spaceAfter=12,
    )
    
    # Titre
    story.append(Paragraph("COMPTE RENDU RÉUNION SEP", title_style))
    story.append(Paragraph(f"Date : {summary_data.get('meeting_date', date.today().isoformat())}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Résumé de performance
    prod = summary_data.get('productivite_globale', 0)
    status = "Conforme" if prod >= 85 else "À améliorer" if prod >= 78 else "Non conforme"
    story.append(Paragraph("RÉSUMÉ DE PERFORMANCE", heading_style))
    story.append(Paragraph(
        f"Productivité Atelier : <b>{prod}%</b> - {status} aux objectifs SEP 2025",
        styles['Normal']
    ))
    story.append(Paragraph(
        f"Heures totales : {summary_data.get('total_heures', 0):.0f}h | Facturable : {summary_data.get('total_facturable', 0):.0f}h",
        styles['Normal']
    ))
    
    # Inspection Rate avec badge CAT
    inspection_rate = summary_data.get('inspection_rate', 0)
    inspection_delta = summary_data.get('inspection_delta_weekly', 0)
    if inspection_rate > 0:
        delta_text = f" ({inspection_delta:+.1f}% vs mercredi dernier)" if inspection_delta != 0 else ""
        # Déterminer le badge CAT selon les seuils (≥65% Vert, 50-64% Orange, <50% Rouge)
        if inspection_rate >= 65:
            cat_status = "Excellent (≥65%)"
        elif inspection_rate >= 50:
            cat_status = "Alerte (50-64%)"
        else:
            cat_status = "Critique (<50%)"
        
        story.append(Paragraph(
            f"Inspection Rate : <b>{inspection_rate:.1f}%</b> - <b>{cat_status}</b>{delta_text}",
            styles['Normal']
        ))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Tableau des actions
    story.append(Paragraph("ACTIONS LEAN", heading_style))
    
    # Actions ouvertes
    ouvertes = [a for a in actions if a.get('statut') == 'Ouvert']
    if ouvertes:
        # Créer un style pour les cellules de problème (texte qui wrap)
        problem_style = ParagraphStyle(
            'ProblemStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            wordWrap='LTR',
        )
        
        data = [[
            Paragraph('<b>ID</b>', styles['Normal']),
            Paragraph('<b>Date ouverture</b>', styles['Normal']),
            Paragraph('<b>Problème</b>', styles['Normal']),
            Paragraph('<b>Owner</b>', styles['Normal']),
            Paragraph('<b>Date clôture prévue</b>', styles['Normal']),
        ]]
        for a in ouvertes:
            probleme_text = a.get('probleme', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            data.append([
                str(a.get('id', '')),
                a.get('date_ouverture', ''),
                Paragraph(probleme_text, problem_style),
                a.get('owner', ''),
                a.get('date_cloture_prevue', '') or '-',
            ])
        
        table = Table(data, colWidths=[0.5*inch, 1*inch, 3.5*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFD700')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFFACD')]),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Aucune action ouverte.", styles['Normal']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Actions critiques
    critiques = [a for a in ouvertes if a.get('date_cloture_prevue') and datetime.fromisoformat(a['date_cloture_prevue']).date() < date.today()]
    if critiques:
        story.append(Paragraph("ACTIONS CRITIQUES (en retard)", heading_style))
        
        # Créer un style pour les cellules de problème (texte qui wrap)
        problem_style = ParagraphStyle(
            'ProblemStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            wordWrap='LTR',
        )
        
        data = [[
            Paragraph('<b>ID</b>', styles['Normal']),
            Paragraph('<b>Problème</b>', styles['Normal']),
            Paragraph('<b>Owner</b>', styles['Normal']),
            Paragraph('<b>Date clôture prévue</b>', styles['Normal']),
        ]]
        for a in critiques:
            probleme_text = a.get('probleme', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            data.append([
                str(a.get('id', '')),
                Paragraph(probleme_text, problem_style),
                a.get('owner', ''),
                a.get('date_cloture_prevue', ''),
            ])
        
        table = Table(data, colWidths=[0.5*inch, 4*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFE4E1')]),
        ]))
        story.append(table)
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Notes de discussion
    if notes:
        story.append(Paragraph("NOTES DE DISCUSSION", heading_style))
        story.append(Paragraph(notes.replace('\n', '<br/>'), styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


@app.post("/api/meeting-summary/generate")
async def generate_cr(request: Request):
    """Génère un compte rendu de réunion (snapshot + PDF)"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        payload = await request.json()
    except:
        payload = {}
    
    try:
        # Générer le snapshot
        meeting_date = date.today()
        if payload.get("meeting_date"):
            meeting_date = datetime.fromisoformat(payload["meeting_date"]).date()
        
        summary = generate_meeting_summary(meeting_date)
        if "error" in summary:
            raise HTTPException(status_code=400, detail=summary["error"])
        
        # Récupérer les actions
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes
                    FROM lean_action
                    ORDER BY date_ouverture DESC
                """)
                rows = cur.fetchall()
                actions = [
                    {
                        "id": r[0],
                        "date_ouverture": r[1].isoformat() if r[1] else None,
                        "date_cloture_prevue": r[2].isoformat() if r[2] else None,
                        "probleme": r[3],
                        "owner": r[4],
                        "statut": r[5],
                        "notes": r[6],
                    }
                    for r in rows
                ]
        
        # Créer le PDF
        notes_discussion = payload.get("notes_discussion", "")
        pdf_buffer = create_pdf_summary(summary, actions, notes_discussion)
        
        # Sauvegarder en base
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO meeting_summary 
                    (meeting_date, productivite_globale, total_heures, total_facturable, 
                     actions_ouvertes, actions_critiques, notes_discussion, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    meeting_date,
                    summary["productivite_globale"],
                    summary["total_heures"],
                    summary["total_facturable"],
                    summary["actions_ouvertes"],
                    summary["actions_critiques"],
                    notes_discussion,
                    email,
                ))
                cr_id = cur.fetchone()[0]
                conn.commit()
        
        # Retourner le PDF
        pdf_buffer.seek(0)
        return StreamingResponse(
            BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=CR_SEP_{meeting_date.isoformat()}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {exc}")


@app.get("/api/meeting-summary/list")
async def list_cr(request: Request):
    """Liste tous les comptes rendus générés"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, meeting_date, productivite_globale, total_heures, total_facturable,
                           actions_ouvertes, actions_critiques, created_by, created_at
                    FROM meeting_summary
                    ORDER BY meeting_date DESC, created_at DESC
                """)
                rows = cur.fetchall()
                summaries = [
                    {
                        "id": r[0],
                        "meeting_date": r[1].isoformat() if r[1] else None,
                        "productivite_globale": float(r[2]) if r[2] else 0,
                        "total_heures": float(r[3]) if r[3] else 0,
                        "total_facturable": float(r[4]) if r[4] else 0,
                        "actions_ouvertes": r[5],
                        "actions_critiques": r[6],
                        "created_by": r[7],
                        "created_at": r[8].isoformat() if r[8] else None,
                    }
                    for r in rows
                ]
        return {"summaries": summaries}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {exc}")


@app.get("/api/meeting-summary/{cr_id}/download")
async def download_cr(request: Request, cr_id: int):
    """Télécharge un compte rendu PDF (re-génère depuis les données)"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        # Récupérer les données du CR
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT meeting_date, notes_discussion
                    FROM meeting_summary
                    WHERE id = %s
                """, (cr_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Compte rendu non trouvé")
                meeting_date = row[0]
                notes = row[1] or ""
        
        # Régénérer le snapshot et le PDF
        summary = generate_meeting_summary(meeting_date)
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes
                    FROM lean_action
                    ORDER BY date_ouverture DESC
                """)
                rows = cur.fetchall()
                actions = [
                    {
                        "id": r[0],
                        "date_ouverture": r[1].isoformat() if r[1] else None,
                        "date_cloture_prevue": r[2].isoformat() if r[2] else None,
                        "probleme": r[3],
                        "owner": r[4],
                        "statut": r[5],
                        "notes": r[6],
                    }
                    for r in rows
                ]
        
        pdf_buffer = create_pdf_summary(summary, actions, notes)
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=CR_SEP_{meeting_date.isoformat()}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement: {exc}")
