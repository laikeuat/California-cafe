from sqlalchemy import Column, Integer, String, Float, LargeBinary, Date, Computed
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Produto(Base):
    __tablename__ = 'produto'

    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String(255), unique=True, nullable=False)
    cod_barras = Column(String(50), nullable=False, unique=True)
    nome = Column(String(255), nullable=False)
    quantidade = Column(Integer, nullable=False)
    cnpj_fornecedor = Column(String(18), nullable=False)
    data_validade = Column(Date, nullable=False)
    valor_venda = Column(Float, nullable=False)
    valor_compra = Column(Float, nullable=False)
    lucro = Column(Float, Computed('valor_venda - valor_compra', persisted=True))
    imagem = Column(LargeBinary)

    def __init__(self, categoria, cod_barras, nome, quantidade_estoque, cnpj_fornecedor, data_validade, valor_compra, valor_venda, imagem):
        self.categoria = categoria
        self.cod_barras = cod_barras
        self.nome = nome
        self.cnpj_fornecedor = cnpj_fornecedor
        self.valor_compra = valor_compra
        self.valor_venda = valor_venda
        self.quantidade = quantidade_estoque
        self.data_validade = data_validade
        self.imagem = imagem
