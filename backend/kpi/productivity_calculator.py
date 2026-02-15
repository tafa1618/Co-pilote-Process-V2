"""
Productivity Calculation Functions
Implements daily, weekly, monthly, and rolling 12-month productivity calculations
Based on productivity_kpi_methodology.md
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductivityCalculator:
    """Calculate productivity metrics at various time granularities"""
    
    def __init__(self, df_raw: pd.DataFrame):
        """
        Initialize calculator with raw timesheet data
        
        Args:
            df_raw: Raw DataFrame from productivity_loader
        """
        self.df_raw = df_raw
        self.df_daily = None
        
    def calculate_productivity_daily(self) -> pd.DataFrame:
        """
        Calculate daily productivity per employee
        
        Formula: Productivity = (Facturable / Hr_travaillée) × 100
        
        Returns:
            DataFrame with columns: salarie_id, salarie_nom, equipe, date,
                                   heures_facturables, heures_non_facturables,
                                   heures_allouees, heures_travaillees, heures_totales,
                                   productivite_pct
        """
        logger.info("Calculating daily productivity...")
        
        # Group by employee + date
        df_daily = self.df_raw.groupby([
            'Salarié - Numéro',
            'Salarié - Nom',
            'Salarié - Equipe(Nom)',
            'Saisie heures - Date'
        ]).agg({
            'Facturable': 'sum',
            'Non Facturable': 'sum',
            'Allouée': 'sum',
            'Hr_travaillée': 'sum',
            'Hr_Totale': 'sum'
        }).reset_index()
        
        # Rename columns
        df_daily.columns = [
            'salarie_id', 'salarie_nom', 'equipe', 'date',
            'heures_facturables', 'heures_non_facturables', 'heures_allouees',
            'heures_travaillees', 'heures_totales'
        ]
        
        # Calculate productivity percentage
        df_daily['productivite_pct'] = np.where(
            df_daily['heures_travaillees'] > 0,
            (df_daily['heures_facturables'] / df_daily['heures_travaillees']) * 100,
            0
        )
        
        # Round to 2 decimals
        df_daily['productivite_pct'] = df_daily['productivite_pct'].round(2)
        
        logger.info(f"Daily productivity calculated: {len(df_daily)} employee-days")
        
        self.df_daily = df_daily
        return df_daily
    
    def calculate_productivity_weekly(self, df_daily: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate weekly productivity per employee
        
        Args:
            df_daily: Daily productivity DataFrame (uses self.df_daily if None)
        
        Returns:
            DataFrame with weekly aggregation
        """
        if df_daily is None:
            df_daily = self.df_daily
        
        if df_daily is None:
            raise ValueError("Must run calculate_productivity_daily() first")
        
        logger.info("Calculating weekly productivity...")
        
        # Add week information
        df_daily['annee'] = df_daily['date'].dt.isocalendar().year
        df_daily['numero_semaine'] = df_daily['date'].dt.isocalendar().week
        df_daily['semaine_debut'] = df_daily['date'] - pd.to_timedelta(df_daily['date'].dt.weekday, unit='d')
        
        # Group by employee + week
        df_weekly = df_daily.groupby([
            'salarie_id',
            'salarie_nom',
            'equipe',
            'annee',
            'numero_semaine',
            'semaine_debut'
        ]).agg({
            'heures_facturables': 'sum',
            'heures_travaillees': 'sum'
        }).reset_index()
        
        # Calculate weekly productivity
        df_weekly['productivite_pct'] = np.where(
            df_weekly['heures_travaillees'] > 0,
            (df_weekly['heures_facturables'] / df_weekly['heures_travaillees']) * 100,
            0
        ).round(2)
        
        logger.info(f"Weekly productivity calculated: {len(df_weekly)} employee-weeks")
        
        return df_weekly
    
    def calculate_productivity_monthly(self, df_daily: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate monthly productivity per employee
        
        Args:
            df_daily: Daily productivity DataFrame (uses self.df_daily if None)
        
        Returns:
            DataFrame with monthly aggregation
        """
        if df_daily is None:
            df_daily = self.df_daily
        
        if df_daily is None:
            raise ValueError("Must run calculate_productivity_daily() first")
        
        logger.info("Calculating monthly productivity...")
        
        # Add month information
        df_daily['annee'] = df_daily['date'].dt.year
        df_daily['mois'] = df_daily['date'].dt.month
        
        # Group by employee + month
        df_monthly = df_daily.groupby([
            'salarie_id',
            'salarie_nom',
            'equipe',
            'annee',
            'mois'
        ]).agg({
            'heures_facturables': 'sum',
            'heures_travaillees': 'sum'
        }).reset_index()
        
        # Calculate monthly productivity
        df_monthly['productivite_pct'] = np.where(
            df_monthly['heures_travaillees'] > 0,
            (df_monthly['heures_facturables'] / df_monthly['heures_travaillees']) * 100,
            0
        ).round(2)
        
        logger.info(f"Monthly productivity calculated: {len(df_monthly)} employee-months")
        
        return df_monthly
    
    def calculate_productivity_rolling12(self, df_daily: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate rolling 12-month productivity per employee (for SEP)
        
        Args:
            df_daily: Daily productivity DataFrame (uses self.df_daily if None)
        
        Returns:
            DataFrame with rolling 12-month productivity
        """
        if df_daily is None:
            df_daily = self.df_daily
        
        if df_daily is None:
            raise ValueError("Must run calculate_productivity_daily() first")
        
        logger.info("Calculating rolling 12-month productivity...")
        
        # Get unique employees
        employees = df_daily[['salarie_id', 'salarie_nom', 'equipe']].drop_duplicates()
        
        # Get all dates
        all_dates = df_daily['date'].unique()
        all_dates.sort()
        
        rolling_results = []
        
        for _, emp in employees.iterrows():
            emp_data = df_daily[df_daily['salarie_id'] == emp['salarie_id']].copy()
            emp_data = emp_data.sort_values('date')
            
            # For each date, calculate rolling 12 months
            for date in all_dates:
                # Get data from (date - 12 months) to date
                start_date = date - pd.DateOffset(months=12)
                mask = (emp_data['date'] >= start_date) & (emp_data['date'] <= date)
                period_data = emp_data[mask]
                
                if len(period_data) > 0:
                    heures_fact_r12 = period_data['heures_facturables'].sum()
                    heures_trav_r12 = period_data['heures_travaillees'].sum()
                    
                    prod_r12 = 0
                    if heures_trav_r12 > 0:
                        prod_r12 = (heures_fact_r12 / heures_trav_r12) * 100
                    
                    rolling_results.append({
                        'salarie_id': emp['salarie_id'],
                        'salarie_nom': emp['salarie_nom'],
                        'equipe': emp['equipe'],
                        'date_reference': date,
                        'heures_facturables_r12': heures_fact_r12,
                        'heures_travaillees_r12': heures_trav_r12,
                        'productivite_r12_pct': round(prod_r12, 2)
                    })
        
        df_rolling12 = pd.DataFrame(rolling_results)
        
        logger.info(f"Rolling 12-month productivity calculated: {len(df_rolling12)} records")
        
        return df_rolling12
    
    def calculate_team_productivity(self, df_daily: pd.DataFrame = None, 
                                   period: str = 'monthly') -> pd.DataFrame:
        """
        Calculate productivity by team (aggregated across all employees)
        
        Args:
            df_daily: Daily productivity DataFrame
            period: 'daily', 'weekly', or 'monthly'
        
        Returns:
            DataFrame with team-level productivity
        """
        if df_daily is None:
            df_daily = self.df_daily
        
        if df_daily is None:
            raise ValueError("Must run calculate_productivity_daily() first")
        
        logger.info(f"Calculating {period} team productivity...")
        
        if period == 'monthly':
            df_daily['annee'] = df_daily['date'].dt.year
            df_daily['mois'] = df_daily['date'].dt.month
            group_cols = ['equipe', 'annee', 'mois']
        elif period == 'weekly':
            df_daily['annee'] = df_daily['date'].dt.isocalendar().year
            df_daily['numero_semaine'] = df_daily['date'].dt.isocalendar().week
            group_cols = ['equipe', 'annee', 'numero_semaine']
        else:  # daily
            group_cols = ['equipe', 'date']
        
        # Aggregate by team
        df_team = df_daily.groupby(group_cols).agg({
            'heures_facturables': 'sum',
            'heures_travaillees': 'sum',
            'salarie_id': 'nunique'  # Count unique employees
        }).reset_index()
        
        df_team.rename(columns={'salarie_id': 'nb_salaries'}, inplace=True)
        
        # Calculate team productivity
        df_team['productivite_pct'] = np.where(
            df_team['heures_travaillees'] > 0,
            (df_team['heures_facturables'] / df_team['heures_travaillees']) * 100,
            0
        ).round(2)
        
        logger.info(f"Team productivity calculated: {len(df_team)} team-periods")
        
        return df_team


if __name__ == "__main__":
    # Test the calculator
    from productivity_loader import ProductivityDataLoader
    
    # Load data
    loader = ProductivityDataLoader()
    df_raw, summary = loader.load_and_prepare()
    
    # Calculate productivity
    calc = ProductivityCalculator(df_raw)
    
    # Daily
    df_daily = calc.calculate_productivity_daily()
    print("\n=== DAILY PRODUCTIVITY (Sample) ===")
    print(df_daily.head(10))
    print(f"\nAverage daily productivity: {df_daily['productivite_pct'].mean():.2f}%")
    
    # Weekly
    df_weekly = calc.calculate_productivity_weekly()
    print("\n=== WEEKLY PRODUCTIVITY (Sample) ===")
    print(df_weekly.head(5))
    
    # Monthly
    df_monthly = calc.calculate_productivity_monthly()
    print("\n=== MONTHLY PRODUCTIVITY (Sample) ===")
    print(df_monthly.head(5))
    
    # Team (monthly)
    df_team = calc.calculate_team_productivity(period='monthly')
    print("\n=== TEAM PRODUCTIVITY (Sample) ===")
    print(df_team.head(10))
    print(f"\nTeam productivity by equipe:")
    team_avg = df_team.groupby('equipe')['productivite_pct'].mean().sort_values(ascending=False)
    print(team_avg)
