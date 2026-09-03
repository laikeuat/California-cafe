import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import customtkinter as ctk
from tkinter import messagebox

from infraestrutura.repositorio_usuario import RepositorioUsuario
from interface import tema


class LoginFrame(ctk.CTkFrame):
    """
    Tela de login como um CTkFrame (não mais uma janela CTk() própria).

    Ao autenticar com sucesso, chama on_login_success(usuario) em vez de
    encerrar o mainloop/destruir a janela - quem decide o que acontece
    depois é o controlador da aplicação (App), que troca de tela dentro
    da mesma janela.
    """

    def __init__(self, master, usuario_aplicacao, on_login_success, **kwargs):
        super().__init__(master, fg_color=tema.TRIGO, **kwargs)

        self.usuario_aplicacao = usuario_aplicacao
        self.on_login_success = on_login_success

        self.email_var = ctk.StringVar()
        self.senha_var = ctk.StringVar()

        self.montar_interface_login()

    def montar_interface_login(self):
        # Centraliza o cartão de login dentro do frame (que ocupa a janela toda)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(
            self,
            fg_color=tema.CREME,
            corner_radius=22,
            width=734,
            height=640,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame.grid(row=0, column=0)
        frame.grid_propagate(False)

        # Faixa "horizonte" (elemento de assinatura) no topo do cartão
        tema.faixa_horizonte(frame).pack(fill="x", side="top")

        ctk.CTkLabel(
            frame, text="☕", font=("Arial", 32), text_color=tema.TERRA
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            frame,
            text="California Café Bar",
            font=tema.corpo(16),
            text_color=tema.TERRA,
        ).pack()
        ctk.CTkLabel(
            frame,
            text="Login",
            font=tema.titulo(48),
            text_color=tema.TERRA,
            width=600,
        ).pack(pady=(4, 16))

        ctk.CTkLabel(
            frame, text="E-mail", font=tema.corpo(15), text_color=tema.TERRA
        ).pack(anchor="w", padx=85)
        ctk.CTkEntry(
            frame,
            textvariable=self.email_var,
            width=410,
            height=52,
            **tema.entrada_estilo(),
        ).pack(pady=(4, 14))

        ctk.CTkLabel(
            frame, text="Senha", font=tema.corpo(15), text_color=tema.TERRA
        ).pack(anchor="w", padx=85)
        ctk.CTkEntry(
            frame,
            textvariable=self.senha_var,
            width=410,
            height=52,
            show="*",
            **tema.entrada_estilo(),
        ).pack(pady=(4, 10))

        ctk.CTkLabel(
            frame,
            text="Esqueci minha senha",
            font=(tema.FONTE_CORPO, 14, "underline"),
            text_color=tema.TERRA,
            cursor="hand2",
        ).pack(pady=6)

        self.btn_entrar = ctk.CTkButton(
            frame,
            text="Entrar",
            font=tema.titulo(20),
            command=self.login,
            width=180,
            height=52,
            **tema.botao_secundario_estilo(),
        )
        self.btn_entrar.pack(pady=(10, 8))

    def login(self):
        email = self.email_var.get()
        senha = self.senha_var.get()

        if not email or not senha:
            messagebox.showinfo("Erro", "Preencha todos os campos!")
            return

        if not self.usuario_aplicacao.validarEmail(email):
            messagebox.showinfo("Erro", "Email Inválido!")
            return

        try:
            repositorio = RepositorioUsuario()
            usuario = repositorio.buscar_usuario(email)

            if usuario and usuario.senha == senha:
                self._animar_sucesso(usuario)
            else:
                messagebox.showinfo("Erro", "Usuário ou senha inválidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar login: {e}")

    def _animar_sucesso(self, usuario):
        """
        Em vez de um popup de 'sucesso' (que só interrompe o fluxo pra
        confirmar algo óbvio), o botão 'Entrar' se transforma rapidamente
        num check de confirmação antes de trocar para o dashboard.
        """
        self.btn_entrar.configure(
            text="✓ Bem-vindo!",
            state="disabled",
            fg_color=tema.VERDE_CLARO,
            hover_color=tema.VERDE_CLARO,
            text_color=tema.VERDE_ESCURO,
        )
        self.after(550, lambda: self.on_login_success(usuario))
