"""
Database schema for Productivity KPI tables
Based on productivity_kpi_methodology.md
"""

# SQL Schema for PostgreSQL/SQLite

SCHEMA_SQL = """
-- Table 1: Raw timesheet data (imported from Excel)
CREATE TABLE IF NOT EXISTS pointages_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salarie_numero INTEGER NOT NULL,
    salarie_nom TEXT NOT NULL,
    salarie_equipe_nom TEXT NOT NULL,
    saisie_date DATE NOT NULL,
    or_numero INTEGER,
    type_heure_libelle TEXT,
    heure_realisee REAL,
    facturable REAL,
    non_facturable REAL,
    allouee REAL,
    hr_travaillee REAL,
    hr_totale REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pointages_raw_salarie ON pointages_raw(salarie_numero);
CREATE INDEX IF NOT EXISTS idx_pointages_raw_date ON pointages_raw(saisie_date);
CREATE INDEX IF NOT EXISTS idx_pointages_raw_equipe ON pointages_raw(salarie_equipe_nom);
CREATE INDEX IF NOT EXISTS idx_pointages_raw_or ON pointages_raw(or_numero);

-- Table 2: Daily aggregation (salarie + date)
CREATE TABLE IF NOT EXISTS pointages_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salarie_id INTEGER NOT NULL,
    salarie_nom TEXT NOT NULL,
    equipe TEXT NOT NULL,
    date DATE NOT NULL,
    heures_facturables REAL DEFAULT 0,
    heures_non_facturables REAL DEFAULT 0,
    heures_allouees REAL DEFAULT 0,
    heures_travaillees REAL DEFAULT 0,
    heures_totales REAL DEFAULT 0,
    productivite_pct REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(salarie_id, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_salarie ON pointages_daily(salarie_id);
CREATE INDEX IF NOT EXISTS idx_daily_date ON pointages_daily(date);
CREATE INDEX IF NOT EXISTS idx_daily_equipe ON pointages_daily(equipe);

-- Table 3: Exhaustivity control (daily status)
CREATE TABLE IF NOT EXISTS exhaustivite_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salarie_id INTEGER NOT NULL,
    salarie_nom TEXT NOT NULL,
    equipe TEXT NOT NULL,
    date DATE NOT NULL,
    heures_totales REAL DEFAULT 0,
    jour_semaine INTEGER,  -- 0=Monday, 6=Sunday
    type_jour TEXT CHECK(type_jour IN ('ouvre', 'weekend')),
    statut_exhaustivite TEXT CHECK(statut_exhaustivite IN ('VERT', 'ORANGE', 'ROUGE', 'BLEU')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(salarie_id, date)
);

CREATE INDEX IF NOT EXISTS idx_exhaustivite_date ON exhaustivite_daily(date);
CREATE INDEX IF NOT EXISTS idx_exhaustivite_statut ON exhaustivite_daily(statut_exhaustivite);

-- Table 4: Weekly productivity aggregation
CREATE TABLE IF NOT EXISTS productivite_weekly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salarie_id INTEGER NOT NULL,
    salarie_nom TEXT NOT NULL,
    equipe TEXT NOT NULL,
    semaine_debut DATE NOT NULL,
    annee INTEGER NOT NULL,
    numero_semaine INTEGER NOT NULL,
    heures_facturables REAL DEFAULT 0,
    heures_travaillees REAL DEFAULT 0,
    productivite_pct REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(salarie_id, annee, numero_semaine)
);

CREATE INDEX IF NOT EXISTS idx_weekly_salarie ON productivite_weekly(salarie_id);
CREATE INDEX IF NOT EXISTS idx_weekly_period ON productivite_weekly(annee, numero_semaine);

-- Table 5: Monthly productivity aggregation
CREATE TABLE IF NOT EXISTS productivite_monthly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salarie_id INTEGER NOT NULL,
    salarie_nom TEXT NOT NULL,
    equipe TEXT NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    heures_facturables REAL DEFAULT 0,
    heures_travaillees REAL DEFAULT 0,
    productivite_pct REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(salarie_id, annee, mois)
);

CREATE INDEX IF NOT EXISTS idx_monthly_salarie ON productivite_monthly(salarie_id);
CREATE INDEX IF NOT EXISTS idx_monthly_period ON productivite_monthly(annee, mois);
CREATE INDEX IF NOT EXISTS idx_monthly_equipe ON productivite_monthly(equipe);

-- Table 6: Rolling 12-month productivity (for SEP)
CREATE TABLE IF NOT EXISTS productivite_rolling12 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salarie_id INTEGER NOT NULL,
    salarie_nom TEXT NOT NULL,
    equipe TEXT NOT NULL,
    date_reference DATE NOT NULL,
    heures_facturables_r12 REAL DEFAULT 0,
    heures_travaillees_r12 REAL DEFAULT 0,
    productivite_r12_pct REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(salarie_id, date_reference)
);

CREATE INDEX IF NOT EXISTS idx_rolling12_salarie ON productivite_rolling12(salarie_id);
CREATE INDEX IF NOT EXISTS idx_rolling12_date ON productivite_rolling12(date_reference);

-- Table 7: Exhaustivity summary by team/month
CREATE TABLE IF NOT EXISTS exhaustivite_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipe TEXT NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    nb_salaries INTEGER DEFAULT 0,
    jours_total INTEGER DEFAULT 0,
    jours_conformes INTEGER DEFAULT 0,
    jours_incomplets INTEGER DEFAULT 0,
    jours_manquants INTEGER DEFAULT 0,
    jours_heures_sup INTEGER DEFAULT 0,
    taux_exhaustivite_pct REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(equipe, annee, mois)
);

CREATE INDEX IF NOT EXISTS idx_summary_equipe ON exhaustivite_summary(equipe);
CREATE INDEX IF NOT EXISTS idx_summary_period ON exhaustivite_summary(annee, mois);
"""

# Helper function to create tables
def create_tables(conn):
    """Create all productivity KPI tables"""
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    print("✓ All tables created successfully")

if __name__ == "__main__":
    import sqlite3
    
    # Test schema creation with SQLite
    conn = sqlite3.connect(':memory:')
    create_tables(conn)
    
    # Verify tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nCreated tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
