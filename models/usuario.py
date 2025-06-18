from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    equipe = Column(String(255), nullable=True)
    acesso = Column(Integer, nullable=False)