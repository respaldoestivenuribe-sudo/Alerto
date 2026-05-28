import os
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.repositories.auth_repository import AuthRepository

JWT_SECRET  = os.getenv("JWT_SECRET", "alerto_secret")
JWT_EXPIRES = 24  # hours


class AuthService:

    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    def register(self, nombre: str, email: str, password: str,
                 security_question: str, security_answer: str,
                 ip: str | None = None) -> dict:
        if self.repo.get_user_by_email(email):
            self.repo.insert_audit_log(None, "register", "users", "failure", ip,
                                       f"email ya registrado: {email}")
            raise ValueError("El correo ya está registrado.")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
        answer_hash   = bcrypt.hashpw(security_answer.lower().encode(), bcrypt.gensalt(12)).decode()

        self.repo.create_user(nombre, email, password_hash, security_question, answer_hash)
        self.repo.insert_audit_log(email, "register", "users", "success", ip)
        return {"message": "Usuario registrado exitosamente."}

    def login(self, email: str, password: str, ip: str | None = None) -> dict:
        user = self.repo.get_user_by_email(email)
        if not user:
            self.repo.insert_audit_log(email, "login", "session", "failure", ip,
                                       "usuario no encontrado")
            raise ValueError("Credenciales inválidas.")

        if not user["is_active"]:
            self.repo.insert_audit_log(email, "login", "session", "failure", ip,
                                       "cuenta desactivada")
            raise ValueError("Cuenta desactivada. Contacta al administrador.")

        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            self.repo.insert_audit_log(email, "login", "session", "failure", ip,
                                       "contraseña incorrecta")
            raise ValueError("Credenciales inválidas.")

        token = jwt.encode(
            {
                "sub":  user["email"],
                "id":   user["id"],
                "name": user["nombre"],
                "role": user["role"],
                "exp":  datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES),
            },
            JWT_SECRET,
            algorithm="HS256",
        )
        self.repo.insert_audit_log(email, "login", "session", "success", ip)
        return {"access_token": token, "token_type": "bearer"}

    def verify_security_answer(self, email: str, answer: str) -> bool:
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("Correo no encontrado.")
        return bcrypt.checkpw(answer.lower().encode(), user["security_answer"].encode())

    def reset_password(self, email: str, answer: str, new_password: str,
                       ip: str | None = None) -> dict:
        if not self.verify_security_answer(email, answer):
            self.repo.insert_audit_log(email, "reset_password", "users", "failure", ip,
                                       "respuesta incorrecta")
            raise ValueError("Respuesta de seguridad incorrecta.")

        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(12)).decode()
        self.repo.update_password(email, password_hash)
        self.repo.insert_audit_log(email, "reset_password", "users", "success", ip)
        return {"message": "Contraseña actualizada exitosamente."}

    def get_security_question(self, email: str) -> str:
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("Correo no encontrado.")
        return user["security_question"]

    def get_me(self, email: str) -> dict:
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        return {
            "id":     user["id"],
            "nombre": user["nombre"],
            "email":  user["email"],
            "role":   user["role"],
        }
