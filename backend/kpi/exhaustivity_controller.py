"""
Exhaustivity Control Functions
Implements daily exhaustivity checks, anomaly detection, and compliance tracking
Based on productivity_kpi_methodology.md
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExhaustivityController:
    """Control exhaustivity of timesheet data"""
    
    def __init__(self, df_daily: pd.DataFrame):
        """
        Initialize controller with daily aggregated data
        
        Args:
            df_daily: Daily productivity DataFrame from ProductivityCalculator
        """
        self.df_daily = df_daily
        
    def generate_expected_calendar(self, start_date: str, end_date: str, 
                                   include_weekends: bool = False) -> pd.DataFrame:
        """
        Generate expected calendar of working days
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            include_weekends: If True, include Saturdays and Sundays
        
        Returns:
            DataFrame with columns: date, jour_semaine, type_jour
        """
        logger.info(f"Generating expected calendar from {start_date} to {end_date}")
        
        # Generate date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create DataFrame
        df_calendar = pd.DataFrame({
            'date': date_range,
            'jour_semaine': date_range.weekday,  # 0=Monday, 6=Sunday
        })
        
        # Add type_jour
        df_calendar['type_jour'] = df_calendar['jour_semaine'].apply(
            lambda x: 'weekend' if x >= 5 else 'ouvre'
        )
        
        # Filter weekends if needed
        if not include_weekends:
            df_calendar = df_calendar[df_calendar['type_jour'] == 'ouvre']
        
        logger.info(f"Generated {len(df_calendar)} days ({df_calendar['type_jour'].value_counts().to_dict()})")
        
        return df_calendar
    
    def check_exhaustivity_daily(self) -> pd.DataFrame:
        """
        Check exhaustivity status for each employee-day
        
        Status rules:
        - VERT: 8h (normal) OR weekend with 0h
        - ORANGE: 0 < Hr_Totale < 8h (incomplete)
        - ROUGE: 0h on working day (missing)
        - BLEU: > 8h (overtime)
        
        Returns:
            DataFrame with exhaustivity status for each employee-day
        """
        logger.info("Checking daily exhaustivity...")
        
        df_exh = self.df_daily.copy()
        
        # Add day of week
        df_exh['jour_semaine'] = df_exh['date'].dt.weekday
        df_exh['type_jour'] = df_exh['jour_semaine'].apply(
            lambda x: 'weekend' if x >= 5 else 'ouvre'
        )
        
        # Determine status
        def get_status(row):
            hr = row['heures_totales']
            is_weekend = row['type_jour'] == 'weekend'
            
            if hr == 0:
                return 'VERT' if is_weekend else 'ROUGE'
            elif hr < 8:
                return 'ORANGE'
            elif hr == 8:
                return 'VERT'
            else:  # hr > 8
                return 'BLEU'
        
        df_exh['statut_exhaustivite'] = df_exh.apply(get_status, axis=1)
        
        # Select relevant columns
        df_exh = df_exh[[
            'salarie_id', 'salarie_nom', 'equipe', 'date',
            'heures_totales', 'jour_semaine', 'type_jour', 'statut_exhaustivite'
        ]]
        
        logger.info(f"Exhaustivity checked: {len(df_exh)} employee-days")
        logger.info(f"Status distribution: {df_exh['statut_exhaustivite'].value_counts().to_dict()}")
        
        return df_exh
    
    def calculate_exhaustivity_rate(self, df_exhaustivity: pd.DataFrame = None,
                                   by: str = 'global') -> pd.DataFrame:
        """
        Calculate exhaustivity rate (% of compliant days)
        
        Args:
            df_exhaustivity: Exhaustivity DataFrame (from check_exhaustivity_daily)
            by: Aggregation level - 'global', 'team', 'employee', 'month'
        
        Returns:
            DataFrame with exhaustivity rates
        """
        if df_exhaustivity is None:
            df_exhaustivity = self.check_exhaustivity_daily()
        
        logger.info(f"Calculating exhaustivity rate by {by}...")
        
        # Filter only working days for rate calculation
        df_work = df_exhaustivity[df_exhaustivity['type_jour'] == 'ouvre'].copy()
        
        if by == 'global':
            total_days = len(df_work)
            compliant_days = len(df_work[df_work['statut_exhaustivite'] == 'VERT'])
            rate = (compliant_days / total_days * 100) if total_days > 0 else 0
            
            result = pd.DataFrame([{
                'scope': 'Global',
                'jours_total': total_days,
                'jours_conformes': compliant_days,
                'jours_incomplets': len(df_work[df_work['statut_exhaustivite'] == 'ORANGE']),
                'jours_manquants': len(df_work[df_work['statut_exhaustivite'] == 'ROUGE']),
                'jours_heures_sup': len(df_work[df_work['statut_exhaustivite'] == 'BLEU']),
                'taux_exhaustivite_pct': round(rate, 2)
            }])
            
        elif by == 'team':
            result = df_work.groupby('equipe').apply(
                lambda x: pd.Series({
                    'jours_total': len(x),
                    'jours_conformes': len(x[x['statut_exhaustivite'] == 'VERT']),
                    'jours_incomplets': len(x[x['statut_exhaustivite'] == 'ORANGE']),
                    'jours_manquants': len(x[x['statut_exhaustivite'] == 'ROUGE']),
                    'jours_heures_sup': len(x[x['statut_exhaustivite'] == 'BLEU']),
                    'nb_salaries': x['salarie_id'].nunique(),
                    'taux_exhaustivite_pct': round(
                        (len(x[x['statut_exhaustivite'] == 'VERT']) / len(x) * 100) if len(x) > 0 else 0,
                        2
                    )
                })
            ).reset_index()
            
        elif by == 'employee':
            result = df_work.groupby(['salarie_id', 'salarie_nom', 'equipe']).apply(
                lambda x: pd.Series({
                    'jours_total': len(x),
                    'jours_conformes': len(x[x['statut_exhaustivite'] == 'VERT']),
                    'jours_incomplets': len(x[x['statut_exhaustivite'] == 'ORANGE']),
                    'jours_manquants': len(x[x['statut_exhaustivite'] == 'ROUGE']),
                    'jours_heures_sup': len(x[x['statut_exhaustivite'] == 'BLEU']),
                    'taux_exhaustivite_pct': round(
                        (len(x[x['statut_exhaustivite'] == 'VERT']) / len(x) * 100) if len(x) > 0 else 0,
                        2
                    )
                })
            ).reset_index()
            
        elif by == 'month':
            df_work['annee'] = df_work['date'].dt.year
            df_work['mois'] = df_work['date'].dt.month
            
            result = df_work.groupby(['equipe', 'annee', 'mois']).apply(
                lambda x: pd.Series({
                    'jours_total': len(x),
                    'jours_conformes': len(x[x['statut_exhaustivite'] == 'VERT']),
                    'jours_incomplets': len(x[x['statut_exhaustivite'] == 'ORANGE']),
                    'jours_manquants': len(x[x['statut_exhaustivite'] == 'ROUGE']),
                    'jours_heures_sup': len(x[x['statut_exhaustivite'] == 'BLEU']),
                    'nb_salaries': x['salarie_id'].nunique(),
                    'taux_exhaustivite_pct': round(
                        (len(x[x['statut_exhaustivite'] == 'VERT']) / len(x) * 100) if len(x) > 0 else 0,
                        2
                    )
                })
            ).reset_index()
        
        logger.info(f"Exhaustivity rate calculated: {len(result)} records")
        
        return result
    
    def detect_anomalies(self, df_exhaustivity: pd.DataFrame = None,
                        anomaly_types: List[str] = None) -> pd.DataFrame:
        """
        Detect and filter anomalies
        
        Args:
            df_exhaustivity: Exhaustivity DataFrame
            anomaly_types: List of status to filter ['ROUGE', 'ORANGE', 'BLEU']
                          If None, returns all anomalies (non-VERT)
        
        Returns:
            DataFrame with only anomalous records
        """
        if df_exhaustivity is None:
            df_exhaustivity = self.check_exhaustivity_daily()
        
        if anomaly_types is None:
            anomaly_types = ['ROUGE', 'ORANGE', 'BLEU']
        
        logger.info(f"Detecting anomalies: {anomaly_types}")
        
        # Filter anomalies
        df_anomalies = df_exhaustivity[
            df_exhaustivity['statut_exhaustivite'].isin(anomaly_types)
        ].copy()
        
        # Sort by severity (ROUGE > ORANGE > BLEU)
        severity_order = {'ROUGE': 1, 'ORANGE': 2, 'BLEU': 3}
        df_anomalies['severity'] = df_anomalies['statut_exhaustivite'].map(severity_order)
        df_anomalies = df_anomalies.sort_values(['severity', 'date', 'equipe', 'salarie_nom'])
        df_anomalies = df_anomalies.drop('severity', axis=1)
        
        logger.info(f"Detected {len(df_anomalies)} anomalies")
        logger.info(f"Breakdown: {df_anomalies['statut_exhaustivite'].value_counts().to_dict()}")
        
        return df_anomalies
    
    def get_missing_days(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Identify days where employees should have worked but didn't submit timesheets
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with missing employee-days
        """
        logger.info(f"Identifying missing days from {start_date} to {end_date}")
        
        # Get expected calendar (working days only)
        df_expected = self.generate_expected_calendar(start_date, end_date, include_weekends=False)
        
        # Get unique employees
        employees = self.df_daily[['salarie_id', 'salarie_nom', 'equipe']].drop_duplicates()
        
        # Create expected employee-days (Cartesian product)
        expected_records = []
        for _, emp in employees.iterrows():
            for _, day in df_expected.iterrows():
                expected_records.append({
                    'salarie_id': emp['salarie_id'],
                    'salarie_nom': emp['salarie_nom'],
                    'equipe': emp['equipe'],
                    'date': day['date']
                })
        
        df_expected_all = pd.DataFrame(expected_records)
        
        # Get actual records
        df_actual = self.df_daily[['salarie_id', 'date']].copy()
        df_actual['has_record'] = True
        
        # Merge to find missing
        df_merged = df_expected_all.merge(
            df_actual,
            on=['salarie_id', 'date'],
            how='left'
        )
        
        df_missing = df_merged[df_merged['has_record'].isna()].copy()
        df_missing = df_missing.drop('has_record', axis=1)
        
        logger.info(f"Found {len(df_missing)} missing employee-days")
        
        return df_missing


if __name__ == "__main__":
    # Test the controller
    from productivity_loader import ProductivityDataLoader
    from productivity_calculator import ProductivityCalculator
    
    # Load and calculate
    loader = ProductivityDataLoader()
    df_raw, summary = loader.load_and_prepare()
    
    calc = ProductivityCalculator(df_raw)
    df_daily = calc.calculate_productivity_daily()
    
    # Exhaustivity control
    controller = ExhaustivityController(df_daily)
    
    # Check exhaustivity
    df_exh = controller.check_exhaustivity_daily()
    print("\n=== EXHAUSTIVITY STATUS (Sample) ===")
    print(df_exh.head(10))
    print(f"\nStatus distribution:")
    print(df_exh['statut_exhaustivite'].value_counts())
    
    # Calculate rates
    print("\n=== GLOBAL EXHAUSTIVITY RATE ===")
    rate_global = controller.calculate_exhaustivity_rate(df_exh, by='global')
    print(rate_global)
    
    print("\n=== EXHAUSTIVITY RATE BY TEAM ===")
    rate_team = controller.calculate_exhaustivity_rate(df_exh, by='team')
    print(rate_team.sort_values('taux_exhaustivite_pct', ascending=False))
    
    # Detect anomalies
    print("\n=== CRITICAL ANOMALIES (ROUGE) ===")
    anomalies_rouge = controller.detect_anomalies(df_exh, anomaly_types=['ROUGE'])
    print(f"Total: {len(anomalies_rouge)} missing days")
    print(anomalies_rouge.head(10))
    
    print("\n=== INCOMPLETE DAYS (ORANGE) ===")
    anomalies_orange = controller.detect_anomalies(df_exh, anomaly_types=['ORANGE'])
    print(f"Total: {len(anomalies_orange)} incomplete days")
    print(anomalies_orange.head(10))
