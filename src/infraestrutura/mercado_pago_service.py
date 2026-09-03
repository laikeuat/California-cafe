import uuid
import requests

from infraestrutura.config_mercado_pago import ACCESS_TOKEN, TERMINAL_ID, BASE_URL


class MercadoPagoService:
    """
    Integração com a API de Orders do Mercado Pago Point, para enviar
    cobranças diretamente ao terminal (Point Smart) a partir do PDV.

    IMPORTANTE: esta API está em transição no Mercado Pago - o formato
    exato do payload de 'criar_cobranca' pode mudar. Teste em sandbox e
    confira a documentação atual em:
    https://www.mercadopago.com.br/developers/pt/docs/mp-point/overview
    """

    def __init__(self):
        # Só os headers fixos ficam aqui. O X-Idempotency-Key NÃO fica
        # aqui - cada requisição de escrita (POST/PATCH) precisa da sua
        # própria chave única, senão o Mercado Pago trata chamadas
        # seguintes como repetição da primeira e ignora/erra.
        self.headers_base = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    def _headers_com_idempotencia(self):
        return {**self.headers_base, "X-Idempotency-Key": str(uuid.uuid4())}

    @staticmethod
    def _levantar_erro_detalhado(resposta):
        """
        resposta.raise_for_status() sozinho perde o corpo da resposta,
        que é onde o Mercado Pago explica o motivo real do erro
        (ex: {"message": "...", "cause": [...]}). Isso mostra esse
        corpo na exceção, pra facilitar debug.
        """
        if not resposta.ok:
            raise Exception(f"HTTP {resposta.status_code} - {resposta.text}")

    def credenciais_configuradas(self):
        return bool(ACCESS_TOKEN) and ACCESS_TOKEN != "." and bool(TERMINAL_ID)

    def listar_terminais(self):
        """Chame uma vez pra descobrir o TERMINAL_ID correto."""
        resposta = requests.get(
            f"{BASE_URL}/terminals/v1/list", headers=self.headers_base, timeout=10
        )
        self._levantar_erro_detalhado(resposta)
        return resposta.json()

    def colocar_terminal_em_modo_pdv(self):
        """Muda o terminal de STANDALONE para PDV. Rode uma vez na config inicial."""
        payload = {"terminal_id": TERMINAL_ID, "operating_mode": "PDV"}
        resposta = requests.patch(
            f"{BASE_URL}/terminals/v1/setup",
            headers=self._headers_com_idempotencia(),
            json=payload,
            timeout=10,
        )
        self._levantar_erro_detalhado(resposta)
        return resposta.json()

    def criar_cobranca(self, valor_total, descricao="Venda PDV Canaã"):
        """Envia a cobrança ao terminal. Retorna o ID da order criada."""
        payload = {
            "type": "point",
            "external_reference": f"venda-{uuid.uuid4()}",
            "description": descricao,
            "transactions": {
                "payments": [{"amount": f"{valor_total:.2f}"}]
            },
            "config": {
                "point": {
                    "terminal_id": TERMINAL_ID,
                    "print_on_terminal": "no_ticket",
                }
            },
        }
        resposta = requests.post(
            f"{BASE_URL}/v1/orders",
            headers=self._headers_com_idempotencia(),
            json=payload,
            timeout=10,
        )
        self._levantar_erro_detalhado(resposta)
        return resposta.json()["id"]

    def consultar_status(self, order_id):
        """
        Status possíveis: 'created' | 'processing' (aguardando o cliente
        pagar) | 'processed' (aprovado) | 'cancelled' | 'error'.
        """
        resposta = requests.get(
            f"{BASE_URL}/v1/orders/{order_id}", headers=self.headers_base, timeout=10
        )
        self._levantar_erro_detalhado(resposta)
        return resposta.json()

    def cancelar_cobranca(self, order_id):
        resposta = requests.post(
            f"{BASE_URL}/v1/orders/{order_id}/cancel",
            headers=self._headers_com_idempotencia(),
            timeout=10,
        )
        self._levantar_erro_detalhado(resposta)
        return resposta.json()