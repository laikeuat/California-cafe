import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
from io import BytesIO

from interface import tema


class ProdutosFrame(ctk.CTkFrame):
    def __init__(self, master, repositorio, aplicacao, app, **kwargs):
        super().__init__(master, fg_color=tema.TRIGO, **kwargs)

        self.repositorio = repositorio
        self.aplicacao = aplicacao
        self.app = app  # referência ao controlador da janela única (App)
        self.imagens_ctk = []  # mantém referências das imagens carregadas

        self.frame_principal = ctk.CTkFrame(
            self,
            fg_color=tema.CREME,
            corner_radius=18,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        self.frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        tema.faixa_horizonte(self.frame_principal).pack(fill="x", side="top")

        self.criar_cabecalho()

        self.lista_frame = ctk.CTkScrollableFrame(
            self.frame_principal, height=400, fg_color=tema.TRIGO, corner_radius=10
        )
        self.lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.carregar_produtos()

    def criar_cabecalho(self):
        topo = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        topo.pack(fill="x", padx=15, pady=(15, 10))

        # Antes esta tela era uma janela própria que o usuário fechava;
        # agora navega de volta para o dashboard dentro da mesma janela.
        ctk.CTkButton(
            topo,
            text="←  Voltar",
            width=100,
            height=36,
            command=lambda: self.app.mostrar_dashboard(self.app.usuario_autenticado),
            **tema.botao_secundario_estilo(),
        ).pack(side="left")

        ctk.CTkLabel(
            topo,
            text="🌾  Lista de Produtos",
            font=tema.titulo(28),
            text_color=tema.VERDE_ESCURO,
        ).pack(side="left", expand=True)

        cabecalho = ctk.CTkFrame(
            self.frame_principal, fg_color=tema.VERDE_ESCURO, height=60, corner_radius=10
        )
        cabecalho.pack(fill="x", padx=15, pady=(0, 5))

        headers = [
            "Produto",
            "Qtd.",
            "Data Validade",
            "Valor Compra",
            "Valor Venda",
            "Lucro",
        ]
        larguras = [200, 60, 130, 130, 130, 150]

        for header, largura in zip(headers, larguras):
            ctk.CTkLabel(
                cabecalho,
                text=header,
                font=tema.corpo(15),
                text_color=tema.TEXTO_CLARO,
                width=largura,
                height=45,
            ).pack(side="left", padx=5, pady=5)

    @staticmethod
    def border_radius(imagem: Image.Image, raio: int) -> Image.Image:
        mascara = Image.new("L", imagem.size, 0)
        draw = ImageDraw.Draw(mascara)
        draw.rounded_rectangle(
            [0, 0, imagem.size[0], imagem.size[1]], radius=raio, fill=255
        )

        imagem = imagem.convert("RGBA")
        imagem.putalpha(mascara)
        return imagem

    def carregar_produtos(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        produtos = self.repositorio.buscar_todos_produtos()
        if not produtos:
            ctk.CTkLabel(
                self.lista_frame,
                text="🌱  Nenhum produto cadastrado ainda.",
                text_color=tema.TERRA,
                font=tema.corpo(15),
            ).pack(pady=20)
            return
        self.imagens_ctk = []
        for produto in produtos:
            self.criar_produto_linha(produto)

    def criar_produto_linha(self, produto):
        vencido = self.aplicacao.produto_vencido(produto)
        linha = ctk.CTkFrame(
            self.lista_frame,
            fg_color=tema.CREME,
            height=50,
            corner_radius=10,
            border_width=1,
            border_color=tema.TERRA_CLARO,
        )
        linha.pack(fill="x", padx=5, pady=3)

        if vencido:
            linha.configure(fg_color=tema.TIJOLO, border_color=tema.TIJOLO_HOVER)

        cor_texto = tema.TEXTO_CLARO if vencido else tema.TEXTO_ESCURO

        imagem_ctk = None
        if produto.imagem:
            try:
                imagem_pil = Image.open(BytesIO(produto.imagem))
                imagem_pil = imagem_pil.resize((90, 90))
                imagem_pil = ProdutosFrame.border_radius(imagem_pil, raio=15)

                imagem_ctk = ctk.CTkImage(light_image=imagem_pil, size=(60, 60))
                self.imagens_ctk.append(imagem_ctk)

            except Exception as e:
                print(f"Erro ao carregar imagem do produto {produto.nome}: {e}")

        data_validade = produto.data_validade.strftime("%d/%m/%Y")
        ctk.CTkLabel(
            linha,
            image=imagem_ctk,
            text="",
            compound="left",
            text_color=cor_texto,
            anchor="w",
            width=60,
            height=40,
        ).pack(side="left", padx=5, pady=2)
        ctk.CTkLabel(
            linha,
            text=produto.nome,
            width=140,
            text_color=cor_texto,
            compound="left",
            anchor="w",
        ).pack(side="left", padx=5, pady=2)
        ctk.CTkLabel(
            linha, text=str(produto.quantidade), width=60, text_color=cor_texto
        ).pack(side="left")
        ctk.CTkLabel(
            linha,
            text=str(data_validade) + (" ⚠️" if vencido else ""),
            width=130,
            text_color=cor_texto,
        ).pack(side="left")
        ctk.CTkLabel(
            linha,
            text=f"R$ {produto.valor_compra:.2f}",
            width=130,
            text_color=cor_texto,
        ).pack(side="left")
        ctk.CTkLabel(
            linha,
            text=f"R$ {produto.valor_venda:.2f}",
            width=130,
            text_color=cor_texto,
        ).pack(side="left")
        ctk.CTkLabel(
            linha, text=f"R$ {produto.lucro:.2f}", width=110, text_color=cor_texto
        ).pack(side="left")

        botoes_frame = ctk.CTkFrame(linha, fg_color="transparent")
        botoes_frame.pack(side="right", padx=5)

        ctk.CTkButton(
            botoes_frame,
            text="Alterar",
            width=70,
            height=30,
            command=lambda p=produto: self.alterar_produtos(p),
            **tema.botao_secundario_estilo(),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botoes_frame,
            text="Remover",
            width=70,
            height=30,
            command=lambda p=produto: self.remover_produto(p),
            **tema.botao_perigo_estilo(),
        ).pack(side="left", padx=5)

    def alterar_produtos(self, produto):
        # Estado local (não mais variável global do módulo) para a imagem
        # selecionada nesta edição.
        estado = {"imagem_binaria": produto.imagem}

        def selecionar_imagem():
            caminho_imagem = filedialog.askopenfilename(
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif")]
            )
            if caminho_imagem:
                try:
                    imagem_pil = Image.open(caminho_imagem).resize((120, 120))
                    imagem_ctk = ctk.CTkImage(dark_image=imagem_pil, size=(120, 120))
                    imagem_label.configure(image=imagem_ctk, text="")
                    imagem_label.image = imagem_ctk

                    with open(caminho_imagem, "rb") as file:
                        estado["imagem_binaria"] = file.read()

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")

        def salvar_alteracoes():
            cod_barras = cod_barras_var.get()
            nome = nome_var.get()
            quantidade = quantidade_var.get()
            cnpj_fornecedor = cnpj_var.get()
            data_validade = data_validade_var.get()
            valor_compra = valor_compra_var.get()
            valor_venda = valor_venda_var.get()

            if not all(
                [cod_barras, nome, quantidade, cnpj_fornecedor, data_validade, valor_compra, valor_venda]
            ):
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            if not self.aplicacao.validar_ean13(cod_barras):
                messagebox.showerror("Erro", "Código de barras inválido! (EAN-13)")
                return
            if not self.aplicacao.validar_cnpj(cnpj_fornecedor):
                messagebox.showerror("Erro", "CNPJ inválido!")
                return
            if not self.aplicacao.validar_data_validade(data_validade):
                messagebox.showerror("Erro", "Data de validade inválida!")
                return
            if not quantidade.isdigit():
                messagebox.showerror("Erro", "Quantidade deve ser um número!")
                return
            if not self.aplicacao.valor_numerico_valido(valor_compra) or \
               not self.aplicacao.valor_numerico_valido(valor_venda):
                messagebox.showerror("Erro", "Valores devem ser numéricos!")
                return

            valor_compra_num = float(valor_compra)
            valor_venda_num = float(valor_venda)
            if valor_compra_num > valor_venda_num:
                messagebox.showerror("Erro", "Valor de compra não pode ser maior que o valor de venda!")
                return

            try:
                self.repositorio.atualizar_produto(
                    produto.id,
                    nome,
                    quantidade,
                    cnpj_fornecedor,
                    data_validade,
                    valor_compra_num,
                    valor_venda_num,
                    estado["imagem_binaria"],
                    cod_barras,
                )
                messagebox.showinfo("Sucesso", "Produto alterado com sucesso!")
                self.carregar_produtos()
                top_level.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")

        top_level = ctk.CTkToplevel(self)
        top_level.title("Alterar Produto")
        top_level.geometry("1000x700")
        top_level.configure(fg_color=tema.TRIGO)
        top_level.transient(self.winfo_toplevel())
        top_level.grab_set()

        frame = ctk.CTkFrame(
            top_level,
            width=800,
            height=600,
            corner_radius=20,
            fg_color=tema.CREME,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)

        tema.faixa_horizonte(frame).place(x=0, y=0, relwidth=1)

        ctk.CTkLabel(
            frame,
            text="Alterar Produto",
            font=tema.titulo(32),
            text_color=tema.VERDE_ESCURO,
        ).place(y=45, relx=0.5, anchor="center")

        cod_barras_var = ctk.StringVar(value=produto.cod_barras)
        nome_var = ctk.StringVar(value=produto.nome)
        quantidade_var = ctk.StringVar(value=str(produto.quantidade))
        cnpj_var = ctk.StringVar(value=produto.cnpj_fornecedor)
        data_validade_var = ctk.StringVar(value=produto.data_validade.strftime("%d/%m/%Y"))
        valor_compra_var = ctk.StringVar(value=str(produto.valor_compra))
        valor_venda_var = ctk.StringVar(value=str(produto.valor_venda))

        imagem_label = ctk.CTkLabel(
            frame,
            width=130,
            height=130,
            text="",
            fg_color=tema.TRIGO,
            corner_radius=10,
        )
        imagem_label.place(x=50, y=105)

        try:
            if produto.imagem:
                imagem_pil = Image.open(BytesIO(produto.imagem)).resize((120, 120))
                imagem_ctk = ctk.CTkImage(dark_image=imagem_pil, size=(120, 120))
                imagem_label.configure(image=imagem_ctk)
                imagem_label.image = imagem_ctk
        except Exception as e:
            print("Erro ao carregar imagem do produto:", e)

        ctk.CTkButton(
            frame,
            text="📁",
            font=("Arial", 18),
            width=30,
            height=30,
            command=selecionar_imagem,
            fg_color="transparent",
            text_color=tema.TERRA,
            hover_color=tema.TRIGO,
        ).place(x=90, y=240)

        campos = [
            ("Cód. de Barras", cod_barras_var, 220, 80, 220),
            ("Nome", nome_var, 460, 80, 260),
            ("Qnt.", quantidade_var, 220, 160, 85),
            ("CNPJ Fornecedor", cnpj_var, 320, 160, 200),
            ("Data Vencimento", data_validade_var, 540, 160, 150),
            ("Valor de Compra", valor_compra_var, 220, 250, 200),
            ("Valor de Venda", valor_venda_var, 440, 250, 200),
        ]

        for label_text, var, x, y, largura in campos:
            ctk.CTkLabel(
                frame, text=label_text, font=tema.corpo(15), text_color=tema.TERRA
            ).place(x=x, y=y)
            ctk.CTkEntry(
                frame,
                textvariable=var,
                width=largura,
                height=55,
                **tema.entrada_estilo(),
            ).place(x=x, y=y + 25)

        ctk.CTkButton(
            frame,
            text="Salvar Alterações",
            command=salvar_alteracoes,
            font=tema.titulo(18),
            width=220,
            height=65,
            **tema.botao_primario_estilo(),
        ).place(relx=0.5, y=550, anchor="center")

    def remover_produto(self, produto):
        confirmacao = messagebox.askyesno(
            "Confirmação", f"Remover o produto '{produto.nome}'?"
        )
        if confirmacao:
            self.repositorio.remover_produto(produto.id)
            self.carregar_produtos()
            messagebox.showinfo("Sucesso", "Produto removido com sucesso!")
        else:
            messagebox.showinfo("Cancelado", "Operação cancelada.")
