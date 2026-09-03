from sqlalchemy import Column, Integer, String, Float, LargeBinary, Date, Computed
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Categoria(Base):
    __tablename__ = 'categoria'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)
    descricao = Column(String(500), nullable=True)

    def __init__(self, nome, descricao=None):
        self.nome = nome
        self.descricao = descricao
        
    