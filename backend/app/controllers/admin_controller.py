from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.security import require_admin
from app.repositories.auth_repository import AuthRepository

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_ROLES = {"usuario", "administrador"}


class RoleUpdate(BaseModel):
    role: str


class StatusUpdate(BaseModel):
    is_active: bool


@router.get("/users")
def list_users(admin=Depends(require_admin), db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    rows = repo.get_all_users()
    return [dict(r) for r in rows]


@router.patch("/users/{user_id}/role")
def update_role(user_id: int, body: RoleUpdate,
                admin=Depends(require_admin), db: Session = Depends(get_db)):
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Rol inválido. Válidos: {VALID_ROLES}")

    repo = AuthRepository(db)
    if not repo.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    repo.update_user_role(user_id, body.role)
    repo.insert_audit_log(
        admin["sub"], "update_role", "users", "success",
        details=f"user_id={user_id} new_role={body.role}"
    )
    return {"message": "Rol actualizado."}


@router.patch("/users/{user_id}/status")
def update_status(user_id: int, body: StatusUpdate,
                  admin=Depends(require_admin), db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    if not repo.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    repo.update_user_status(user_id, body.is_active)
    action = "activate_user" if body.is_active else "deactivate_user"
    repo.insert_audit_log(
        admin["sub"], action, "users", "success",
        details=f"user_id={user_id}"
    )
    return {"message": "Estado actualizado."}


@router.get("/audit-log")
def get_audit_log(limit: int = 100, admin=Depends(require_admin),
                  db: Session = Depends(get_db)):
    from sqlalchemy import text
    rows = db.execute(
        text("SELECT * FROM audit_log ORDER BY ts DESC LIMIT :limit"),
        {"limit": min(limit, 500)}
    ).mappings().all()
    return [dict(r) for r in rows]
