from pydantic import BaseModel

class Usuario(BaseModel):
    id: int
    usuario: str
    equipe: str | None
    acesso: int

class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: Usuario