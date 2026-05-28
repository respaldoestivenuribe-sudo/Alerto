from sqlalchemy import Table, Column, Integer, Float, String, MetaData, TIMESTAMP

metadata = MetaData()

alerts = Table(
    "alerts", metadata,
    Column("id",                Integer,                  primary_key=True, autoincrement=True),
    Column("evaluated_at",      TIMESTAMP(timezone=True), nullable=False),
    Column("precip_1h",         Float,                    nullable=False),
    Column("precip_3h",         Float,                    nullable=False),
    Column("intensidad_actual", Float,                    nullable=False),
    Column("humedad_prom_6h",   Float,                    nullable=False),
    Column("nivel_lluvia",      Float,                    nullable=False),
    Column("riesgo_score",      Float,                    nullable=False),
    Column("nivel_riesgo",      String(10),               nullable=False),
)
