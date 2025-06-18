from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import create_access_token
from database import SessionLocal
from services import user_service
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import Token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_access_token({"sub": user.usuario})  # <-- Atenção aqui também
    return {"access_token": token, "token_type": "bearer"}