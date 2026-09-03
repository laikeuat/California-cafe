import customtkinter as ctk
from tkinter import messagebox
from interface.cadastrar_produto import cadastrar_produto
from interface import tema
from dominio.usuario import Usuario


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, usuario, produto_aplicacao, app, **kwargs):
        super().__init__(master, fg_color=tema.TRIGO, **kwargs)

        self.usuario = usuario
        self.produto_aplicacao = produto_aplicacao
        self.app = app  # referência ao controlador da janela única (App)

        self.criar_interface()

    def criar_avisos(self, parent):
        proximos_validade = self.produto_aplicacao.produtos_proximos_validade(dias=15)
        baixo_estoque = self.produto_aplicacao.produtos_baixo_estoque(limite=10)

        if proximos_validade:
            nomes = ", ".join(p.nome for p in proximos_validade[:3])
            if len(proximos_validade) > 3:
                nomes += f" e mais {len(proximos_validade) - 3}"
            self._criar_aviso(
                parent, icone="⏳",
                texto=f"{len(proximos_validade)} produto(s) vencendo em até 15 dias: {nomes}",
            )

        if baixo_estoque:
            nomes = ", ".join(p.nome for p in baixo_estoque[:3])
            if len(baixo_estoque) > 3:
                nomes += f" e mais {len(baixo_estoque) - 3}"
            self._criar_aviso(
                parent, icone="📉",
                texto=f"{len(baixo_estoque)} produto(s) com estoque baixo: {nomes}",
            )

    def _criar_aviso(self, parent, icone, texto):
        aviso = ctk.CTkFrame(
            parent, fg_color=tema.CREME, corner_radius=12,
            border_width=2, border_color=tema.TIJOLO,
        )
        aviso.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            aviso, text=f"{icone}  {texto}", font=tema.corpo(14),
            text_color=tema.TIJOLO, anchor="w",
        ).pack(fill="x", padx=20, pady=10)

    def criar_interface(self):
        self.pack(fill="both", expand=True)

        # === Barra lateral - verde-mata escuro ===
        barra_lateral = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=tema.VERDE_ESCURO,
        )
        barra_lateral.pack(side="left", fill="y")
        barra_lateral.pack_propagate(False)

        ctk.CTkLabel(
            barra_lateral, text="🌾", font=("Arial", 30), text_color=tema.VERDE_CLARO
        ).pack(pady=(40, 4))
        ctk.CTkLabel(
            barra_lateral,
            text="California\nCafé Bar",
            font=tema.titulo(19),
            text_color=tema.TEXTO_CLARO,
            justify="center",
        ).pack(pady=(0, 30))

        ctk.CTkFrame(barra_lateral, height=1, fg_color=tema.VERDE_CLARO).pack(
            fill="x", padx=30, pady=(0, 20)
        )

        ctk.CTkLabel(
            barra_lateral,
            text=f"Olá, {self.usuario.nome}",
            font=tema.corpo(15),
            text_color=tema.VERDE_CLARO,
            wraplength=200,
        ).pack(pady=(0, 30))

        # Antes: command=lambda: TelaProdutos(ctk.CTk())  -> abria uma 2ª janela
        # raiz e quebrava o app. Agora navega dentro da mesma janela.
        ctk.CTkButton(
            barra_lateral,
            text="🌱  Gerenciar Produtos",
            command=self.app.mostrar_produtos,
            width=200,
            height=50,
            anchor="w",
            **tema.botao_primario_estilo(),
        ).pack(pady=10, padx=20)

        ctk.CTkButton(
            barra_lateral,
            text="🧑‍🌾  Cadastrar Vendedor",
            command=self.cadastrar_vendedor,
            width=200,
            height=50,
            anchor="w",
            **tema.botao_secundario_estilo(),
        ).pack(pady=(0, 10), padx=20)
        ctk.CTkButton(
            barra_lateral,
            text="📂  Criar Categoria",
            command=self.cadastrar_categoria,
            width=200,
            height=50,
            anchor="w",
            **tema.botao_secundario_estilo(),
        ).pack(pady=(0, 10), padx=20)

        ctk.CTkButton(
            barra_lateral,
            text="Sair",
            command=self.app.logout,
            width=200,
            height=40,
            **tema.botao_perigo_estilo(),
        ).pack(side="bottom", pady=30, padx=20)

        # === Painel principal - creme ===
        painel_principal = ctk.CTkFrame(self, fg_color=tema.TRIGO)
        painel_principal.pack(expand=True, fill="both", padx=30, pady=30)

        self.criar_topo_lucro(painel_principal)
        self.criar_estoque(painel_principal)

    def criar_topo_lucro(self, parent):
        lucro_total = self.produto_aplicacao.calcular_lucro()
        total_produtos = self.produto_aplicacao.contar_produtos()

        frame_topo = ctk.CTkFrame(
            parent,
            fg_color=tema.CREME,
            corner_radius=18,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame_topo.pack(pady=(0, 20), padx=0, fill="x")

        tema.faixa_horizonte(frame_topo).pack(fill="x", side="top")

        conteudo = ctk.CTkFrame(frame_topo, fg_color="transparent")
        conteudo.pack(fill="x", padx=30, pady=20)

        info = ctk.CTkFrame(conteudo, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            info,
            text="Valor em estoque hoje",
            font=tema.corpo(15),
            text_color=tema.TERRA,
        ).pack(anchor="w")
        ctk.CTkLabel(
            info,
            text=f"R$ {lucro_total:,.2f}",
            font=tema.titulo(34),
            text_color=tema.VERDE_ESCURO,
        ).pack(anchor="w", pady=(2, 8))
        ctk.CTkLabel(
            info,
            text=f"🌾 {total_produtos} produtos cadastrados",
            font=tema.corpo(15),
            text_color=tema.TERRA,
        ).pack(anchor="w")

        ctk.CTkButton(
            conteudo,
            text="+ Cadastrar Produto",
            command=lambda: cadastrar_produto(
                master=self.winfo_toplevel(),
                on_sucesso=self.atualizar,
            ),
            font=tema.titulo(18),
            width=220,
            height=60,
            **tema.botao_primario_estilo(),
        ).pack(side="right")

    def criar_estoque(self, parent):
        frame_estoque = ctk.CTkFrame(
            parent,
            fg_color=tema.CREME,
            corner_radius=18,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame_estoque.pack(fill="both", expand=True)

        tema.faixa_horizonte(frame_estoque).pack(fill="x", side="top")

        ctk.CTkLabel(
            frame_estoque,
            text="🚜  Estoque - em construção...",
            font=tema.corpo(18),
            text_color=tema.TERRA,
        ).pack(pady=40)

    def atualizar(self):
        """Recarrega o dashboard (ex: após cadastrar um produto novo)."""
        self.app.mostrar_dashboard(self.usuario)

    def cadastrar_vendedor(self):
        """
        Diálogo (CTkToplevel) só acessível pelo Gerente, pra criar contas
        de Vendedor. Substitui o antigo auto-cadastro público da tela de
        login - agora só o Gerente decide quem vira Vendedor.
        """

        def salvar():
            nome = nome_var.get()
            email = email_var.get()
            senha = senha_var.get()

            if not all([nome, email, senha]):
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            if not self.app.usuario_aplicacao.validarEmail(email):
                messagebox.showerror("Erro", "Email inválido!")
                return
            if not self.app.usuario_aplicacao.verificaEmail(email):
                messagebox.showerror("Erro", "Já existe um usuário com esse e-mail!")
                return

            try:
                self.app.repositorio_usuario.inserir_usuario(
                    email=email,
                    nome=nome,
                    senha=senha,
                    cargo=Usuario.CARGO_VENDEDOR,
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar vendedor: {e}")
                return

            messagebox.showinfo("Sucesso", f"Vendedor '{nome}' cadastrado com sucesso!")
            toplevel.destroy()

        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Cadastrar Vendedor")
        toplevel.geometry("500x520")
        toplevel.configure(fg_color=tema.TRIGO)
        toplevel.transient(self.winfo_toplevel())
        toplevel.grab_set()

        frame = ctk.CTkFrame(
            toplevel,
            fg_color=tema.CREME,
            corner_radius=22,
            width=420,
            height=460,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)

        tema.faixa_horizonte(frame).pack(fill="x", side="top")

        ctk.CTkLabel(
            frame,
            text="🧑‍🌾  Cadastrar Vendedor",
            font=tema.titulo(24),
            text_color=tema.VERDE_ESCURO,
        ).pack(pady=(24, 20))

        nome_var = ctk.StringVar()
        email_var = ctk.StringVar()
        senha_var = ctk.StringVar()

        for label_text, var, mostrar in [
            ("Nome", nome_var, None),
            ("E-mail", email_var, None),
            ("Senha", senha_var, "*"),
        ]:
            ctk.CTkLabel(
                frame, text=label_text, font=tema.corpo(15), text_color=tema.TERRA
            ).pack(anchor="w", padx=40)
            ctk.CTkEntry(
                frame,
                textvariable=var,
                width=340,
                height=48,
                show=mostrar,
                **tema.entrada_estilo(),
            ).pack(pady=(2, 14), padx=40)

        ctk.CTkButton(
            frame,
            text="Salvar",
            command=salvar,
            font=tema.titulo(18),
            width=180,
            height=50,
            **tema.botao_primario_estilo(),
        ).pack(pady=10)
    def cadastrar_categoria(self):
        """
        Diálogo (CTkToplevel) para criar uma nova categoria de produto.
        Campos: nome e descrição (texto livre, multi-linha).
        """

        def salvar():
            nome = nome_var.get().strip()
            descricao = caixa_descricao.get("1.0", "end").strip()

            if not nome:
                messagebox.showerror("Erro", "Informe o nome da categoria!")
                return

            try:
                self.app.repositorio_categoria.inserir_categoria(
                    nome=nome,
                    descricao=descricao,
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar categoria: {e}")
                return

            messagebox.showinfo("Sucesso", f"Categoria '{nome}' cadastrada com sucesso!")
            toplevel.destroy()

        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Criar Categoria")
        toplevel.geometry("500x550")
        toplevel.configure(fg_color=tema.TRIGO)
        toplevel.transient(self.winfo_toplevel())
        toplevel.grab_set()

        frame = ctk.CTkFrame(
            toplevel,
            fg_color=tema.CREME,
            corner_radius=22,
            width=420,
            height=490,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)

        tema.faixa_horizonte(frame).pack(fill="x", side="top")

        ctk.CTkLabel(
            frame,
            text="📂  Criar Categoria",
            font=tema.titulo(24),
            text_color=tema.VERDE_ESCURO,
        ).pack(pady=(24, 20))

        nome_var = ctk.StringVar()

        ctk.CTkLabel(
            frame, text="Nome", font=tema.corpo(15), text_color=tema.TERRA
        ).pack(anchor="w", padx=40)
        ctk.CTkEntry(
            frame,
            textvariable=nome_var,
            width=340,
            height=48,
            **tema.entrada_estilo(),
        ).pack(pady=(2, 14), padx=40)

        ctk.CTkLabel(
            frame, text="Descrição", font=tema.corpo(15), text_color=tema.TERRA
        ).pack(anchor="w", padx=40)
        caixa_descricao = ctk.CTkTextbox(
            frame,
            width=340,
            height=140,
            fg_color=tema.CREME,
            text_color=tema.TEXTO_ESCURO,
            border_color=tema.TERRA_CLARO,
            border_width=1,
            corner_radius=14,
        )
        caixa_descricao.pack(pady=(2, 14), padx=40)

        ctk.CTkButton(
            frame,
            text="Salvar",
            command=salvar,
            font=tema.titulo(18),
            width=180,
            height=50,
            **tema.botao_primario_estilo(),
        ).pack(pady=10)