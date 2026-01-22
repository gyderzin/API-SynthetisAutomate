from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import (
    create_access_token,
    create_refresh_token,
)
from database import SessionLocal
from services import user_service
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import Token
from jose import jwt, JWTError
from core.security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# LOGIN → retorna access + refresh
# -----------------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")        

    data = {"sub": user.usuario}

    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario": {
            "id": user.id,
            "usuario": user.usuario,
            "equipe": user.equipe,
            "acesso": user.acesso
        }
    }


# -----------------------------
# RENOVA TOKEN
# -----------------------------
@router.post("/refresh")
def refresh_token_endpoint(refresh_token: str):
    """
    Recebe um refresh token e devolve novo access token.
    """

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Refresh inválido")

        # cria novo access
        new_access = create_access_token({"sub": username})

        return {"access_token": new_access}

    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh inválido ou expirado")
