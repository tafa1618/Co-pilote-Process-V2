"""Configuration et constantes de l'application"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ADMIN_EMAIL = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or ""
ENV = os.environ.get("ENV", "dev")

# Default to localhost for local development (use 'db' in docker-compose)
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5432/kpi_db"

print(f"🔍 [DEBUG] DATABASE_URL: {DATABASE_URL}")  # Temporary debug

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

