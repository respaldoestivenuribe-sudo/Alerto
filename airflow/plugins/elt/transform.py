import pandas as pd
from datetime import datetime, timezone


def transform_current(raw_data: dict) -> pd.DataFrame:
    """Convierte el JSON current de Open-Meteo en un DataFrame de una fila"""
    if not raw_data or "current" not in raw_data:
        print("Error: datos current vacíos o inválidos")
        return None

    current = raw_data["current"]

    df = pd.DataFrame([{
        "fetched_at":         datetime.now(timezone.utc),
        "time":               pd.to_datetime(current.get("time")),
        "precipitation":      current.get("precipitation"),
        "rain":               current.get("rain"),
        "showers":            current.get("showers"),
        "relative_humidity":  current.get("relative_humidity_2m"),
        "cloudcover":         current.get("cloudcover"),
        "windspeed_10m":      current.get("windspeed_10m"),
    }])

    print(f"Transform current: {len(df)} fila generada")
    return df


def transform_hourly(raw_data: dict) -> pd.DataFrame:
    """Convierte el JSON hourly de Open-Meteo en un DataFrame de N filas"""
    if not raw_data or "hourly" not in raw_data:
        print("Error: datos hourly vacíos o inválidos")
        return None

    hourly = raw_data["hourly"]

    df = pd.DataFrame({
        "time":              pd.to_datetime(hourly.get("time")),
        "precipitation":     hourly.get("precipitation"),
        "rain":              hourly.get("rain"),
        "showers":           hourly.get("showers"),
        "relative_humidity": hourly.get("relative_humidity_2m"),
        "cloudcover":        hourly.get("cloudcover"),
        "windspeed_10m":     hourly.get("windspeed_10m"),
    })

    df["fetched_at"] = datetime.now(timezone.utc)
    df = df.dropna(subset=["precipitation"])

    print(f"Transform hourly: {len(df)} filas generadas")
    return df