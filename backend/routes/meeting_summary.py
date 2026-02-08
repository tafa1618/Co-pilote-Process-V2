"""Routes pour les comptes rendus de réunion"""
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from config import ALLOWED_ADMINS
from database import get_conn
from services.meeting_summary_service import generate_meeting_summary, generate_sep_markdown

router = APIRouter(prefix="/api/meeting-summary", tags=["meeting-summary"])


@router.post("/generate")
async def generate_cr(request: Request):
    """Génère un compte rendu de réunion (snapshot + Markdown)"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        payload = await request.json()
    except:
        payload = {}
    
    try:
        # Générer le snapshot
        meeting_date = date.today()
        if payload.get("meeting_date"):
            meeting_date = datetime.fromisoformat(payload["meeting_date"]).date()
        
        summary = generate_meeting_summary(meeting_date)
        if "error" in summary:
            raise HTTPException(status_code=400, detail=summary["error"])
        
        # Récupérer les actions
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes
                    FROM lean_action
                    ORDER BY date_ouverture DESC
                """)
                rows = cur.fetchall()
                actions = [
                    {
                        "id": r[0],
                        "date_ouverture": r[1].isoformat() if r[1] else None,
                        "date_cloture_prevue": r[2].isoformat() if r[2] else None,
                        "probleme": r[3],
                        "owner": r[4],
                        "statut": r[5],
                        "notes": r[6],
                    }
                    for r in rows
                ]
        
        # Générer le Markdown
        notes_discussion = payload.get("notes_discussion", "")
        markdown_content = generate_sep_markdown(summary, actions, notes_discussion)
        
        # Sauvegarder en base
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO meeting_summary 
                    (meeting_date, productivite_globale, total_heures, total_facturable, 
                     actions_ouvertes, actions_critiques, notes_discussion, markdown_content, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    meeting_date,
                    summary["productivite_globale"],
                    summary["total_heures"],
                    summary["total_facturable"],
                    summary["actions_ouvertes"],
                    summary["actions_critiques"],
                    notes_discussion,
                    markdown_content,
                    email,
                ))
                cr_id = cur.fetchone()[0]
                conn.commit()
        
        # Retourner le Markdown
        return JSONResponse({
            "id": cr_id,
            "meeting_date": meeting_date.isoformat(),
            "markdown": markdown_content,
            "summary": summary,
        })
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {exc}")


@router.get("/list")
async def list_cr(request: Request):
    """Liste tous les comptes rendus générés"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, meeting_date, productivite_globale, total_heures, total_facturable,
                           actions_ouvertes, actions_critiques, created_by, created_at
                    FROM meeting_summary
                    ORDER BY meeting_date DESC, created_at DESC
                """)
                rows = cur.fetchall()
                summaries = [
                    {
                        "id": r[0],
                        "meeting_date": r[1].isoformat() if r[1] else None,
                        "productivite_globale": float(r[2]) if r[2] else 0,
                        "total_heures": float(r[3]) if r[3] else 0,
                        "total_facturable": float(r[4]) if r[4] else 0,
                        "actions_ouvertes": r[5],
                        "actions_critiques": r[6],
                        "created_by": r[7],
                        "created_at": r[8].isoformat() if r[8] else None,
                    }
                    for r in rows
                ]
        return {"summaries": summaries}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {exc}")


@router.get("/{cr_id}")
async def get_cr(request: Request, cr_id: int):
    """Récupère un compte rendu archivé (Markdown)"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, meeting_date, productivite_globale, total_heures, total_facturable,
                           actions_ouvertes, actions_critiques, notes_discussion, markdown_content,
                           created_by, created_at
                    FROM meeting_summary
                    WHERE id = %s
                """, (cr_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Compte rendu non trouvé")
                
                return JSONResponse({
                    "id": row[0],
                    "meeting_date": row[1].isoformat() if row[1] else None,
                    "productivite_globale": float(row[2]) if row[2] else 0,
                    "total_heures": float(row[3]) if row[3] else 0,
                    "total_facturable": float(row[4]) if row[4] else 0,
                    "actions_ouvertes": row[5],
                    "actions_critiques": row[6],
                    "notes_discussion": row[7] or "",
                    "markdown": row[8] or "",
                    "created_by": row[9],
                    "created_at": row[10].isoformat() if row[10] else None,
                })
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {exc}")

