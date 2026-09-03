"""
Tema visual da aplicação - identidade "neon noturno" do California Café Bar
(nomes de variável mantidos do tema anterior por legado, mas os valores e
papéis agora seguem a paleta escura com bordas neon).

Paleta:
    VERDE_ESCURO   #08080D  - fundo da barra lateral, botões secundários (quase preto)
    VERDE_CLARO    #FF2E9E  - rosa neon: destaques, botão de ação principal, títulos em cartão
    TRIGO          #0A0A12  - fundo geral das janelas (base escura)
    CREME          #16161F  - cartões e painéis sobre o fundo (cinza-chumbo escuro)
    TERRA          #B9B4C7  - textos secundários / labels (lilás-acinzentado, legível no escuro)
    TERRA_CLARO    #FF7FC4  - borda "neon acesa" (rosa mais claro, simula o brilho)
    TIJOLO         #FF3B5C  - alertas / produto vencido (vermelho neon)

Tipografia:
    FONTE_TITULO  - "Britannic Bold": robusto, para títulos e destaques
    FONTE_CORPO   - "Berlin Sans FB": redondo/amigável, para textos e campos

Sobre o efeito neon:
    CTk/Tkinter não suporta sombra/blur real (sem box-shadow). O "brilho" é
    simulado com duas camadas: um frame externo um pouco maior na cor mais
    clara (TERRA_CLARO) funcionando como halo, e o frame de conteúdo por
    cima, levemente menor, com a borda vivida (VERDE_CLARO). Use
    `moldura_neon()` quando quiser esse efeito completo em um card
    específico (ex: login, diálogos de cadastro). Para o resto do app, os
    frames que já usam `border_color=tema.TERRA_CLARO` continuam
    funcionando sem alteração nenhuma - só ganham a cor neon automaticamente.
"""

FONTE_TITULO = "Britannic Bold"
FONTE_CORPO = "Berlin Sans FB"

# --- Cores -----------------------------------------------------------------
VERDE_ESCURO = "#08080D"
VERDE_ESCURO_HOVER = "#17171F"
VERDE_CLARO = "#FF2E9E"
VERDE_CLARO_HOVER = "#D41C82"
TRIGO = "#0A0A12"
CREME = "#16161F"
TERRA = "#B9B4C7"
TERRA_CLARO = "#FF7FC4"
TIJOLO = "#FF3B5C"
TIJOLO_HOVER = "#CC2E49"
TEXTO_ESCURO = "#0A0A12"
TEXTO_CLARO = "#F5F0FA"

# Acento secundário (opcional) - ciano neon, útil pra diferenciar de "ação
# principal" sem recorrer a mais um tom de rosa. Não é usado por nenhuma
# função abaixo ainda, fica disponível caso queira usar em algum detalhe.
CIANO_NEON = "#39E8DE"
CIANO_NEON_HOVER = "#22B8AF"


def titulo(tamanho=30, negrito=True):
    return (FONTE_TITULO, tamanho, "bold") if negrito else (FONTE_TITULO, tamanho)


def corpo(tamanho=15):
    return (FONTE_CORPO, tamanho)


def entrada_estilo():
    """Estilo padrão para CTkEntry em todo o app - fundo escuro, borda neon fina."""
    return dict(
        fg_color=CREME,
        text_color=TEXTO_CLARO,
        border_color=TERRA_CLARO,
        border_width=1,
        corner_radius=14,
    )


def botao_primario_estilo():
    """Botão de ação principal - rosa neon com texto escuro (alto contraste)."""
    return dict(
        fg_color=VERDE_CLARO,
        hover_color=VERDE_CLARO_HOVER,
        text_color=TEXTO_ESCURO,
        corner_radius=18,
    )


def botao_secundario_estilo():
    """Botão de ação secundária - fundo quase preto, texto claro."""
    return dict(
        fg_color=VERDE_ESCURO,
        hover_color=VERDE_ESCURO_HOVER,
        text_color=TEXTO_CLARO,
        corner_radius=18,
    )


def botao_perigo_estilo():
    """Botão destrutivo (remover, sair) - vermelho neon."""
    return dict(
        fg_color=TIJOLO,
        hover_color=TIJOLO_HOVER,
        text_color=TEXTO_CLARO,
        corner_radius=18,
    )


def faixa_horizonte(parent, altura=10):
    """
    Elemento de assinatura visual: uma faixa fina de duas cores (fundo escuro
    em cima, rosa neon embaixo) usada no topo dos painéis principais.
    """
    import customtkinter as ctk

    faixa = ctk.CTkFrame(parent, height=altura, fg_color=VERDE_ESCURO, corner_radius=0)
    ctk.CTkFrame(
        faixa, height=altura // 2, fg_color=VERDE_CLARO, corner_radius=0
    ).pack(side="bottom", fill="x")
    return faixa


def moldura_neon(parent, width, height, corner_radius=22, halo=4, borda=2):
    """
    Cria um "cartão" com efeito de brilho neon simulado por camadas:

      - camada externa (halo): cor TERRA_CLARO (rosa mais claro), do
        tamanho width x height - funciona como o brilho que vaza pra fora.
      - camada interna (conteúdo): cor CREME, um pouco menor, centralizada,
        com borda sólida VERDE_CLARO (rosa neon vivo) - é onde você deve
        colocar os widgets do card.

    Retorna (externo, interno). Coloque seus widgets dentro de `interno`,
    igual você já faz com um CTkFrame comum.

    Exemplo:
        externo, cartao = tema.moldura_neon(self, width=420, height=460)
        externo.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(cartao, text="...").pack(...)
    """
    import customtkinter as ctk

    externo = ctk.CTkFrame(
        parent,
        width=width,
        height=height,
        corner_radius=corner_radius,
        fg_color=TERRA_CLARO,
    )
    externo.pack_propagate(False)

    interno = ctk.CTkFrame(
        externo,
        corner_radius=corner_radius - 2,
        fg_color=CREME,
        border_width=borda,
        border_color=VERDE_CLARO,
    )
    interno.place(
        x=halo, y=halo, width=width - halo * 2, height=height - halo * 2
    )

    return externo, interno