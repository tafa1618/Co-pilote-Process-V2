import pandas as pd
import sys

# Force UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Charger les données
df = pd.read_excel('data/productivite.xlsx')

print("=" * 80)
print("ANALYSE STRUCTURE FICHIER PRODUCTIVITE")
print("=" * 80)

print(f"\nDIMENSIONS")
print(f"   Lignes: {len(df):,}")
print(f"   Colonnes: {len(df.columns)}")

print(f"\nSALARIES")
print(f"   Salaries uniques: {df['Salarié - Numéro'].nunique()}")
print(f"   Equipes uniques: {df['Salarié - Equipe(Nom)'].nunique()}")

print(f"\nPERIODE")
print(f"   Du: {df['Saisie heures - Date'].min()}")
print(f"   Au: {df['Saisie heures - Date'].max()}")
print(f"   Jours: {(df['Saisie heures - Date'].max() - df['Saisie heures - Date'].min()).days}")

print(f"\nCATEGORIES D'HEURES")
print(df['Categorie Heure'].value_counts())

print(f"\nTYPES D'HEURES (Top 15)")
print(df['Type heure (Libellé)'].value_counts().head(15))

print(f"\nSTATISTIQUES HEURES")
stats_cols = ['Facturable', 'Non Facturable', 'Allouée', 'Hr_travaillée', 'Hr_Totale']
print(df[stats_cols].describe())

print(f"\nVALEURS MANQUANTES")
print(df[stats_cols].isnull().sum())

print(f"\nEXEMPLE AGREGATION PAR SALARIE/JOUR")
daily_agg = df.groupby(['Salarié - Numéro', 'Salarié - Nom', 'Saisie heures - Date']).agg({
    'Facturable': 'sum',
    'Non Facturable': 'sum',
    'Hr_travaillée': 'sum',
    'Hr_Totale': 'sum'
}).reset_index()

print(daily_agg.head(10))

print(f"\nDISTRIBUTION HEURES TOTALES PAR JOUR")
print(daily_agg['Hr_Totale'].value_counts().head(20))

print(f"\nEXEMPLES ANOMALIES EXHAUSTIVITE")
print("\nJours avec 0h:")
print(daily_agg[daily_agg['Hr_Totale'] == 0].head(5))
print(f"\nJours avec <8h (hors 0):")
print(daily_agg[(daily_agg['Hr_Totale'] > 0) & (daily_agg['Hr_Totale'] < 8)].head(5))
print(f"\nJours avec >8h:")
print(daily_agg[daily_agg['Hr_Totale'] > 8].head(5))
