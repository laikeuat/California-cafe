from infraestrutura.banco_dados import get_db
from dominio.usuario import Usuario


class RepositorioUsuario:
    def __init__(self):
        pass

    def inserir_usuario(self, email, nome, senha, cargo=Usuario.CARGO_VENDEDOR):
        with get_db() as session:
            novo_usuario = Usuario(email=email, nome=nome, senha=senha, cargo=cargo)
            session.add(novo_usuario)
            session.commit()

    def buscar_usuario(self, email):
        with get_db() as session:
            return session.query(Usuario).filter_by(email=email).first()

    def buscar_todos_vendedores(self):
        with get_db() as session:
            return session.query(Usuario).filter_by(cargo=Usuario.CARGO_VENDEDOR).all()
