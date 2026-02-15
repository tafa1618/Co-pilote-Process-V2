"""
Data Loader for Productivity KPI
Loads and validates timesheet data from Excel file
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductivityDataLoader:
    """Load and validate productivity timesheet data"""
    
    def __init__(self, file_path: str = "data/productivite.xlsx"):
        self.file_path = Path(file_path)
        self.df_raw = None
        
    def load_data(self) -> pd.DataFrame:
        """Load Excel file into DataFrame"""
        logger.info(f"Loading data from {self.file_path}")
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        self.df_raw = pd.read_excel(self.file_path)
        logger.info(f"Loaded {len(self.df_raw)} rows, {len(self.df_raw.columns)} columns")
        
        return self.df_raw
    
    def validate_columns(self) -> Dict[str, bool]:
        """Validate that all required columns exist"""
        required_columns = [
            'Salarié - Numéro',
            'Salarié - Nom',
            'Salarié - Equipe(Nom)',
            'Saisie heures - Date',
            'OR (Numéro)',
            'Type heure (Libellé)',
            'Heure realisee',
            'Facturable',
            'Non Facturable',
            'Allouée',
            'Hr_travaillée',
            'Hr_Totale'
        ]
        
        validation = {}
        for col in required_columns:
            exists = col in self.df_raw.columns
            validation[col] = exists
            if not exists:
                logger.warning(f"Missing column: {col}")
        
        return validation
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and standardize data"""
        logger.info("Cleaning data...")
        df = self.df_raw.copy()
        
        # Convert date column to datetime
        df['Saisie heures - Date'] = pd.to_datetime(df['Saisie heures - Date'])
        
        # Fill NaN values in numeric columns with 0
        numeric_cols = ['Facturable', 'Non Facturable', 'Allouée', 'Hr_travaillée', 'Hr_Totale']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Ensure OR number is integer
        df['OR (Numéro)'] = df['OR (Numéro)'].fillna(0).astype(int)
        
        # Remove any duplicate rows
        initial_count = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_count:
            logger.info(f"Removed {initial_count - len(df)} duplicate rows")
        
        logger.info(f"Cleaned data: {len(df)} rows")
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics of the data"""
        summary = {
            'total_rows': len(df),
            'total_employees': df['Salarié - Numéro'].nunique(),
            'total_teams': df['Salarié - Equipe(Nom)'].nunique(),
            'date_range': {
                'start': df['Saisie heures - Date'].min(),
                'end': df['Saisie heures - Date'].max(),
                'days': (df['Saisie heures - Date'].max() - df['Saisie heures - Date'].min()).days
            },
            'teams': df['Salarié - Equipe(Nom)'].unique().tolist(),
            'categories': {
                'facturable': df['Facturable'].notna().sum(),
                'non_facturable': df['Non Facturable'].notna().sum(),
                'allouee': df['Allouée'].notna().sum()
            }
        }
        
        return summary
    
    def load_and_prepare(self) -> Tuple[pd.DataFrame, Dict]:
        """Complete loading pipeline"""
        # Load
        self.load_data()
        
        # Validate
        validation = self.validate_columns()
        if not all(validation.values()):
            missing = [k for k, v in validation.items() if not v]
            raise ValueError(f"Missing required columns: {missing}")
        
        # Clean
        df_clean = self.clean_data()
        
        # Summary
        summary = self.get_data_summary(df_clean)
        
        logger.info("Data loading complete")
        logger.info(f"Summary: {summary['total_employees']} employees, {summary['total_teams']} teams")
        
        return df_clean, summary


if __name__ == "__main__":
    # Test the loader
    loader = ProductivityDataLoader()
    df, summary = loader.load_and_prepare()
    
    print("\n=== DATA SUMMARY ===")
    print(f"Total rows: {summary['total_rows']:,}")
    print(f"Employees: {summary['total_employees']}")
    print(f"Teams: {summary['total_teams']}")
    print(f"Period: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"\nTeams: {', '.join(summary['teams'])}")
    print(f"\nCategories:")
    print(f"  Facturable: {summary['categories']['facturable']:,} rows")
    print(f"  Non Facturable: {summary['categories']['non_facturable']:,} rows")
    print(f"  Allouée: {summary['categories']['allouee']:,} rows")
