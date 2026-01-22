from sqlalchemy import Column, Integer, String, Text, LargeBinary, TIMESTAMP, text, Boolean
from database import Base

class Modelo(Base):
    __tablename__ = "modelos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    equipe = Column(String(255), nullable=True)
    descriçao = Column(String(500), nullable=False)
    modelo_automacao = Column(Text, nullable=False)  # LONGTEXT para JSON em texto puro
    documento_modelo = Column(LargeBinary, nullable=False)  # MEDIUMBLOB para o Word
    termografia = Column(Boolean, nullable=False)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
