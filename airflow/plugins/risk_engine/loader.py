from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert

from elt.config import DB_CONN
from risk_engine.models import alerts
from risk_engine.engine import calculate_risk


def _get_engine():
    return create_engine(DB_CONN)


def _fetch_gold_features(conn):
    result = conn.execute(text("""
        SELECT
            precipitation_1h,
            precipitation_3h,
            humidity_avg_6h,
            intensity_mm_h
        FROM public_gold.gold_risk_features_latest
        LIMIT 1
    """))
    return result.mappings().first()


def run_risk_engine():
    engine = _get_engine()
    with engine.begin() as conn:
        row = _fetch_gold_features(conn)
        if row is None:
            print("No hay datos en gold_risk_features_latest, omitiendo ciclo.")
            return

        result = calculate_risk(
            precip_1h         = float(row["precipitation_1h"]),
            precip_3h         = float(row["precipitation_3h"]),
            intensidad_actual = float(row["intensity_mm_h"]),
            humedad_prom_6h   = float(row["humidity_avg_6h"]),
        )

        conn.execute(
            insert(alerts),
            {
                "evaluated_at":     datetime.now(timezone.utc),
                "precip_1h":        float(row["precipitation_1h"]),
                "precip_3h":        float(row["precipitation_3h"]),
                "intensidad_actual": float(row["intensity_mm_h"]),
                "humedad_prom_6h":  float(row["humidity_avg_6h"]),
                "nivel_lluvia":     result["nivel_lluvia"],
                "riesgo_score":     result["riesgo_score"],
                "nivel_riesgo":     result["nivel_riesgo"],
            }
        )

    print(f"Riesgo calculado: {result['nivel_riesgo']} (score={result['riesgo_score']})")