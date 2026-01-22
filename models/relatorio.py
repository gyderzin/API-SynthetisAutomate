from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean, Text
from database import Base

class Relatorio(Base):
    __tablename__ = "relatorios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    modelo = Column(String(256), nullable=False)
    emissor = Column(String(256), nullable=False)
    equipe = Column(String(256), nullable=False)
    nome_arquivo = Column(String(256), nullable=False)
    item_pendente = Column(Text, nullable=False)
    caminho_arquivo = Column(String(512), nullable=False)
    emitido_em = Column(TIMESTAMP, server_default=func.now())
