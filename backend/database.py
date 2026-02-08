"""Gestion de la base de données et schémas"""
from fastapi import HTTPException
import psycopg
from config import DATABASE_URL

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
    markdown_content text,
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

LLTI_RECORD_SCHEMA = """
CREATE TABLE IF NOT EXISTS llti_record (
    id SERIAL PRIMARY KEY,
    or_segment text NOT NULL,
    numero_facture text NOT NULL,
    date_facture date NOT NULL,
    date_pointage date NOT NULL,
    client text,
    sn_equipement text,
    constructeur text,
    llti_jours numeric NOT NULL,
    inserted_at timestamp without time zone DEFAULT now(),
    CONSTRAINT llti_record_facture_unique UNIQUE (numero_facture)
);
"""


def get_conn():
    """Retourne une connexion à la base de données"""
    try:
        return psycopg.connect(DATABASE_URL)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {exc}") from exc


def ensure_schema():
    """Crée les tables si elles n'existent pas"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(POINTAGE_SCHEMA)
            cur.execute(LEAN_ACTION_SCHEMA)
            cur.execute(MEETING_SUMMARY_SCHEMA)
            cur.execute(INSPECTION_RECORD_SCHEMA)
            cur.execute(LLTI_RECORD_SCHEMA)
            
            # Migration : Ajouter la colonne markdown_content si elle n'existe pas
            try:
                cur.execute("""
                    ALTER TABLE meeting_summary 
                    ADD COLUMN IF NOT EXISTS markdown_content text
                """)
            except Exception:
                pass  # La colonne existe déjà ou erreur de migration
            
            # Migration : Supprimer l'ancienne colonne pdf_path si elle existe
            try:
                cur.execute("""
                    ALTER TABLE meeting_summary 
                    DROP COLUMN IF EXISTS pdf_path
                """)
            except Exception:
                pass  # La colonne n'existe pas ou erreur de migration
        conn.commit()

