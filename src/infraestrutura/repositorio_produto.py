from infraestrutura.banco_dados import get_db
from dominio.produto import Produto
from datetime import datetime, date
from itertools import cycle
import re


class repositorioProduto:
    def __init__(self):
        pass

    def inserir_produto(
        self,
        categoria,
        cod_barras,
        nome,
        quantidade_estoque,
        cnpj_fornecedor,
        data_validade,
        valor_compra,
        valor_venda,
        imagem,
    ):
        data_validade_convertida = datetime.strptime(data_validade, "%d/%m/%Y").date()
        novo_produto = Produto(
            categoria=categoria,
            cod_barras=cod_barras,
            nome=nome,
            quantidade_estoque=quantidade_estoque,
            cnpj_fornecedor=cnpj_fornecedor,
            data_validade=data_validade_convertida,
            valor_compra=valor_compra,
            valor_venda=valor_venda,
            imagem=imagem,
        )
        with get_db() as session:
            try:
                session.add(novo_produto)
                session.commit()
            except Exception as e:
                session.rollback()
                raise Exception(f"Erro ao inserir produto: {e}")

    def buscar_produto(self, nome):
        with get_db() as session:
            return session.query(Produto).filter_by(nome=nome).first()

    def buscar_por_codigo_barras(self, cod_barras):
        with get_db() as session:
            return session.query(Produto).filter_by(cod_barras=cod_barras).first()

    def buscar_todos_produtos(self):
        with get_db() as session:
            return session.query(Produto).all()

    def remover_produto(self, id):
        with get_db() as session:
            produto = session.get(Produto, id)
            if produto:
                session.delete(produto)
                session.commit()

    def atualizar_produto(self, id_produto, categoria, nome, quantidade, cnpj_fornecedor, vencimento, valor_compra, valor_venda, imagem, cod_barras):
        with get_db() as session:
            produto = session.query(Produto).filter_by(id=id_produto).first()
            if produto is None:
                raise Exception("Produto não encontrado.")

            data_validade_convertida = datetime.strptime(vencimento, "%d/%m/%Y").date()
            produto.categoria = categoria
            produto.cod_barras = cod_barras
            produto.nome = nome
            produto.quantidade = quantidade
            produto.cnpj_fornecedor = cnpj_fornecedor
            produto.data_validade = data_validade_convertida
            produto.valor_compra = valor_compra
            produto.valor_venda = valor_venda
            produto.imagem = imagem

            session.commit()

    def dar_baixa_estoque(self, produto_id, quantidade_vendida):
        """Reduz a quantidade em estoque após uma venda no PDV."""
        with get_db() as session:
            produto = session.get(Produto, produto_id)
            if produto is None:
                raise Exception("Produto não encontrado.")
            if produto.quantidade < quantidade_vendida:
                raise Exception(f"Estoque insuficiente para '{produto.nome}'.")
            produto.quantidade -= quantidade_vendida
            session.commit()

    def buscar_todos(self):
        with get_db() as session:
            return session.query(Produto).all()
