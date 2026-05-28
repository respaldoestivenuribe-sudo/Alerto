from sqlalchemy import text
from sqlalchemy.orm import Session


class PrecipitationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_current(self):
        result = self.db.execute(text("""
            SELECT precipitation_1h, precipitation_3h, precipitation_6h,
                   humidity_avg_6h, trend_1h, as_of_time
            FROM public_gold.gold_risk_features_latest
            LIMIT 1
        """))
        return result.mappings().first()

    def get_history(self, limit: int = 100, offset: int = 0):
        result = self.db.execute(
            text("""
                SELECT time_local, precipitation_mm
                FROM public_gold.gold_precipitation_history
                ORDER BY time_local DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )
        return result.mappings().all()
