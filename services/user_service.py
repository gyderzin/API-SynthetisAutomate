from sqlalchemy.orm import Session
from models.usuario import User
from core.security import verify_password

def get_user_by_usuario(db: Session, usuario: str):
    """
    Busca um usuário no banco pelo campo 'usuario'.
    """
    return db.query(User).filter(User.usuario == usuario).first()

def authenticate_user(db: Session, usuario: str, senha: str):
    """
    Valida o login:
    1. Verifica se o usuário existe
    2. Compara a senha informada com o hash no banco
    """
    user = get_user_by_usuario(db, usuario)
    if not user:
        return None  # Usuário não encontrado

    if not verify_password(senha, user.senha):
        return None  # Senha inválida

    return user  # Autenticação bem-sucedida