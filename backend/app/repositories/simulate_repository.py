from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session


class SimulateRepository:

    def __init__(self, db: Session):
        self.db = db

    def insert_bronze(self, precip_1h: float, precip_3h: float, humedad: float):
        now        = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        fetched_at = datetime.now(timezone.utc)

        remaining       = max(precip_3h - precip_1h, 0)
        precip_horas_12 = remaining / 2

        entries = []
        for i in range(10):
            t = now - timedelta(hours=i)
            if i == 0:
                precip = precip_1h
            elif i <= 2:
                precip = precip_horas_12
            else:
                precip = 0.0

            entries.append({
                "fetched_at":        fetched_at,
                "time":              t,
                "precipitation":     precip,
                "rain":              precip,
                "showers":           0.0,
                "relative_humidity": humedad,
                "cloudcover":        80.0,
                "windspeed_10m":     10.0,
            })

        self.db.execute(
            text("""
                INSERT INTO bronze_weather_hourly
                    (fetched_at, time, precipitation, rain, showers,
                    relative_humidity, cloudcover, windspeed_10m)
                VALUES
                    (:fetched_at, :time, :precipitation, :rain, :showers,
                    :relative_humidity, :cloudcover, :windspeed_10m)
                ON CONFLICT (time) DO UPDATE SET
                    fetched_at        = EXCLUDED.fetched_at,
                    precipitation     = EXCLUDED.precipitation,
                    rain              = EXCLUDED.rain,
                    showers           = EXCLUDED.showers,
                    relative_humidity = EXCLUDED.relative_humidity,
                    cloudcover        = EXCLUDED.cloudcover,
                    windspeed_10m     = EXCLUDED.windspeed_10m
            """),
            entries
        )

        self.db.execute(
            text("""
                INSERT INTO bronze_weather_current
                    (fetched_at, time, precipitation, rain, showers,
                    relative_humidity, cloudcover, windspeed_10m)
                VALUES
                    (:fetched_at, :time, :precipitation, :rain, :showers,
                    :relative_humidity, :cloudcover, :windspeed_10m)
            """),
            entries[0]
        )

        self.db.commit()