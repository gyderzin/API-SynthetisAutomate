from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal

router = APIRouter(prefix="/test", tags=["Test"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")  # Consulta simples só pra testar a conexão
        return {"status": "Conexão com o banco de dados bem-sucedida!"}
    except Exception as e:
        return {"status": "Falha na conexão com o banco", "error": str(e)}