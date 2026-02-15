"""Routes pour l'upload de fichiers"""
from io import BytesIO
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
import pandas as pd
from config import ADMIN_PASSWORD, ADMIN_EMAIL
from database import get_conn, ensure_schema, POINTAGE_SCHEMA, INSPECTION_RECORD_SCHEMA
from services.productivity_service_legacy import process_uploaded_file, set_latest_df
from preprocessing.preprocessing_inspection import preprocess_uploaded_inspection_file
from services.llti_service import process_uploaded_file as process_llti_file, set_latest_df as set_llti_df

router = APIRouter(tags=["upload"])


@router.post("/kpi/productivite/upload")
async def upload_kpi(request: Request, file: UploadFile = File(...)):
    """Upload des données de productivité"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")

    if ADMIN_PASSWORD:
        provided = request.headers.get("X-Admin-Password") or ""
        if provided != ADMIN_PASSWORD:
            raise HTTPException(status_code=403, detail="Mot de passe admin invalide")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        raise HTTPException(status_code=400, detail="Format non supporté")

    buffer = BytesIO(await file.read())

    try:
        # Pour les fichiers Excel, vérifier s'il y a plusieurs onglets
        if suffix in {".xlsx", ".xls"}:
            excel_file = pd.ExcelFile(buffer)
            sheet_names = excel_file.sheet_names
            
            df = None
            inspection_df = None
            
            for sheet_name in sheet_names:
                sheet_df = pd.read_excel(excel_file, sheet_name=sheet_name)
                if {"Saisie heures - Date", "Salarié - Nom", "Facturable"}.issubset(set(sheet_df.columns)):
                    df = sheet_df
                elif {"sn", "date_facture", "is_inspected"}.issubset(set(sheet_df.columns)) or \
                     {"SN", "Date Facture", "Is Inspected"}.issubset(set(sheet_df.columns)):
                    inspection_df = sheet_df
            
            if df is None and sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_names[0])
        else:
            df = pd.read_csv(buffer)
            inspection_df = None
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erreur lecture fichier: {str(exc)}")

    # Preprocess les données de productivité
    df_prepared = process_uploaded_file(df)

    # Vérifier si la colonne "OR (Numéro)" existe
    or_col = None
    for col in df_prepared.columns:
        if "or" in col.lower() and ("numéro" in col.lower() or "numero" in col.lower()):
            or_col = col
            break
    
    # Agrégation par technicien / jour
    groupby_cols = ["Saisie heures - Date", "Salarié - Nom", "Salarié - Equipe(Nom)"]
    if or_col:
        groupby_cols.append(or_col)
    
    grouped = (
        df_prepared.groupby(groupby_cols, as_index=False)
        .agg(
            facturable=("Facturable", "sum"),
            heures_total=("heures_travaillees", "sum"),
        )
    )

    rows = []
    for _, r in grouped.iterrows():
        rows.append((
            r["Saisie heures - Date"].date(),
            r["Salarié - Nom"],
            r["Salarié - Equipe(Nom)"],
            float(r["facturable"]),
            float(r["heures_total"]),
            str(r.get(or_col, "")) if or_col else None,
        ))

    ensure_schema()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(POINTAGE_SCHEMA)
            cur.executemany(
                """
                INSERT INTO pointage (jour, technicien, equipe, facturable, heures_total, or_numero)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (technicien, jour)
                DO UPDATE SET
                    equipe = EXCLUDED.equipe,
                    facturable = EXCLUDED.facturable,
                    heures_total = EXCLUDED.heures_total,
                    or_numero = EXCLUDED.or_numero,
                    inserted_at = now();
                """,
                rows,
            )
        conn.commit()

    set_latest_df(df_prepared)

    # Traiter les données d'inspection si présentes
    inspection_rows = 0
    if inspection_df is not None:
        try:
            inspection_df.columns = inspection_df.columns.str.strip()
            col_mapping = {}
            for col in inspection_df.columns:
                col_lower = col.lower()
                if "sn" in col_lower or "serial" in col_lower:
                    col_mapping[col] = "sn"
                elif "date" in col_lower and "facture" in col_lower:
                    col_mapping[col] = "date_facture"
                elif "inspect" in col_lower:
                    col_mapping[col] = "is_inspected"
                elif "or" in col_lower and "segment" in col_lower:
                    col_mapping[col] = "or_segment"
                elif "type" in col_lower and "materiel" in col_lower:
                    col_mapping[col] = "type_materiel"
                elif "atelier" in col_lower:
                    col_mapping[col] = "atelier"
            
            inspection_df = inspection_df.rename(columns=col_mapping)
            inspection_df_prepared = preprocess_uploaded_inspection_file(inspection_df)
            
            inspection_rows_data = []
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for _, row in inspection_df_prepared.iterrows():
                        or_segment = str(row.get("or_segment", "") or "").strip()
                        technicien = None
                        equipe = None
                        
                        if or_segment:
                            cur.execute(
                                """
                                SELECT technicien, equipe, SUM(heures_total) as total_heures
                                FROM pointage
                                WHERE or_numero = %s OR or_numero LIKE %s
                                GROUP BY technicien, equipe
                                ORDER BY total_heures DESC
                                LIMIT 1
                                """,
                                (or_segment, f"%{or_segment}%"),
                            )
                            result = cur.fetchone()
                            if result:
                                technicien = result[0]
                                equipe = result[1]
                        
                        inspection_rows_data.append((
                            str(row["sn"]),
                            or_segment,
                            str(row.get("type_materiel", "") or ""),
                            str(row.get("atelier", "") or ""),
                            row["date_facture"].date(),
                            str(row["is_inspected"]),
                            technicien,
                            equipe,
                        ))
            
            if inspection_rows_data:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.executemany(
                            """
                            INSERT INTO inspection_record (sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (sn, date_facture)
                            DO UPDATE SET
                                or_segment = EXCLUDED.or_segment,
                                type_materiel = EXCLUDED.type_materiel,
                                atelier = EXCLUDED.atelier,
                                is_inspected = EXCLUDED.is_inspected,
                                technicien = EXCLUDED.technicien,
                                equipe = EXCLUDED.equipe,
                                inserted_at = now();
                            """,
                            inspection_rows_data,
                        )
                    conn.commit()
                inspection_rows = len(inspection_rows_data)
        except Exception as exc:
            print(f"⚠️ Erreur traitement inspection: {exc}")

    return {
        "message": "Données agrégées et sauvegardées en base (1 ligne par technicien/jour)",
        "kpi": {
            "rows": len(grouped),
            "columns": list(df_prepared.columns),
            "role": user["role"],
            "owner": user["email"],
        },
        "inspection": {
            "rows": inspection_rows,
            "processed": inspection_df is not None,
        } if inspection_df is not None else None,
    }


@router.post("/kpi/inspection/upload")
async def upload_inspection(request: Request, file: UploadFile = File(...)):
    """Upload des données d'inspection"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")

    if ADMIN_PASSWORD:
        provided = request.headers.get("X-Admin-Password") or ""
        if provided != ADMIN_PASSWORD:
            raise HTTPException(status_code=403, detail="Mot de passe admin invalide")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        raise HTTPException(status_code=400, detail="Format non supporté")

    buffer = BytesIO(await file.read())

    try:
        df = pd.read_excel(buffer) if suffix != ".csv" else pd.read_csv(buffer)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Preprocess les données d'inspection
    df_prepared = preprocess_uploaded_inspection_file(df)

    # Pour chaque ligne, chercher le technicien avec le plus d'heures sur l'OR
    ensure_schema()
    rows = []
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for _, row in df_prepared.iterrows():
                or_segment = str(row.get("or_segment", "") or "").strip()
                technicien = None
                equipe = None
                
                if or_segment:
                    cur.execute(
                        """
                        SELECT technicien, equipe, SUM(heures_total) as total_heures
                        FROM pointage
                        WHERE or_numero = %s OR or_numero LIKE %s
                        GROUP BY technicien, equipe
                        ORDER BY total_heures DESC
                        LIMIT 1
                        """,
                        (or_segment, f"%{or_segment}%"),
                    )
                    result = cur.fetchone()
                    if result:
                        technicien = result[0]
                        equipe = result[1]
                
                rows.append((
                    str(row["sn"]),
                    or_segment,
                    str(row.get("type_materiel", "") or ""),
                    str(row.get("atelier", "") or ""),
                    row["date_facture"].date(),
                    str(row["is_inspected"]),
                    technicien,
                    equipe,
                ))

    # Insérer en base
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO inspection_record (sn, or_segment, type_materiel, atelier, date_facture, is_inspected, technicien, equipe)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sn, date_facture)
                DO UPDATE SET
                    or_segment = EXCLUDED.or_segment,
                    type_materiel = EXCLUDED.type_materiel,
                    atelier = EXCLUDED.atelier,
                    is_inspected = EXCLUDED.is_inspected,
                    technicien = EXCLUDED.technicien,
                    equipe = EXCLUDED.equipe,
                    inserted_at = now();
                """,
                rows,
            )
        conn.commit()

    return {"message": "Données d'inspection enregistrées", "rows": len(rows)}


@router.post("/kpi/llti/upload")
async def upload_llti(request: Request, file: UploadFile = File(...)):
    """Upload des données LLTI (Lead Time to Invoice)"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")

    if ADMIN_PASSWORD:
        provided = request.headers.get("X-Admin-Password") or ""
        if provided != ADMIN_PASSWORD:
            raise HTTPException(status_code=403, detail="Mot de passe admin invalide")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        raise HTTPException(status_code=400, detail="Format non supporté")

    buffer = BytesIO(await file.read())

    try:
        df = pd.read_excel(buffer) if suffix != ".csv" else pd.read_csv(buffer)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Preprocess les données LLTI
    df_prepared = process_llti_file(df)
    
    if df_prepared.empty:
        return {"message": "Aucune donnée LLTI valide après preprocessing", "rows": 0}

    # Sauvegarder en mémoire
    set_llti_df(df_prepared)

    # Insérer en base
    ensure_schema()
    rows = []
    
    for _, row in df_prepared.iterrows():
        rows.append((
            str(row.get("N° OR (Segment)", "") or ""),
            str(row.get("N° Facture (Lignes)", "") or ""),
            row["Date Facture (Lignes)"].date() if pd.notna(row["Date Facture (Lignes)"]) else None,
            row["Pointage dernière date (Segment)"].date() if pd.notna(row["Pointage dernière date (Segment)"]) else None,
            str(row.get("Nom Client OR (or)", "") or ""),
            str(row.get("Numéro série Equipement (Segment)", "") or ""),
            str(row.get("Constructeur de l'équipement", "") or ""),
            float(row.get("LLTI_jours", 0) or 0),
        ))

    # Filtrer les lignes valides
    rows = [r for r in rows if r[2] and r[3] and r[1]]  # date_facture, date_pointage, numero_facture

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO llti_record (or_segment, numero_facture, date_facture, date_pointage,
                                       client, sn_equipement, constructeur, llti_jours)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (numero_facture)
                DO UPDATE SET
                    or_segment = EXCLUDED.or_segment,
                    date_facture = EXCLUDED.date_facture,
                    date_pointage = EXCLUDED.date_pointage,
                    client = EXCLUDED.client,
                    sn_equipement = EXCLUDED.sn_equipement,
                    constructeur = EXCLUDED.constructeur,
                    llti_jours = EXCLUDED.llti_jours,
                    inserted_at = now();
                """,
                rows,
            )
        conn.commit()

    return {"message": "Données LLTI enregistrées", "rows": len(rows)}

