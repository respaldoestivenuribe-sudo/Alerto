from sqlalchemy import Table, Column, Integer, Float, MetaData, TIMESTAMP


metadata = MetaData()

bronze_weather_current = Table(
    "bronze_weather_current", metadata,
    Column("id",                Integer, primary_key=True, autoincrement=True),
    Column("fetched_at",        TIMESTAMP(timezone=True), nullable=False),
    Column("time",              TIMESTAMP(timezone=True), nullable=False),
    Column("precipitation",     Float),
    Column("rain",              Float),
    Column("showers",           Float),
    Column("relative_humidity", Float),
    Column("cloudcover",        Float),
    Column("windspeed_10m",     Float),
)

bronze_weather_hourly = Table(
    "bronze_weather_hourly", metadata,
    Column("id",                Integer, primary_key=True, autoincrement=True),
    Column("fetched_at",        TIMESTAMP(timezone=True), nullable=False),
    Column("time",              TIMESTAMP(timezone=True), nullable=False, unique=True),
    Column("precipitation",     Float),
    Column("rain",              Float),
    Column("showers",           Float),
    Column("relative_humidity", Float),
    Column("cloudcover",        Float),
    Column("windspeed_10m",     Float),
)