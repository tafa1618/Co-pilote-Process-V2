"""Routes pour les actions Lean"""
from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict
from config import ALLOWED_ADMINS
from database import get_conn

router = APIRouter(prefix="/api/lean-actions", tags=["lean-actions"])


@router.get("")
async def get_lean_actions(request: Request):
    """Récupère toutes les actions lean"""
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
                    SELECT id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes, 
                           created_at, updated_at
                    FROM lean_action
                    ORDER BY date_ouverture DESC, id DESC
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
                        "created_at": r[7].isoformat() if r[7] else None,
                        "updated_at": r[8].isoformat() if r[8] else None,
                    }
                    for r in rows
                ]
        return {"actions": actions}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {exc}")


@router.post("")
async def create_lean_action(request: Request, action: Dict[str, Any]):
    """Crée une nouvelle action lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    probleme = action.get("probleme", "").strip()
    if not probleme:
        raise HTTPException(status_code=400, detail="Le problème est obligatoire")
    
    owner = action.get("owner", email).strip() or email
    date_ouverture = action.get("date_ouverture")
    date_cloture_prevue = action.get("date_cloture_prevue")
    statut = action.get("statut", "Ouvert")
    notes = action.get("notes", "").strip()
    
    if statut not in ["Ouvert", "Clôturé"]:
        statut = "Ouvert"
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lean_action 
                    (date_ouverture, date_cloture_prevue, probleme, owner, statut, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes, 
                              created_at, updated_at
                """, (date_ouverture, date_cloture_prevue, probleme, owner, statut, notes))
                row = cur.fetchone()
                conn.commit()
                return {
                    "id": row[0],
                    "date_ouverture": row[1].isoformat() if row[1] else None,
                    "date_cloture_prevue": row[2].isoformat() if row[2] else None,
                    "probleme": row[3],
                    "owner": row[4],
                    "statut": row[5],
                    "notes": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None,
                }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {exc}")


@router.put("/{action_id}")
async def update_lean_action(request: Request, action_id: int, action: Dict[str, Any]):
    """Met à jour une action lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    updates = []
    params = []
    
    if "date_cloture_prevue" in action:
        updates.append("date_cloture_prevue = %s")
        params.append(action["date_cloture_prevue"])
    
    if "probleme" in action:
        updates.append("probleme = %s")
        params.append(action["probleme"].strip())
    
    if "owner" in action:
        updates.append("owner = %s")
        params.append(action["owner"].strip())
    
    if "statut" in action:
        statut = action["statut"]
        if statut in ["Ouvert", "Clôturé"]:
            updates.append("statut = %s")
            params.append(statut)
    
    if "notes" in action:
        updates.append("notes = %s")
        params.append(action["notes"].strip())
    
    if not updates:
        raise HTTPException(status_code=400, detail="Aucune modification fournie")
    
    updates.append("updated_at = now()")
    params.append(action_id)
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE lean_action
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING id, date_ouverture, date_cloture_prevue, probleme, owner, statut, notes,
                              created_at, updated_at
                """, params)
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Action non trouvée")
                conn.commit()
                return {
                    "id": row[0],
                    "date_ouverture": row[1].isoformat() if row[1] else None,
                    "date_cloture_prevue": row[2].isoformat() if row[2] else None,
                    "probleme": row[3],
                    "owner": row[4],
                    "statut": row[5],
                    "notes": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None,
                }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {exc}")


@router.delete("/{action_id}")
async def delete_lean_action(request: Request, action_id: int):
    """Supprime une action lean"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    email = user["email"].lower()
    if email not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Accès restreint")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM lean_action WHERE id = %s RETURNING id", (action_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Action non trouvée")
                conn.commit()
        return {"message": "Action supprimée", "id": action_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {exc}")

