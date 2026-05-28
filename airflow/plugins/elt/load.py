import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert
from elt.config import DB_CONN
from elt.models import bronze_weather_current, bronze_weather_hourly


def get_engine():
    return create_engine(DB_CONN)


def load_current(df: pd.DataFrame):
    if df is None or df.empty:
        print("DataFrame current vacío, no se cargan")
        return

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            insert(bronze_weather_current),
            df.to_dict(orient="records")
        )
    print(f"Cargadas {len(df)} filas a bronze_weather_current")


def load_hourly(df: pd.DataFrame):
    if df is None or df.empty:
        print("DataFrame hourly vacío, no se carga")
        return

    engine = get_engine()
    stmt = insert(bronze_weather_hourly)
    stmt = stmt.on_conflict_do_update(
        index_elements=["time"],
        set_={
            "fetched_at":        stmt.excluded.fetched_at,
            "precipitation":     stmt.excluded.precipitation,
            "rain":              stmt.excluded.rain,
            "showers":           stmt.excluded.showers,
            "relative_humidity": stmt.excluded.relative_humidity,
            "cloudcover":        stmt.excluded.cloudcover,
            "windspeed_10m":     stmt.excluded.windspeed_10m,
        }
    )

    with engine.begin() as conn:
        conn.execute(stmt, df.to_dict(orient="records"))
    print(f"Cargadas {len(df)} filas a bronze_weather_hourly")