"""
RF-005 / RF-006 — Configurable thresholds and pipeline frequency.
Admins can read and update system_config key-value pairs.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.security import get_current_user, require_admin

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdate(BaseModel):
    value: str


@router.get("")
def get_config(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT key, value, description, updated_at, updated_by FROM system_config ORDER BY key")
    ).mappings().all()
    return [dict(r) for r in rows]


@router.patch("/{key}")
def update_config(key: str, body: ConfigUpdate,
                  admin=Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT key FROM system_config WHERE key = :key"), {"key": key}
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Clave de configuración no encontrada.")

    db.execute(
        text("""
            UPDATE system_config
            SET value = :value, updated_at = NOW(), updated_by = :by
            WHERE key = :key
        """),
        {"value": body.value, "by": admin["sub"], "key": key}
    )
    db.commit()
    return {"message": "Configuración actualizada.", "key": key, "value": body.value}
