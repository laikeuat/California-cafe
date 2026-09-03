import customtkinter as ctk
from tkinter import messagebox

from interface import tema
from infraestrutura.mercado_pago_service import MercadoPagoService


class PDVFrame(ctk.CTkFrame):
    """
    Tela de Ponto de Venda - acesso exclusivo do Vendedor.

    Fluxo: digita/escaneia o código de barras -> Enter -> produto entra
    no carrinho -> repete pro próximo item -> "Finalizar Venda" dá baixa
    no estoque de cada item vendido.

    O Vendedor não tem acesso a cadastro/edição de produto aqui (essas
    ações continuam restritas ao Dashboard do Gerente).
    """

    def __init__(self, master, usuario, repositorio_produto, app, **kwargs):
        super().__init__(master, fg_color=tema.TRIGO, **kwargs)

        self.usuario = usuario
        self.repositorio_produto = repositorio_produto
        self.app = app

        self.carrinho = []  # lista de dicts: {produto, quantidade}
        self.pagamento = MercadoPagoService()

        self.criar_interface()
        self.entry_codigo.focus_set()

    def criar_interface(self):
        self.pack(fill="both", expand=True)

        # === Cabeçalho ===
        cabecalho = ctk.CTkFrame(self, fg_color=tema.VERDE_ESCURO, height=70, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)

        ctk.CTkLabel(
            cabecalho,
            text="🧾  Ponto de Venda",
            font=tema.titulo(24),
            text_color=tema.TEXTO_CLARO,
        ).pack(side="left", padx=25)

        ctk.CTkLabel(
            cabecalho,
            text=f"Vendedor(a): {self.usuario.nome}",
            font=tema.corpo(14),
            text_color=tema.VERDE_CLARO,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            cabecalho,
            text="Sair",
            command=self.app.logout,
            width=100,
            height=36,
            **tema.botao_perigo_estilo(),
        ).pack(side="right", padx=25)

        # Label de status/confirmação discreta (sem popups pra sucesso)
        self.label_status = ctk.CTkLabel(
            cabecalho, text="", font=tema.corpo(14), text_color=tema.VERDE_CLARO
        )
        self.label_status.pack(side="right", padx=10)

        # === Corpo: leitor + carrinho (esquerda) / resumo (direita) ===
        corpo = ctk.CTkFrame(self, fg_color=tema.TRIGO)
        corpo.pack(fill="both", expand=True, padx=20, pady=20)

        coluna_esquerda = ctk.CTkFrame(corpo, fg_color="transparent")
        coluna_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # --- Campo de leitura de código de barras ---
        leitor_frame = ctk.CTkFrame(
            coluna_esquerda,
            fg_color=tema.CREME,
            corner_radius=16,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        leitor_frame.pack(fill="x", pady=(0, 15))
        tema.faixa_horizonte(leitor_frame, altura=6).pack(fill="x", side="top")

        ctk.CTkLabel(
            leitor_frame,
            text="Código de barras",
            font=tema.corpo(14),
            text_color=tema.TERRA,
        ).pack(anchor="w", padx=20, pady=(15, 2))

        self.codigo_var = ctk.StringVar()
        self.entry_codigo = ctk.CTkEntry(
            leitor_frame,
            textvariable=self.codigo_var,
            width=400,
            height=48,
            font=tema.corpo(16),
            **tema.entrada_estilo(),
        )
        self.entry_codigo.pack(anchor="w", padx=20, pady=(0, 18))
        self.entry_codigo.bind("<Return>", lambda event: self.adicionar_ao_carrinho())

        # --- Lista do carrinho ---
        carrinho_frame = ctk.CTkFrame(
            coluna_esquerda,
            fg_color=tema.CREME,
            corner_radius=16,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        carrinho_frame.pack(fill="both", expand=True)
        tema.faixa_horizonte(carrinho_frame, altura=6).pack(fill="x", side="top")

        cabecalho_lista = ctk.CTkFrame(carrinho_frame, fg_color=tema.VERDE_ESCURO, height=50)
        cabecalho_lista.pack(fill="x", padx=15, pady=(15, 8))
        cabecalho_lista.pack_propagate(False)

        # (texto, peso-de-coluna, alinhamento) - os mesmos pesos são usados
        # nas linhas do carrinho, pra alinhar cabeçalho com dados mesmo
        # quando a janela é redimensionada.
        self.colunas_carrinho = [
            ("Produto", 3, "w"),
            ("Qtd.", 1, "center"),
            ("Unit.", 2, "e"),
            ("Subtotal", 2, "e"),
            ("", 2, "center"),
        ]
        for i, (texto, peso, alinhamento) in enumerate(self.colunas_carrinho):
            cabecalho_lista.grid_columnconfigure(i, weight=peso, minsize=70)
            ctk.CTkLabel(
                cabecalho_lista, text=texto, font=tema.corpo(15),
                text_color=tema.TEXTO_CLARO, anchor=alinhamento,
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=10)

        self.lista_carrinho = ctk.CTkScrollableFrame(
            carrinho_frame, fg_color=tema.TRIGO, corner_radius=10
        )
        self.lista_carrinho.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # --- Coluna direita: resumo/total ---
        coluna_direita = ctk.CTkFrame(
            corpo,
            fg_color=tema.CREME,
            corner_radius=16,
            width=280,
            border_width=2,
            border_color=tema.TERRA_CLARO,
        )
        coluna_direita.pack(side="right", fill="y")
        coluna_direita.pack_propagate(False)
        tema.faixa_horizonte(coluna_direita, altura=6).pack(fill="x", side="top")

        ctk.CTkLabel(
            coluna_direita, text="Total da venda", font=tema.corpo(15), text_color=tema.TERRA
        ).pack(pady=(30, 4))

        self.label_total = ctk.CTkLabel(
            coluna_direita, text="R$ 0,00", font=tema.titulo(34), text_color=tema.VERDE_ESCURO
        )
        self.label_total.pack(pady=(0, 30))

        self.btn_finalizar = ctk.CTkButton(
            coluna_direita,
            text="Finalizar Venda",
            command=self.finalizar_venda,
            font=tema.titulo(18),
            width=220,
            height=60,
            **tema.botao_primario_estilo(),
        )
        self.btn_finalizar.pack(pady=10)

        ctk.CTkButton(
            coluna_direita,
            text="Limpar Carrinho",
            command=self.limpar_carrinho,
            font=tema.corpo(15),
            width=220,
            height=40,
            **tema.botao_secundario_estilo(),
        ).pack(pady=10)

    # ---- Lógica do carrinho --------------------------------------------

    def adicionar_ao_carrinho(self):
        codigo = self.codigo_var.get().strip()
        self.codigo_var.set("")
        self.entry_codigo.focus_set()

        if not codigo:
            return

        produto = self.repositorio_produto.buscar_por_codigo_barras(codigo)
        if produto is None:
            self._mostrar_status("Produto não encontrado", tema.TIJOLO)
            return

        if produto.quantidade <= 0:
            self._mostrar_status(f"'{produto.nome}' sem estoque", tema.TIJOLO)
            return

        # Se o produto já está no carrinho, só incrementa a quantidade
        for item in self.carrinho:
            if item["produto"].id == produto.id:
                if item["quantidade"] + 1 > produto.quantidade:
                    self._mostrar_status("Quantidade acima do estoque", tema.TIJOLO)
                    return
                item["quantidade"] += 1
                self._renderizar_carrinho()
                self._mostrar_status(f"+1 {produto.nome}", tema.VERDE_CLARO)
                return

        self.carrinho.append({"produto": produto, "quantidade": 1})
        self._renderizar_carrinho()
        self._mostrar_status(f"{produto.nome} adicionado", tema.VERDE_CLARO)

    def _mostrar_status(self, texto, cor, persistente=False):
        """
        persistente=True: fica na tela até outra chamada trocar/limpar
        (usado enquanto aguarda pagamento na maquininha). Sem isso, some
        sozinho em 1.5s (usado pra confirmações rápidas tipo 'produto
        adicionado').
        """
        self.label_status.configure(text=texto, text_color=cor)
        if not persistente:
            self.after(1500, lambda: self.label_status.configure(text=""))

    def _renderizar_carrinho(self):
        for widget in self.lista_carrinho.winfo_children():
            widget.destroy()

        total = 0.0
        for item in self.carrinho:
            produto = item["produto"]
            quantidade = item["quantidade"]
            subtotal = produto.valor_venda * quantidade
            total += subtotal

            linha = ctk.CTkFrame(
                self.lista_carrinho, fg_color=tema.CREME, height=64,
                corner_radius=12, border_width=1, border_color=tema.TERRA_CLARO,
            )
            linha.pack(fill="x", pady=5, padx=2)
            linha.pack_propagate(False)

            for i, (_, peso, _) in enumerate(self.colunas_carrinho):
                linha.grid_columnconfigure(i, weight=peso, minsize=70)

            ctk.CTkLabel(
                linha, text=produto.nome, anchor="w", text_color=tema.TEXTO_ESCURO,
                font=tema.corpo(15), wraplength=260, justify="left",
            ).grid(row=0, column=0, sticky="ew", padx=12)

            ctk.CTkLabel(
                linha, text=str(quantidade), text_color=tema.TEXTO_ESCURO,
                font=tema.corpo(15),
            ).grid(row=0, column=1, sticky="ew", padx=5)

            # ':,.2f' formata com separador de milhar (R$ 1.234,56 em vez
            # de estourar a coluna) - antes valores grandes cortavam.
            ctk.CTkLabel(
                linha, text=f"R$ {produto.valor_venda:,.2f}", text_color=tema.TEXTO_ESCURO,
                font=tema.corpo(15), anchor="e",
            ).grid(row=0, column=2, sticky="ew", padx=10)

            ctk.CTkLabel(
                linha, text=f"R$ {subtotal:,.2f}", text_color=tema.VERDE_ESCURO,
                font=(tema.FONTE_CORPO, 16, "bold"), anchor="e",
            ).grid(row=0, column=3, sticky="ew", padx=10)

            ctk.CTkButton(
                linha, text="Remover", width=90, height=36, font=tema.corpo(13),
                command=lambda p=produto.id: self.remover_do_carrinho(p),
                **tema.botao_perigo_estilo(),
            ).grid(row=0, column=4, sticky="e", padx=10)

        self.label_total.configure(text=f"R$ {total:,.2f}")

    def remover_do_carrinho(self, produto_id):
        self.carrinho = [item for item in self.carrinho if item["produto"].id != produto_id]
        self._renderizar_carrinho()

    def limpar_carrinho(self):
        self.carrinho = []
        self._renderizar_carrinho()

    def finalizar_venda(self):
        if not self.carrinho:
            self._mostrar_status("Carrinho vazio", tema.TIJOLO)
            return

        total = sum(item["produto"].valor_venda * item["quantidade"] for item in self.carrinho)

        confirmar = messagebox.askyesno(
            "Confirmar venda",
            f"Finalizar venda no valor de {self.label_total.cget('text')}?",
        )
        if not confirmar:
            return

        # Sem token/terminal configurados ainda -> segue sem integração
        # com a maquininha (só dá baixa no estoque), pra não travar o
        # PDV enquanto a integração não for configurada.
        # if not self.pagamento.credenciais_configuradas():
        self._concluir_venda_local()
            # return
# 
        # self._enviar_cobranca_maquininha(total)

    def _enviar_cobranca_maquininha(self, total):
        self.btn_finalizar.configure(state="disabled", text="Enviando à maquininha...")
        self.update_idletasks()  # força redesenhar AGORA, antes da chamada de rede travar a UI
        try:
            order_id = self.pagamento.criar_cobranca(total)
            print(f"[MercadoPago] Cobrança criada. order_id={order_id}")
        except Exception as e:
            self.btn_finalizar.configure(state="normal", text="Finalizar Venda")
            messagebox.showerror("Erro", f"Não foi possível enviar a cobrança à maquininha: {e}")
            return

        self._mostrar_status("Aguardando pagamento na maquininha...", tema.TERRA, persistente=True)
        self._checar_status_pagamento(order_id)

    def _checar_status_pagamento(self, order_id):
        try:
            order = self.pagamento.consultar_status(order_id)
        except Exception as e:
            self.btn_finalizar.configure(state="normal", text="Finalizar Venda")
            messagebox.showerror("Erro", f"Erro ao consultar pagamento: {e}")
            return

        status = order.get("status")
        print(f"[MercadoPago] order_id={order_id} status='{status}' resposta_completa={order}")

        if status == "processed":
            self.btn_finalizar.configure(state="normal", text="Finalizar Venda")
            self._concluir_venda_local()
            return

        if status in ("cancelled", "error"):
            self.btn_finalizar.configure(state="normal", text="Finalizar Venda")
            self._mostrar_status("Pagamento não aprovado", tema.TIJOLO)
            return

        # Ainda 'created' ou 'processing' (cliente ainda não pagou na
        # maquininha) - continua checando a cada 2s sem travar a UI.
        self.after(2000, lambda: self._checar_status_pagamento(order_id))

    def _concluir_venda_local(self):
        """Dá baixa no estoque de cada item e limpa o carrinho."""
        try:
            for item in self.carrinho:
                self.repositorio_produto.dar_baixa_estoque(
                    item["produto"].id, item["quantidade"]
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar venda: {e}")
            return

        self.limpar_carrinho()
        self._mostrar_status("✓ Venda registrada!", tema.VERDE_CLARO)