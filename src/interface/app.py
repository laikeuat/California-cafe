import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import customtkinter as ctk

from interface import tema
from aplicacao.produto_aplicacao import produtoAplicacao
from aplicacao.usuario_aplicacao import usuarioAplicacao
from infraestrutura.repositorio_produto import repositorioProduto
from infraestrutura.repositorio_usuario import RepositorioUsuario
from dominio.usuario import Usuario

from interface.tela_login import LoginFrame
from interface.dashboard import DashboardFrame
from interface.tela_produtos import ProdutosFrame
from interface.pdv import PDVFrame


class App(ctk.CTk):
    """
    Janela única da aplicação.

    Em vez de cada tela abrir sua própria janela (ctk.CTk()), o app mantém
    UMA janela raiz e troca o conteúdo trocando o CTkFrame exibido dentro
    dela. Isso evita o bug de o programa fechar/travar após o login, que
    acontecia porque o CustomTkinter não suporta múltiplas janelas raiz
    (CTk()) simultâneas - ele mantém gerenciadores globais de tema/escala
    atrelados a uma única janela raiz.

    Diálogos modais (cadastrar produto, alterar produto) continuam usando
    CTkToplevel, que é o jeito correto de abrir uma janela secundária por
    cima da janela principal.
    """

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.title("Distribuidora Canaã 🌾 Gestão de Estoque")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        self.configure(fg_color=tema.TRIGO)

        # Estado/serviços compartilhados entre as telas
        self.usuario_autenticado = None
        self.usuario_aplicacao = usuarioAplicacao()
        self.repositorio_usuario = RepositorioUsuario()
        self.repositorio_produto = repositorioProduto()
        self.produto_aplicacao = produtoAplicacao(self.repositorio_produto)

        # Container único onde as "páginas" (frames) são desenhadas
        self.container = ctk.CTkFrame(self, fg_color=tema.TRIGO)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.mostrar_login()

    def _limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---- Navegação entre telas ----------------------------------------

    def mostrar_login(self):
        self._limpar_container()
        frame = LoginFrame(
            self.container,
            usuario_aplicacao=self.usuario_aplicacao,
            on_login_success=self.rotear_pos_login,
        )
        frame.grid(row=0, column=0, sticky="nsew")

    def rotear_pos_login(self, usuario):
        """
        Decide a tela inicial de acordo com o cargo do usuário:
        - Vendedor: vai direto pro PDV, sem acesso a Dashboard/Produtos.
        - Gerente: vai pro Dashboard, com acesso a gestão de produtos e
          cadastro de novos vendedores.
        """
        self.usuario_autenticado = usuario
        if usuario.cargo == Usuario.CARGO_VENDEDOR:
            self.mostrar_pdv(usuario)
        else:
            self.mostrar_dashboard(usuario)

    def mostrar_dashboard(self, usuario):
        self.usuario_autenticado = usuario
        self._limpar_container()
        frame = DashboardFrame(
            self.container,
            usuario=usuario,
            produto_aplicacao=self.produto_aplicacao,
            app=self,
        )
        frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_produtos(self):
        self._limpar_container()
        frame = ProdutosFrame(
            self.container,
            repositorio=self.repositorio_produto,
            aplicacao=self.produto_aplicacao,
            app=self,
        )
        frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_pdv(self, usuario):
        self._limpar_container()
        frame = PDVFrame(
            self.container,
            usuario=usuario,
            repositorio_produto=self.repositorio_produto,
            app=self,
        )
        frame.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        self.usuario_autenticado = None
        self.mostrar_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()
