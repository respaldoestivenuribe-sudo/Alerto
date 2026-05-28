from sqlalchemy import text
from sqlalchemy.orm import Session


class RiskRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_current(self):
        result = self.db.execute(text("""
            SELECT nivel_riesgo, riesgo_score, nivel_lluvia, evaluated_at
            FROM public.alerts
            ORDER BY evaluated_at DESC
            LIMIT 1
        """))
        return result.mappings().first()

    def get_history(self, limit: int = 100, offset: int = 0):
        result = self.db.execute(
            text("""
                SELECT evaluated_at, riesgo_score, nivel_riesgo,
                       precip_1h, precip_3h, humedad_prom_6h
                FROM public.alerts
                ORDER BY evaluated_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )
        return result.mappings().all()

    def get_recent_high_risk(self, hours: int = 24):
        result = self.db.execute(
            text("""
                SELECT id, evaluated_at, nivel_riesgo, riesgo_score
                FROM public.alerts
                WHERE nivel_riesgo IN ('NARANJA', 'ROJO')
                  AND evaluated_at >= NOW() - INTERVAL ':hours hours'
                ORDER BY evaluated_at DESC
                LIMIT 50
            """.replace(":hours", str(hours)))
        )
        return result.mappings().all()
