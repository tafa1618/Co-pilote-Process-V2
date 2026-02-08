"""Application Streamlit pour les vues détaillées des KPIs"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Ajouter le répertoire parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Imports et configuration
import psycopg

# Constantes
STANDARDIZED_HEURES = "Heures_travaillées"
STANDARDIZED_FACTURABLE = "Heures_facturables"
STANDARDIZED_MOIS_PERIODE = "Mois_periode"
COL_TECHNICIEN = "Salarié - Nom"
COL_EQUIPE = "Salarié - Equipe(Nom)"
COL_FACTURABLE = "Facturable"

# Configuration DB
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://kpi_user:kpi_pass@db:5432/kpi_db"

def get_conn():
    """Connexion à la base de données"""
    return psycopg.connect(DATABASE_URL)

def load_from_db():
    """Charge et preprocess les données de productivité depuis la base de données"""
    try:
        with get_conn() as conn:
            df_db = pd.read_sql_query(
                "SELECT jour, technicien, equipe, facturable, heures_total FROM pointage",
                conn,
            )
        if df_db.empty:
            return None
        
        # Preprocessing
        df_db["Saisie heures - Date"] = pd.to_datetime(df_db["jour"])
        df_db[COL_FACTURABLE] = pd.to_numeric(df_db["facturable"], errors="coerce").fillna(0)
        df_db[STANDARDIZED_HEURES] = pd.to_numeric(df_db["heures_total"], errors="coerce")
        df_db[STANDARDIZED_FACTURABLE] = df_db[COL_FACTURABLE]
        df_db[STANDARDIZED_MOIS_PERIODE] = df_db["Saisie heures - Date"].dt.to_period("M")
        df_db = df_db.rename(columns={"technicien": COL_TECHNICIEN, "equipe": COL_EQUIPE})
        
        return df_db
    except Exception as e:
        print(f"⚠️ Erreur chargement productivité: {e}")
        return None

# Imports optionnels pour inspection
try:
    from services.inspection_service import calculate_inspection_analytics, load_inspection_from_db
    from utils.quarters import get_current_quarter_dates, get_quarter_dates
except ImportError:
    # Fallback pour inspection
    def get_quarter_dates(year, quarter):
        """Calcule les dates de début et fin d'un trimestre"""
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3
        from datetime import date
        start_date = date(year, start_month, 1)
        if end_month == 12:
            end_date = date(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            end_date = date(year, end_month + 1, 1) - pd.Timedelta(days=1)
        return start_date, end_date
    
    def calculate_inspection_analytics(start_date, end_date, last_wednesday, team=None):
        """Calcule les analytics d'inspection (fallback)"""
        return {
            "inspection_rate": 0.0,
            "inspected": 0,
            "not_inspected": 0,
            "total": 0,
            "delta_weekly": 0.0,
            "by_atelier": [],
            "by_type_materiel": [],
            "by_technicien": [],
            "records": [],
        }

st.set_page_config(
    page_title="Co-Pilote Process - Détails KPIs",
    page_icon="📊",
    layout="wide"
)

# CSS personnalisé pour correspondre au thème Neemba
st.markdown("""
<style>
    .main {
        background-color: #000000;
        color: #F5F5DC;
    }
    .stSelectbox label, .stSlider label {
        color: #FFD700;
    }
    h1, h2, h3 {
        color: #FFD700;
    }
    .metric-container {
        background-color: rgba(255, 215, 0, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)


def get_query_params():
    """Récupère les paramètres de l'URL"""
    query_params = st.query_params
    return {
        "kpi": query_params.get("kpi", "productivity"),
        "year": int(query_params.get("year", date.today().year)),
        "quarter": int(query_params.get("quarter", (date.today().month - 1) // 3 + 1)),
        "team": query_params.get("team", None),
        "month": query_params.get("month", None),
    }


def render_inspection_detail():
    """Affiche la vue détaillée de l'Inspection Rate"""
    params = get_query_params()
    year = params["year"]
    quarter = params["quarter"]
    team = params["team"]
    
    st.title("📊 Inspection Rate - Détail")
    
    # Sélecteurs
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox("Année", range(2020, 2030), index=year - 2020)
    with col2:
        selected_quarter = st.selectbox("Trimestre", [1, 2, 3, 4], index=quarter - 1)
    with col3:
        # Récupérer les équipes disponibles
        with get_conn() as conn:
            teams_df = pd.read_sql_query(
                "SELECT DISTINCT equipe FROM inspection_record WHERE equipe IS NOT NULL AND equipe != '' ORDER BY equipe",
                conn
            )
        teams = ["Toutes"] + teams_df["equipe"].tolist() if not teams_df.empty else ["Toutes"]
        selected_team_idx = 0
        if team:
            try:
                selected_team_idx = teams.index(team)
            except:
                selected_team_idx = 0
        selected_team = st.selectbox("Équipe", teams, index=selected_team_idx)
        if selected_team == "Toutes":
            selected_team = None
    
    # Calculer les dates du trimestre
    start_date, end_date = get_quarter_dates(selected_year, selected_quarter)
    
    # Calculer le mercredi dernier
    today = date.today()
    current_weekday = today.weekday()
    if current_weekday == 2:
        last_wednesday = today - pd.Timedelta(days=7)
    elif current_weekday > 2:
        days_back = current_weekday - 2
        last_wednesday = today - pd.Timedelta(days=days_back)
    else:
        days_back = 7 - (2 - current_weekday)
        last_wednesday = today - pd.Timedelta(days=days_back)
    
    # Calculer les analytics
    analytics = calculate_inspection_analytics(start_date, end_date, last_wednesday, selected_team)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Taux d'Inspection", f"{analytics['inspection_rate']:.1f}%")
    with col2:
        st.metric("OR Inspectés", analytics['inspected'])
    with col3:
        st.metric("OR Non Inspectés", analytics['not_inspected'])
    with col4:
        st.metric("Total OR", analytics['total'])
    
    # Badge CAT
    rate = analytics['inspection_rate']
    if rate >= 65:
        st.success(f"✅ Excellent (≥65%) - Cible CAT atteinte")
    elif rate >= 50:
        st.warning(f"⚠️ Alerte (50-64%) - Sous la cible CAT")
    else:
        st.error(f"❌ Critique (<50%) - Action requise")
    
    # Delta hebdomadaire
    if analytics['delta_weekly'] != 0:
        delta = analytics['delta_weekly']
        if delta >= 0:
            st.info(f"📈 Variation: +{delta:.1f}% vs mercredi dernier")
        else:
            st.warning(f"📉 Variation: {delta:.1f}% vs mercredi dernier")
    
    # Tableaux de détail
    st.subheader("Performance par Atelier")
    if analytics['by_atelier']:
        atelier_df = pd.DataFrame(analytics['by_atelier'])
        st.dataframe(atelier_df, use_container_width=True)
    
    st.subheader("Performance par Type de Matériel")
    if analytics['by_type_materiel']:
        type_df = pd.DataFrame(analytics['by_type_materiel'])
        st.dataframe(type_df, use_container_width=True)
    
    st.subheader("Performance par Technicien")
    if analytics['by_technicien']:
        tech_df = pd.DataFrame(analytics['by_technicien'])
        st.dataframe(tech_df, use_container_width=True)
    
    # Tableau des enregistrements
    st.subheader("Détail des Enregistrements")
    if analytics['records']:
        records_df = pd.DataFrame(analytics['records'])
        st.dataframe(records_df, use_container_width=True, height=400)


def render_productivity_detail():
    """Affiche la vue détaillée de la Productivité"""
    params = get_query_params()
    month = params.get("month")
    team = params.get("team")
    
    st.title("📈 Productivité - Détail")
    
    # Charger les données
    df = load_from_db()
    if df is None or df.empty:
        st.error("Aucune donnée disponible. Veuillez importer un fichier.")
        return
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        # Convertir Mois_periode en string pour l'affichage
        months = sorted(df[STANDARDIZED_MOIS_PERIODE].dropna().astype(str).unique()) if not df.empty else []
        selected_month = st.selectbox("Mois", ["Tous"] + list(months), index=0)
        if selected_month == "Tous":
            selected_month = None
    
    with col2:
        teams = sorted(df[COL_EQUIPE].dropna().unique()) if not df.empty else []
        selected_team = st.selectbox("Équipe", ["Toutes"] + list(teams), index=0)
        if selected_team == "Toutes":
            selected_team = None
    
    # Filtrer les données
    filtered_df = df.copy()
    if selected_month:
        filtered_df = filtered_df[filtered_df[STANDARDIZED_MOIS_PERIODE].astype(str) == selected_month]
    if selected_team:
        filtered_df = filtered_df[filtered_df[COL_EQUIPE] == selected_team]
    
    # KPI Cards
    total_hours = float(filtered_df[STANDARDIZED_HEURES].sum())
    total_fact = float(filtered_df[STANDARDIZED_FACTURABLE].sum())
    global_prod = total_fact / total_hours if total_hours else 0.0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Productivité Globale", f"{global_prod * 100:.2f}%")
    with col2:
        st.metric("Heures Totales", f"{total_hours:.0f}h")
    with col3:
        st.metric("Facturable", f"{total_fact:.0f}h")
    
    # Tableaux
    st.subheader("Productivité par Technicien")
    tech_agg = (
        filtered_df.groupby(COL_TECHNICIEN)
        .agg(
            facturable=(STANDARDIZED_FACTURABLE, "sum"),
            heures=(STANDARDIZED_HEURES, "sum")
        )
        .reset_index()
    )
    tech_agg["productivite"] = (
        tech_agg["facturable"] / tech_agg["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    tech_agg = tech_agg.sort_values("productivite", ascending=False)
    st.dataframe(tech_agg, use_container_width=True)
    
    st.subheader("Productivité par Équipe")
    team_agg = (
        filtered_df.groupby(COL_EQUIPE)
        .agg(
            facturable=(STANDARDIZED_FACTURABLE, "sum"),
            heures=(STANDARDIZED_HEURES, "sum")
        )
        .reset_index()
    )
    team_agg["productivite"] = (
        team_agg["facturable"] / team_agg["heures"]
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    st.dataframe(team_agg, use_container_width=True)


def main():
    """Point d'entrée principal de l'app Streamlit"""
    params = get_query_params()
    kpi = params["kpi"]
    
    if kpi == "inspection":
        render_inspection_detail()
    elif kpi == "productivity":
        render_productivity_detail()
    else:
        st.error(f"KPI inconnu: {kpi}")


if __name__ == "__main__":
    main()

