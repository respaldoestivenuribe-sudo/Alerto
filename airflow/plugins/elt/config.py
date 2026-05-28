import os

LAT = 6.274446878228221
LON = -75.58206257517574

FIELDS_CURRENT = "precipitation,rain,showers,relative_humidity_2m,cloudcover,windspeed_10m"
FIELDS_HOURLY  = "precipitation,rain,showers,relative_humidity_2m,cloudcover,windspeed_10m"

OPEN_METEO_CURRENT_URL = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={LAT}&longitude={LON}"
    f"&current={FIELDS_CURRENT}"
    f"&timezone=America/Bogota"
)

OPEN_METEO_HOURLY_URL = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={LAT}&longitude={LON}"
    f"&hourly={FIELDS_HOURLY}"
    f"&timezone=America/Bogota"
    f"&past_days=7"
)

DB_CONN = os.getenv("DATABASE_URL")