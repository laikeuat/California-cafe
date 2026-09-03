from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'

    CARGO_GERENTE = "Gerente"
    CARGO_VENDEDOR = "Vendedor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    nome = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    cargo = Column(String(20), nullable=False, default=CARGO_VENDEDOR)
