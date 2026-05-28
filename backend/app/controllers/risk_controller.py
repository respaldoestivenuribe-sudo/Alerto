from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.security import get_current_user
from app.services.risk_service import RiskService
from fastapi import HTTPException

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.get("/current")
def get_current_risk(user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = RiskService(db)
    result = service.get_current()
    if not result:
        raise HTTPException(status_code=404, detail="No hay datos de riesgo disponibles")
    return result


@router.get("/history")
def get_risk_history(limit: int = 100, offset: int = 0,
                     user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = RiskService(db)
    return service.get_history(limit=min(limit, 500), offset=offset)


@router.get("/alerts/recent")
def get_recent_alerts(hours: int = 24, user=Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """Returns high-risk alerts from the last N hours (for notification bell)."""
    service = RiskService(db)
    return service.get_recent_high_risk(hours=min(hours, 72))
