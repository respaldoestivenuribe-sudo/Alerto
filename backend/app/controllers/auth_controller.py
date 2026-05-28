from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db import get_db
from app.services.auth_service import AuthService
from app.middleware.security import get_current_user

router  = APIRouter(prefix="/api/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


class RegisterRequest(BaseModel):
    nombre:            str      = Field(..., min_length=2, max_length=100)
    email:             EmailStr
    password:          str      = Field(..., min_length=6)
    security_question: str
    security_answer:   str


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email:        EmailStr
    answer:       str
    new_password: str = Field(..., min_length=6)


@router.post("/register")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.register(
            body.nombre, body.email, body.password,
            body.security_question, body.security_answer,
            ip=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.login(
            body.email, body.password,
            ip=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/security-question")
def get_security_question(email: str, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return {"security_question": service.get_security_question(email)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reset-password")
def reset_password(request: Request, body: ResetPasswordRequest,
                   db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.reset_password(
            body.email, body.answer, body.new_password,
            ip=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def me(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.get_me(user["sub"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
