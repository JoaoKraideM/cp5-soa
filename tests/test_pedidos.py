"""Testes automatizados dos requisitos centrais da API."""

import json
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_criar_pedido_retorna_201_e_dados_corretos():
    resposta = client.post(
        "/pedidos",
        json={"cliente": "Maria Silva", "descricao": "Teclado mecânico", "valor": 249.90},
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    assert UUID(dados["id"])
    assert dados["cliente"] == "Maria Silva"
    assert dados["descricao"] == "Teclado mecânico"
    assert dados["valor"] == 249.90
    assert dados["status"] == "CRIADO"
    assert resposta.headers["Location"] == f"/pedidos/{dados['id']}"
    assert resposta.headers["X-Request-ID"]


def test_consultar_pedido_existente_retorna_200():
    criado = client.post(
        "/pedidos",
        json={"cliente": "Joana", "descricao": "Mouse", "valor": 120.0},
    )
    pedido_id = criado.json()["id"]

    consulta = client.get(f"/pedidos/{pedido_id}")

    assert consulta.status_code == 200
    assert consulta.json() == criado.json()


def test_consultar_pedido_inexistente_retorna_404():
    resposta = client.get("/pedidos/00000000-0000-0000-0000-000000000000")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pedido não encontrado."}


def test_dados_invalidos_retorna_422():
    resposta = client.post(
        "/pedidos",
        json={"cliente": "  ", "descricao": "Mouse", "valor": -10},
    )

    assert resposta.status_code == 422
    assert len(resposta.json()["detail"]) >= 2


def test_log_de_criacao_e_json_estruturado():
    resposta = client.post(
        "/pedidos",
        json={"cliente": "Equipe", "descricao": "Monitor", "valor": 500},
    )

    # Valida o formato do evento com o ID real de uma requisição à API.
    import logging
    from app.observability import FormatadorJSON

    registro = logging.LogRecord(
        name="cp5.soa.pedidos",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Pedido criado com sucesso",
        args=(),
        exc_info=None,
    )
    registro.operacao = "criar_pedido"
    registro.request_id = resposta.headers["X-Request-ID"]
    registro.pedido_id = UUID(resposta.json()["id"])
    log = json.loads(FormatadorJSON().format(registro))

    assert log["timestamp"].endswith("Z")
    assert log["level"] == "INFO"
    assert log["operacao"] == "criar_pedido"
    assert log["mensagem"] == "Pedido criado com sucesso"
    assert log["requestId"] == resposta.headers["X-Request-ID"]
    assert log["pedidoId"] == resposta.json()["id"]
