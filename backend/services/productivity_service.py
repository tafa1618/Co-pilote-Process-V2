"""
Productivity KPI Service
Handles business logic for productivity calculations and data retrieval
"""
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import logging

from kpi.productivity_loader import ProductivityDataLoader
from kpi.productivity_calculator import ProductivityCalculator
from kpi.exhaustivity_controller import ExhaustivityController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductivityService:
    """Service layer for productivity KPI operations"""
    
    def __init__(self):
        """Initialize service with data loader and calculator"""
        self.loader = ProductivityDataLoader()
        self.df_raw = None
        self.df_daily = None
        self.calculator = None
        self.controller = None
        self._initialized = False
    
    def initialize(self):
        """Load and prepare data (call once at startup)"""
        if self._initialized:
            return
        
        logger.info("Initializing Productivity Service...")
        
        try:
            # Load data
            self.df_raw, summary = self.loader.load_and_prepare()
            
            # Calculate daily productivity
            self.calculator = ProductivityCalculator(self.df_raw)
            self.df_daily = self.calculator.calculate_productivity_daily()
            
            # Initialize exhaustivity controller
            self.controller = ExhaustivityController(self.df_daily)
            
            self._initialized = True
            logger.info("Productivity Service initialized successfully")
        except FileNotFoundError as e:
            logger.error(f"Failed to initialize Productivity Service: {e}")
            logger.info("Service will start without data. Please ensure the data file exists.")
        except Exception as e:
            logger.error(f"Unexpected error during Productivity Service initialization: {e}")
    
    def get_productivity_daily(self, salarie_id: Optional[int] = None,
                              equipe: Optional[str] = None,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> List[Dict]:
        """
        Get daily productivity data with optional filters
        
        Args:
            salarie_id: Filter by employee ID
            equipe: Filter by team name
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
        
        Returns:
            List of daily productivity records
        """
        self.initialize()
        
        df = self.df_daily.copy()
        
        # Apply filters
        if salarie_id:
            df = df[df['salarie_id'] == salarie_id]
        if equipe:
            df = df[df['equipe'] == equipe]
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        
        # Convert to dict
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        return df.to_dict('records')
    
    def get_productivity_team(self, period: str = 'monthly',
                             equipe: Optional[str] = None,
                             year: Optional[int] = None,
                             month: Optional[int] = None) -> List[Dict]:
        """
        Get team productivity aggregated by period
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            equipe: Filter by team name
            year: Filter by year
            month: Filter by month (only for monthly period)
        
        Returns:
            List of team productivity records
        """
        self.initialize()
        
        df = self.calculator.calculate_team_productivity(period=period)
        
        # Apply filters
        if equipe:
            df = df[df['equipe'] == equipe]
        if year and 'annee' in df.columns:
            df = df[df['annee'] == year]
        if month and 'mois' in df.columns:
            df = df[df['mois'] == month]
        
        # Convert dates if present
        if 'date' in df.columns:
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        if 'semaine_debut' in df.columns:
            df['semaine_debut'] = df['semaine_debut'].dt.strftime('%Y-%m-%d')
        
        return df.to_dict('records')
    
    def get_exhaustivity_summary(self, by: str = 'team',
                                equipe: Optional[str] = None,
                                year: Optional[int] = None,
                                month: Optional[int] = None) -> List[Dict]:
        """
        Get exhaustivity summary
        
        Args:
            by: Aggregation level - 'global', 'team', 'employee', 'month'
            equipe: Filter by team name
            year: Filter by year
            month: Filter by month
        
        Returns:
            List of exhaustivity summary records
        """
        self.initialize()
        
        df_exh = self.controller.check_exhaustivity_daily()
        df_summary = self.controller.calculate_exhaustivity_rate(df_exh, by=by)
        
        # Apply filters
        if equipe and 'equipe' in df_summary.columns:
            df_summary = df_summary[df_summary['equipe'] == equipe]
        if year and 'annee' in df_summary.columns:
            df_summary = df_summary[df_summary['annee'] == year]
        if month and 'mois' in df_summary.columns:
            df_summary = df_summary[df_summary['mois'] == month]
        
        return df_summary.to_dict('records')
    
    def get_exhaustivity_anomalies(self, anomaly_types: Optional[List[str]] = None,
                                  equipe: Optional[str] = None,
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None,
                                  limit: int = 100) -> List[Dict]:
        """
        Get exhaustivity anomalies
        
        Args:
            anomaly_types: List of status ['ROUGE', 'ORANGE', 'BLEU']
            equipe: Filter by team name
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
            limit: Maximum number of records to return
        
        Returns:
            List of anomaly records
        """
        self.initialize()
        
        df_exh = self.controller.check_exhaustivity_daily()
        df_anomalies = self.controller.detect_anomalies(df_exh, anomaly_types=anomaly_types)
        
        # Apply filters
        if equipe:
            df_anomalies = df_anomalies[df_anomalies['equipe'] == equipe]
        if start_date:
            df_anomalies = df_anomalies[df_anomalies['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df_anomalies = df_anomalies[df_anomalies['date'] <= pd.to_datetime(end_date)]
        
        # Limit results
        df_anomalies = df_anomalies.head(limit)
        
        # Convert dates
        df_anomalies['date'] = df_anomalies['date'].dt.strftime('%Y-%m-%d')
        
        return df_anomalies.to_dict('records')
    
    def get_teams_list(self) -> List[str]:
        """Get list of all teams"""
        self.initialize()
        return sorted(self.df_daily['equipe'].unique().tolist())
    
    def get_employees_list(self, equipe: Optional[str] = None) -> List[Dict]:
        """
        Get list of all employees
        
        Args:
            equipe: Filter by team name
        
        Returns:
            List of employee records with id, name, and team
        """
        self.initialize()
        
        df = self.df_daily[['salarie_id', 'salarie_nom', 'equipe']].drop_duplicates()
        
        if equipe:
            df = df[df['equipe'] == equipe]
        
        df = df.sort_values(['equipe', 'salarie_nom'])
        
        return df.to_dict('records')


# Global service instance
productivity_service = ProductivityService()
