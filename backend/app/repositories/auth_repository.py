from sqlalchemy import text
from sqlalchemy.orm import Session


class AuthRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── Users ──────────────────────────────────────────────────────────────────

    def get_user_by_email(self, email: str):
        result = self.db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        )
        return result.mappings().first()

    def get_user_by_id(self, user_id: int):
        result = self.db.execute(
            text("SELECT id, nombre, email, role, is_active, created_at FROM users WHERE id = :id"),
            {"id": user_id}
        )
        return result.mappings().first()

    def get_all_users(self):
        result = self.db.execute(text("""
            SELECT id, nombre, email, role, is_active, created_at
            FROM users ORDER BY created_at DESC
        """))
        return result.mappings().all()

    def create_user(self, nombre: str, email: str, password_hash: str,
                    security_question: str, security_answer: str,
                    role: str = "usuario"):
        self.db.execute(
            text("""
                INSERT INTO users (nombre, email, password_hash, security_question,
                                   security_answer, role)
                VALUES (:nombre, :email, :password_hash, :security_question,
                        :security_answer, :role)
            """),
            {
                "nombre":            nombre,
                "email":             email,
                "password_hash":     password_hash,
                "security_question": security_question,
                "security_answer":   security_answer,
                "role":              role,
            }
        )
        self.db.commit()

    def update_password(self, email: str, password_hash: str):
        self.db.execute(
            text("UPDATE users SET password_hash = :pw WHERE email = :email"),
            {"pw": password_hash, "email": email}
        )
        self.db.commit()

    def update_user_role(self, user_id: int, role: str):
        self.db.execute(
            text("UPDATE users SET role = :role WHERE id = :id"),
            {"role": role, "id": user_id}
        )
        self.db.commit()

    def update_user_status(self, user_id: int, is_active: bool):
        self.db.execute(
            text("UPDATE users SET is_active = :active WHERE id = :id"),
            {"active": is_active, "id": user_id}
        )
        self.db.commit()

    # ── Audit log (RNF-SEG-003) ────────────────────────────────────────────────

    def insert_audit_log(self, user_email, action: str, resource: str,
                         result: str, ip_address=None, details=None):
        self.db.execute(
            text("""
                INSERT INTO audit_log (user_email, action, resource, result, ip_address, details)
                VALUES (:email, :action, :resource, :result, :ip, :details)
            """),
            {
                "email":    user_email,
                "action":   action,
                "resource": resource,
                "result":   result,
                "ip":       ip_address,
                "details":  details,
            }
        )
        self.db.commit()
