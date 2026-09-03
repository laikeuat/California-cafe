import os
import sys
from tkinter import messagebox
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from infraestrutura.repositorio_produto import repositorioProduto
from infraestrutura.repositorio_categoria import repositorioCategoria
from aplicacao.produto_aplicacao import produtoAplicacao
from interface import tema


def cadastrar_produto(master=None, on_sucesso=None):
    """
    Abre o diálogo de cadastro de produto como CTkToplevel sobre a janela
    principal (master). CTkToplevel é o jeito correto de abrir uma janela
    secundária - diferente de instanciar um novo ctk.CTk(), não quebra o
    tema/escala globais do CustomTkinter.

    on_sucesso: callback opcional chamado após cadastrar com sucesso
    (ex: para atualizar o dashboard).
    """

    # Estado da imagem selecionada, local a esta chamada (não mais uma
    # variável global do módulo, que causava bugs se o diálogo fosse
    # aberto mais de uma vez na mesma execução).
    estado = {"imagem_binaria": None}

    def carregar_categorias():
        """Busca as categorias no banco e devolve um dict {nome: id}."""
        repositorio_cat = repositorioCategoria()
        categorias = repositorio_cat.listar_categorias()
        return {c.nome_categoria: c.id for c in categorias}

    mapa_categorias = carregar_categorias()

    def salvar_produto():
        cod_barras = cod_barras_var.get()
        nome = nome_var.get()
        quantidade = quantidade_var.get()
        cnpj_fornecedor = cnpj_var.get()
        vencimento = vencimento_var.get()
        valor_compra = valor_compra_var.get()
        valor_venda = valor_venda_var.get()
        categoria_nome = categoria_var.get()

        if not all([cod_barras, nome, quantidade, cnpj_fornecedor, vencimento, valor_compra, valor_venda]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        if not categoria_nome or categoria_nome not in mapa_categorias:
            messagebox.showerror("Erro", "Selecione uma categoria!")
            return
        if not produtoAplicacao.validar_ean13(cod_barras):
            messagebox.showerror("Erro", "Código de barras inválido! (EAN-13)")
            return
        if not produtoAplicacao.validar_cnpj(cnpj_fornecedor):
            messagebox.showerror("Erro", "CNPJ inválido!")
            return
        if not estado["imagem_binaria"]:
            messagebox.showerror("Erro", "Selecione uma imagem!")
            return
        if not quantidade.isdigit():
            messagebox.showerror("Erro", "Quantidade deve ser um número!")
            return
        if not produtoAplicacao.validar_data_validade(vencimento):
            messagebox.showerror("Erro", "Data de validade inválida!")
            return

        # Antes: valores comparados/convertidos como string (bug), agora
        # validamos que são números primeiro e SÓ DEPOIS comparamos.
        if not produtoAplicacao.valor_numerico_valido(valor_compra) or \
           not produtoAplicacao.valor_numerico_valido(valor_venda):
            messagebox.showerror("Erro", "Valores devem ser numéricos!")
            return

        valor_compra_num = float(valor_compra)
        valor_venda_num = float(valor_venda)

        if valor_compra_num > valor_venda_num:
            messagebox.showerror("Erro", "Valor de compra não pode ser maior que o valor de venda!")
            return

        try:
            repositorio = repositorioProduto()
            repositorio.inserir_produto(
                cod_barras=cod_barras,
                nome=nome,
                quantidade_estoque=quantidade,
                cnpj_fornecedor=cnpj_fornecedor,
                data_validade=vencimento,
                valor_compra=valor_compra_num,
                valor_venda=valor_venda_num,
                imagem=estado["imagem_binaria"],
                id_categoria=mapa_categorias[categoria_nome],
            )
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            cadastro_toplevel.destroy()
            if on_sucesso:
                on_sucesso()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar produto: {e}")

    def selecionar_imagem():
        caminho_imagem = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if caminho_imagem:
            try:
                imagem_pil = Image.open(caminho_imagem)
                imagem_pil = imagem_pil.resize((120, 120))

                imagem_ctk = ctk.CTkImage(dark_image=imagem_pil, size=(120, 120))

                imagem_label.configure(image=imagem_ctk, text="")
                imagem_label.image = imagem_ctk

                with open(caminho_imagem, "rb") as file:
                    estado["imagem_binaria"] = file.read()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")

    def nova_categoria():
        """Abre um mini-diálogo para cadastrar uma categoria nova sem
        sair da tela de cadastro de produto. Ao salvar, recarrega a
        lista do dropdown e já seleciona a categoria recém-criada."""

        def salvar_categoria():
            nome_cat = nome_cat_var.get().strip()
            descricao_cat = caixa_descricao_cat.get("1.0", "end").strip()

            if not nome_cat:
                messagebox.showerror("Erro", "Informe o nome da categoria!")
                return

            try:
                repositorio_cat = repositorioCategoria()
                repositorio_cat.inserir_categoria(nome=nome_cat, descricao=descricao_cat)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar categoria: {e}")
                return

            nonlocal mapa_categorias
            mapa_categorias = carregar_categorias()
            combo_categoria.configure(values=list(mapa_categorias.keys()))
            categoria_var.set(nome_cat)

            messagebox.showinfo("Sucesso", f"Categoria '{nome_cat}' cadastrada com sucesso!")
            cat_toplevel.destroy()

        cat_toplevel = ctk.CTkToplevel(cadastro_toplevel)
        cat_toplevel.title("Nova Categoria")
        cat_toplevel.geometry("420x420")
        cat_toplevel.configure(fg_color=tema.TRIGO)
        cat_toplevel.transient(cadastro_toplevel)
        cat_toplevel.grab_set()

        frame_cat = ctk.CTkFrame(
            cat_toplevel,
            fg_color=tema.CREME,
            corner_radius=20,
            width=360,
            height=380,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        frame_cat.place(relx=0.5, rely=0.5, anchor="center")
        frame_cat.pack_propagate(False)

        tema.faixa_horizonte(frame_cat).pack(fill="x", side="top")

        ctk.CTkLabel(
            frame_cat,
            text="📂  Nova Categoria",
            font=tema.titulo(20),
            text_color=tema.VERDE_ESCURO,
        ).pack(pady=(20, 16))

        nome_cat_var = ctk.StringVar()

        ctk.CTkLabel(
            frame_cat, text="Nome", font=tema.corpo(14), text_color=tema.TERRA
        ).pack(anchor="w", padx=30)
        ctk.CTkEntry(
            frame_cat,
            textvariable=nome_cat_var,
            width=300,
            height=42,
            **tema.entrada_estilo(),
        ).pack(pady=(2, 12), padx=30)

        ctk.CTkLabel(
            frame_cat, text="Descrição", font=tema.corpo(14), text_color=tema.TERRA
        ).pack(anchor="w", padx=30)
        caixa_descricao_cat = ctk.CTkTextbox(
            frame_cat,
            width=300,
            height=110,
            fg_color=tema.CREME,
            text_color=tema.TEXTO_ESCURO,
            border_color=tema.TERRA_CLARO,
            border_width=1,
            corner_radius=14,
        )
        caixa_descricao_cat.pack(pady=(2, 12), padx=30)

        ctk.CTkButton(
            frame_cat,
            text="Salvar",
            command=salvar_categoria,
            font=tema.titulo(16),
            width=160,
            height=44,
            **tema.botao_primario_estilo(),
        ).pack(pady=6)

    cadastro_toplevel = ctk.CTkToplevel(master)
    cadastro_toplevel.title("Cadastrar Produto")
    cadastro_toplevel.geometry("1000x700")
    cadastro_toplevel.configure(fg_color=tema.TRIGO)
    if master is not None:
        cadastro_toplevel.transient(master)
        cadastro_toplevel.grab_set()

    frame = ctk.CTkFrame(
        cadastro_toplevel,
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
        text="🌾  Cadastrar Produto",
        font=tema.titulo(32),
        text_color=tema.VERDE_ESCURO,
    ).place(y=45, relx=0.5, anchor="center")

    cod_barras_var = ctk.StringVar()
    nome_var = ctk.StringVar()
    quantidade_var = ctk.StringVar()
    cnpj_var = ctk.StringVar()
    vencimento_var = ctk.StringVar()
    valor_compra_var = ctk.StringVar()
    valor_venda_var = ctk.StringVar()
    categoria_var = ctk.StringVar(value="")

    imagem_label = ctk.CTkLabel(
        frame, width=130, height=130, text="", fg_color=tema.TRIGO, corner_radius=10
    )
    imagem_label.place(x=50, y=105)

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
        ("Data Vencimento", vencimento_var, 540, 160, 150),
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

    # === Categoria: dropdown + botão de criar nova ===
    ctk.CTkLabel(
        frame, text="Categoria", font=tema.corpo(15), text_color=tema.TERRA
    ).place(x=220, y=340)

    combo_categoria = ctk.CTkOptionMenu(
        frame,
        variable=categoria_var,
        values=list(mapa_categorias.keys()),
        width=380,
        height=55,
        fg_color=tema.CREME,
        text_color=tema.TEXTO_ESCURO,
        button_color=tema.VERDE_ESCURO,
        button_hover_color=tema.VERDE_ESCURO_HOVER,
        dropdown_fg_color=tema.CREME,
        dropdown_text_color=tema.TEXTO_ESCURO,
    )
    combo_categoria.place(x=220, y=365)

    ctk.CTkButton(
        frame,
        text="+",
        font=tema.titulo(18),
        width=45,
        height=55,
        command=nova_categoria,
        **tema.botao_secundario_estilo(),
    ).place(x=615, y=365)

    ctk.CTkButton(
        frame,
        text="Enviar",
        command=salvar_produto,
        font=tema.titulo(18),
        width=200,
        height=65,
        **tema.botao_primario_estilo(),
    ).place(relx=0.5, y=550, anchor="center")