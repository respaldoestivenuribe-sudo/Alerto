import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("POSTGRES_USER") or os.getenv("PGUSER")
    password = os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD")
    host = os.getenv("DB_HOST") or os.getenv("PGHOST")
    port = os.getenv("DB_PORT") or os.getenv("PGPORT")
    db_name = os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE")

    missing = [
        name for name, value in {
            "POSTGRES_USER/PGUSER": user,
            "POSTGRES_PASSWORD/PGPASSWORD": password,
            "DB_HOST/PGHOST": host,
            "DB_PORT/PGPORT": port,
            "POSTGRES_DB/PGDATABASE": db_name,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {', '.join(missing)}")

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


DATABASE_URL = _database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
