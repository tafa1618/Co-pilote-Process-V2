"""Configuration et constantes de l'application"""
import os

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

# Liste des emails autorisés pour accéder à SuiviSepMeeting
ALLOWED_ADMINS = [
    ADMIN_EMAIL,
]
ALLOWED_ADMINS = [e for e in ALLOWED_ADMINS if e]  # Filtrer les valeurs vides

