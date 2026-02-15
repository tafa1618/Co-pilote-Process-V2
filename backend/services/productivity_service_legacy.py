"""
Legacy Productivity Service
Maintains backward compatibility for old routes (upload.py, productivity_old.py)
This is a stub service that provides the old interface
"""
import pandas as pd
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for uploaded data (legacy)
_latest_df: Optional[pd.DataFrame] = None


def load_from_db() -> Optional[pd.DataFrame]:
    """Load data from database (stub - returns None)"""
    return None


def get_latest_df() -> Optional[pd.DataFrame]:
    """Get the latest uploaded DataFrame from memory"""
    return _latest_df


def set_latest_df(df: pd.DataFrame):
    """Set the latest DataFrame in memory"""
    global _latest_df
    _latest_df = df.copy()
    logger.info(f"Latest DataFrame set: {len(df)} rows")


def process_uploaded_file(file_path: str) -> pd.DataFrame:
    """
    Process uploaded Excel file (legacy function)
    
    Args:
        file_path: Path to Excel file
    
    Returns:
        Processed DataFrame
    """
    logger.info(f"Processing uploaded file: {file_path}")
    
    # Load Excel
    df = pd.read_excel(file_path)
    
    # Basic cleaning
    df['Saisie heures - Date'] = pd.to_datetime(df['Saisie heures - Date'])
    
    # Fill NaN values
    numeric_cols = ['Facturable', 'Non Facturable', 'Allouée', 'Hr_travaillée', 'Hr_Totale']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Calculate heures_travaillees if not present
    if 'heures_travaillees' not in df.columns:
        df['heures_travaillees'] = df['Hr_travaillée']
    
    # Calculate productivite if not present
    if 'productivite' not in df.columns:
        df['productivite'] = (df['Facturable'] / df['heures_travaillees']).fillna(0)
    
    logger.info(f"File processed: {len(df)} rows")
    
    # Store in memory
    set_latest_df(df)
    
    return df


def calculate_all_productivity_analytics(df: pd.DataFrame) -> dict:
    """
    Calculate productivity analytics (legacy function)
    
    Args:
        df: DataFrame with productivity data
    
    Returns:
        Dictionary with analytics
    """
    logger.info("Calculating productivity analytics (legacy)")
    
    # Basic aggregation
    total_facturable = df['Facturable'].sum()
    total_travaillees = df['heures_travaillees'].sum()
    
    global_productivity = 0
    if total_travaillees > 0:
        global_productivity = (total_facturable / total_travaillees) * 100
    
    # By team
    team_stats = []
    if 'Salarié - Equipe(Nom)' in df.columns:
        for team in df['Salarié - Equipe(Nom)'].unique():
            team_df = df[df['Salarié - Equipe(Nom)'] == team]
            team_fact = team_df['Facturable'].sum()
            team_trav = team_df['heures_travaillees'].sum()
            team_prod = (team_fact / team_trav * 100) if team_trav > 0 else 0
            
            team_stats.append({
                'equipe': team,
                'heures_facturables': float(team_fact),
                'heures_travaillees': float(team_trav),
                'productivite_pct': round(team_prod, 2)
            })
    
    return {
        'global': {
            'heures_facturables': float(total_facturable),
            'heures_travaillees': float(total_travaillees),
            'productivite_pct': round(global_productivity, 2)
        },
        'by_team': sorted(team_stats, key=lambda x: x['productivite_pct'], reverse=True),
        'total_rows': len(df)
    }
