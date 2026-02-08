"""Preprocessing des données d'inspection"""
import pandas as pd
from datetime import date
from database import get_conn


def load_raw_inspection_data(
    start_date: date | None = None,
    end_date: date | None = None,
    team: str | None = None
) -> pd.DataFrame | None:
    """Charge les données brutes d'inspection depuis la base de données
    
    Args:
        start_date: Date de début du filtre (optionnel)
        end_date: Date de fin du filtre (optionnel)
        team: Nom de l'équipe pour filtrer (optionnel)
        
    Returns:
        DataFrame brut avec colonnes: sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe
    """
    try:
        with get_conn() as conn:
            query = """
                SELECT sn, or_segment, type_materiel, atelier, date_facture, 
                       is_inspected, technicien, equipe 
                FROM inspection_record
            """
            params = []
            conditions = []

            if start_date and end_date:
                conditions.append("date_facture >= %s AND date_facture <= %s")
                params.extend([start_date, end_date])
            
            if team:
                conditions.append("equipe ILIKE %s")
                params.append(f"%{team}%")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY date_facture DESC"
            
            df = pd.read_sql_query(query, conn, params=params if params else None)
            return df if not df.empty else None
    except Exception as exc:
        print(f"⚠️ Erreur chargement données inspection: {exc}")
        return None


def preprocess_inspection_df(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un DataFrame d'inspection pour l'analyse
    
    Args:
        df: DataFrame brut avec colonnes: sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe
        
    Returns:
        DataFrame préprocessé avec:
        - Filtrage des lignes avec or_segment valide
        - Normalisation des valeurs
        - Colonnes calculées si nécessaire
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # S'assurer que date_facture est une date
    df["date_facture"] = pd.to_datetime(df["date_facture"], errors="coerce")
    df = df.dropna(subset=["date_facture"])

    # Normaliser is_inspected
    df["is_inspected"] = df["is_inspected"].astype(str).str.strip()

    # Filtrer les lignes avec or_segment valide (non vide)
    df["or_segment"] = df["or_segment"].astype(str).str.strip()
    df = df[df["or_segment"] != ""]

    # Normaliser les autres colonnes
    df["sn"] = df["sn"].astype(str).str.strip()
    df["type_materiel"] = df["type_materiel"].astype(str).str.strip()
    df["atelier"] = df["atelier"].astype(str).str.strip()
    df["technicien"] = df["technicien"].astype(str).str.strip()
    df["equipe"] = df["equipe"].astype(str).str.strip()

    return df


def preprocess_uploaded_inspection_file(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess un DataFrame uploadé depuis un fichier Excel/CSV
    
    Args:
        df: DataFrame brut depuis fichier avec colonnes: sn, date_facture, is_inspected, etc.
        
    Returns:
        DataFrame préprocessé prêt pour l'insertion en base
    """
    if df.empty:
        return df

    df = df.copy()

    # Validation des colonnes requises
    required = {"sn", "date_facture", "is_inspected"}
    if not required.issubset(df.columns):
        raise ValueError(f"Colonnes manquantes: {required - set(df.columns)}")

    # Normaliser les colonnes optionnelles
    if "or_segment" not in df.columns:
        df["or_segment"] = ""
    if "type_materiel" not in df.columns:
        df["type_materiel"] = ""
    if "atelier" not in df.columns:
        df["atelier"] = ""

    # Normaliser date_facture
    df["date_facture"] = pd.to_datetime(df["date_facture"], errors="coerce")
    df = df.dropna(subset=["date_facture"])

    # Normaliser is_inspected
    df["is_inspected"] = df["is_inspected"].astype(str).str.strip()
    
    # Valider que les valeurs sont correctes
    valid_values = {"Inspecté", "Non Inspecté"}
    invalid = set(df["is_inspected"].unique()) - valid_values
    if invalid:
        raise ValueError(
            f"Valeurs invalides pour is_inspected: {invalid}. Valeurs attendues: {valid_values}"
        )

    return df

