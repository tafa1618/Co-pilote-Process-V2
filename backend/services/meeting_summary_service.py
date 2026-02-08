"""Service pour la génération de comptes rendus de réunion en Markdown"""
from datetime import datetime, date
from typing import Any, Dict, List
import pandas as pd
from services.productivity_service import load_from_db, get_latest_df
from services.inspection_service import calculate_inspection_analytics
from utils.quarters import get_current_quarter_dates
from database import get_conn


def generate_meeting_summary(meeting_date: date | None = None) -> Dict[str, Any]:
    """Génère un snapshot des KPIs et actions pour une réunion"""
    if meeting_date is None:
        meeting_date = date.today()
    
    # Charger les données de productivité
    db_df = load_from_db()
    if db_df is not None and not db_df.empty:
        df = db_df
    elif get_latest_df() is not None and not get_latest_df().empty:
        df = get_latest_df().copy()
    else:
        return {
            "error": "Aucune donnée disponible",
            "meeting_date": meeting_date.isoformat(),
        }
    
    # Calculer les KPIs globaux
    total_hours = float(df["Heures_travaillées"].sum())
    total_fact = float(df["Heures_facturables"].sum())
    global_prod = total_fact / total_hours if total_hours else 0.0
    
    # Calculer les KPIs d'inspection
    start_date, end_date = get_current_quarter_dates()
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
    
    inspection_analytics = calculate_inspection_analytics(start_date, end_date, last_wednesday)
    
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


def generate_sep_markdown(
    summary_data: Dict[str, Any], 
    actions: List[Dict[str, Any]], 
    notes: str = ""
) -> str:
    """Génère un rapport SEP en Markdown"""
    meeting_date = datetime.fromisoformat(summary_data.get('meeting_date', date.today().isoformat())).date()
    
    # Format de date en français
    date_str = meeting_date.strftime("%d %B %Y")
    
    markdown = f"""# COMPTE RENDU RÉUNION SEP

**Date de la séance :** {date_str}

---

## 📊 RÉSUMÉ DE PERFORMANCE

"""
    
    # Productivité
    prod = summary_data.get('productivite_globale', 0)
    if prod >= 85:
        status = "✅ **Excellent** (≥85%)"
    elif prod >= 78:
        status = "⚠️ **Advanced** (78-84%)"
    else:
        status = "❌ **Emerging** (<78%)"
    
    markdown += f"""### Productivité Atelier
- **Taux :** {prod}% - {status} aux objectifs SEP 2025
- **Heures totales :** {summary_data.get('total_heures', 0):.0f}h
- **Heures facturables :** {summary_data.get('total_facturable', 0):.0f}h

"""
    
    # Inspection Rate
    inspection_rate = summary_data.get('inspection_rate', 0)
    inspection_delta = summary_data.get('inspection_delta_weekly', 0)
    if inspection_rate > 0:
        delta_text = f" ({inspection_delta:+.1f}% vs mercredi dernier)" if inspection_delta != 0 else ""
        if inspection_rate >= 65:
            cat_status = "✅ **Excellent** (≥65%)"
        elif inspection_rate >= 50:
            cat_status = "⚠️ **Alerte** (50-64%)"
        else:
            cat_status = "❌ **Critique** (<50%)"
        
        markdown += f"""### Inspection Rate
- **Taux :** {inspection_rate:.1f}% - {cat_status}{delta_text}

"""
    
    markdown += "---\n\n"
    
    # Actions ouvertes
    ouvertes = [a for a in actions if a.get('statut') == 'Ouvert']
    if ouvertes:
        markdown += "## 🔧 ACTIONS LEAN OUVERTES\n\n"
        markdown += "| ID | Date ouverture | Problème | Owner | Date clôture prévue |\n"
        markdown += "|----|----------------|----------|-------|---------------------|\n"
        
        for a in ouvertes:
            probleme = a.get('probleme', '').replace('|', '\\|')
            date_ouv = a.get('date_ouverture', '') or '-'
            date_clot = a.get('date_cloture_prevue', '') or '-'
            owner = a.get('owner', '') or '-'
            markdown += f"| {a.get('id', '')} | {date_ouv} | {probleme} | {owner} | {date_clot} |\n"
        
        markdown += "\n"
    else:
        markdown += "## 🔧 ACTIONS LEAN OUVERTES\n\n"
        markdown += "*Aucune action ouverte.*\n\n"
    
    # Actions critiques
    critiques = [
        a for a in ouvertes 
        if a.get('date_cloture_prevue') 
        and datetime.fromisoformat(a['date_cloture_prevue']).date() < date.today()
    ]
    if critiques:
        markdown += "## 🚨 ACTIONS CRITIQUES (en retard)\n\n"
        markdown += "| ID | Problème | Owner | Date clôture prévue |\n"
        markdown += "|----|----------|-------|---------------------|\n"
        
        for a in critiques:
            probleme = a.get('probleme', '').replace('|', '\\|')
            date_clot = a.get('date_cloture_prevue', '')
            owner = a.get('owner', '') or '-'
            markdown += f"| {a.get('id', '')} | {probleme} | {owner} | {date_clot} |\n"
        
        markdown += "\n"
    
    # Notes de discussion
    if notes:
        markdown += "---\n\n"
        markdown += "## 📝 NOTES DE DISCUSSION\n\n"
        # Convertir les notes en liste à puces
        notes_lines = notes.strip().split('\n')
        for line in notes_lines:
            line = line.strip()
            if line:
                markdown += f"- {line}\n"
        markdown += "\n"
    
    markdown += "---\n\n"
    markdown += f"*Généré le {datetime.now().strftime('%d %B %Y à %H:%M')}*\n"
    
    return markdown
