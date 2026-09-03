import re
from itertools import cycle
from datetime import date, timedelta
from infraestrutura.repositorio_produto import repositorioProduto


class produtoAplicacao:
    def __init__(self, produto_dao):
        self.produto_dao = produto_dao

    @staticmethod
    def validar_cnpj(cnpj):
        cnpj = re.sub(r"\D", "", cnpj)
        if len(cnpj) != 14:
            return False
        if cnpj in (c * 14 for c in "1234567890"):
            return False
        cnpj_r = cnpj[::-1]
        for i in range(2, 0, -1):
            cnpj_enum = zip(cycle(range(2, 10)), cnpj_r[i:])
            dv = sum(map(lambda x: int(x[1]) * x[0], cnpj_enum)) * 10 % 11
            if cnpj_r[i - 1 : i] != str(dv % 10):
                return False

        return True

    @staticmethod
    def validar_ean13(codigo: str) -> bool:
        if not codigo.isdigit() or len(codigo) != 13:
            return False
        digitos = [int(char) for char in codigo]
        soma_pares = sum(digitos[1:12:2]) * 3
        soma_impares = sum(digitos[0:12:2])
        total = soma_pares + soma_impares
        digito_calculado = (10 - (total % 10)) % 10
        return digito_calculado == digitos[12]

    def produto_vencido(self, produto):
        return produto.data_validade < date.today()

    @staticmethod
    def validar_data_validade(data_validade):
        try:
            dia, mes, ano = map(int, data_validade.split("/"))
            data = date(ano, mes, dia)
            return data >= date.today()
        except ValueError:
            return False

    @staticmethod
    def valor_numerico_valido(valor):
        """Verifica se uma string representa um número (inteiro ou decimal) válido e não-negativo."""
        try:
            return float(valor) >= 0
        except (TypeError, ValueError):
            return False
        
    def produtos_proximos_validade(self, dias=15):
        """Produtos que vencem dentro de `dias` a partir de hoje (e ainda não vencidos)."""
        hoje = date.today()
        limite = hoje + timedelta(days=dias)
        produtos = self.produto_dao.buscar_todos()
        return [p for p in produtos if hoje <= p.data_validade <= limite]

    def produtos_baixo_estoque(self, limite=10):
        """Produtos com quantidade em estoque igual ou abaixo do limite."""
        produtos = self.produto_dao.buscar_todos()
        return [p for p in produtos if p.quantidade <= limite]
    
    def calcular_valor_total(self, valor_unitario, quantidade):
        return valor_unitario * quantidade

    def calcular_lucro(self):
        produtos = self.produto_dao.buscar_todos()
        total = sum(p.lucro * p.quantidade for p in produtos)
        return total

    def contar_produtos(self):
        produtos = self.produto_dao.buscar_todos()
        total = 0
        for p in produtos:
            total += p.quantidade
        return total
