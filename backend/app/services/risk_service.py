from sqlalchemy.orm import Session
from app.repositories.risk_repository import RiskRepository


class RiskService:

    def __init__(self, db: Session):
        self.repository = RiskRepository(db)

    def get_current(self):
        row = self.repository.get_current()
        if not row:
            return None
        return {
            "nivel_riesgo": row["nivel_riesgo"],
            "riesgo_score": row["riesgo_score"],
            "nivel_lluvia": row["nivel_lluvia"],
            "evaluated_at": row["evaluated_at"],
        }

    def get_history(self, limit: int = 100, offset: int = 0):
        rows = self.repository.get_history(limit=limit, offset=offset)
        return [
            {
                "evaluated_at":    row["evaluated_at"],
                "riesgo_score":    row["riesgo_score"],
                "nivel_riesgo":    row["nivel_riesgo"],
                "precip_1h":       row["precip_1h"],
                "precip_3h":       row["precip_3h"],
                "humedad_prom_6h": row["humedad_prom_6h"],
            }
            for row in rows
        ]

    def get_recent_high_risk(self, hours: int = 24):
        rows = self.repository.get_recent_high_risk(hours=hours)
        return [dict(r) for r in rows]
