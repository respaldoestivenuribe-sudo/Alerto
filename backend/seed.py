import os
from pathlib import Path
import bcrypt
from sqlalchemy import create_engine, text

DB_CONN = os.getenv("DATABASE_URL")


def get_engine():
    if not DB_CONN:
        raise RuntimeError("DATABASE_URL is required to initialize the database")
    return create_engine(DB_CONN)


def init_schema(engine):
    init_sql_path = os.getenv("INIT_SQL_PATH")
    if not init_sql_path:
        return

    path = Path(init_sql_path)
    if not path.exists():
        print(f"INIT_SQL_PATH no existe, omitiendo init SQL: {path}")
        return

    with engine.begin() as conn:
        conn.execute(text(path.read_text(encoding="utf-8")))
    print(f"Schema inicializado desde {path}")


def seed_admin(engine):
    with engine.begin() as conn:
        existing = conn.execute(
            text("SELECT id FROM users WHERE email = 'admin@alerto.com'")
        ).fetchone()

        if existing:
            print("Admin ya existe, omitiendo seed.")
            return

        password_hash = bcrypt.hashpw(b"alerto123**", bcrypt.gensalt(12)).decode()
        answer_hash   = bcrypt.hashpw(b"admin", bcrypt.gensalt(12)).decode()

        conn.execute(
            text("""
                INSERT INTO users (nombre, email, password_hash, security_question,
                                   security_answer, role)
                VALUES (:nombre, :email, :password_hash, :security_question,
                        :security_answer, :role)
            """),
            {
                "nombre":            "Administrador",
                "email":             "admin@alerto.com",
                "password_hash":     password_hash,
                "security_question": "¿Cuál es el nombre de tu primera mascota?",
                "security_answer":   answer_hash,
                "role":              "administrador",
            }
        )
        print("Admin creado: admin@alerto.com / alerto123**")


if __name__ == "__main__":
    engine = get_engine()
    init_schema(engine)
    seed_admin(engine)
