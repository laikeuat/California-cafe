import dominio.categoria as categoria
from sqlalchemy.orm import sessionmaker

from infraestrutura.banco_dados import get_db

class repositorioCategoria:
    def __init__(self, engine):
        pass
    def criar_categoria(self, nome, descricao):
        nova_categoria = categoria.Categoria(nome=nome, descricao=descricao)
        with get_db() as session:
            try:
                session.add(nova_categoria)
                session.commit()
            except Exception as e:
                session.rollback()
                raise Exception(f"Erro ao criar categoria: {e}")
    def buscar_categoria(self, nome):
        with get_db() as session:
            return session.query(categoria.Categoria).filter_by(nome=nome).first()
    def remover_categoria(self, id):
        with get_db() as session:
            categoria_obj = session.get(categoria.Categoria, id)
            if categoria_obj:
                session.delete(categoria_obj)
                session.commit()
    def buscar_todas_categorias(self):
        with get_db() as session:
            return session.query(categoria.Categoria).all()
    