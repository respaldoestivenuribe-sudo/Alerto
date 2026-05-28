from sqlalchemy.orm import Session
from app.repositories.precipitation_repository import PrecipitationRepository


class PrecipitationService:

    def __init__(self, db: Session):
        self.repository = PrecipitationRepository(db)

    def get_current(self):
        row = self.repository.get_current()
        if not row:
            return None
        return {
            "precipitation_1h": row["precipitation_1h"],
            "precipitation_3h": row["precipitation_3h"],
            "precipitation_6h": row["precipitation_6h"],
            "humidity_avg_6h":  row["humidity_avg_6h"],
            "trend_1h":         row["trend_1h"],
            "as_of_time":       row["as_of_time"],
        }

    def get_history(self, limit: int = 100, offset: int = 0):
        rows = self.repository.get_history(limit=limit, offset=offset)
        return [
            {
                "time_local":       row["time_local"],
                "precipitation_mm": row["precipitation_mm"],
            }
            for row in rows
        ]
