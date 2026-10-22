"""Ponto de entrada HTTP da API REST de pedidos."""

import logging
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request, Response, status

from app.observability import registrar
from app.repository import RepositorioPedidos
from app.schemas import PedidoEntrada, PedidoSaida, RespostaErro
from app.service import ServicoPedidos


app = FastAPI(
    title="CP5 SOA - API de Pedidos",
    description="API REST simples para criação e consulta de pedidos, com persistência em memória.",
    version="1.0.0",
)

servico_pedidos = ServicoPedidos(RepositorioPedidos())


@app.middleware("http")
async def adicionar_id_requisicao(request: Request, call_next):
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.post(
    "/pedidos",
    response_model=PedidoSaida,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
    responses={
        201: {"description": "Pedido criado com sucesso"},
        422: {"description": "Dados inválidos"},
    },
)
def criar_pedido(entrada: PedidoEntrada, request: Request, response: Response) -> PedidoSaida:
    pedido = servico_pedidos.criar(entrada)
    response.headers["Location"] = f"/pedidos/{pedido.id}"
    registrar("criar_pedido", "Pedido criado com sucesso", request.state.request_id, pedido.id)
    return pedido


@app.get(
    "/pedidos/{pedido_id}",
    response_model=PedidoSaida,
    summary="Consultar pedido por identificador",
    responses={
        404: {"model": RespostaErro, "description": "Pedido não encontrado"},
        422: {"description": "Identificador inválido"},
    },
)
def consultar_pedido(pedido_id: UUID, request: Request) -> PedidoSaida:
    pedido = servico_pedidos.buscar(pedido_id)
    if pedido is None:
        registrar(
            "consultar_pedido",
            "Pedido não encontrado",
            request.state.request_id,
            pedido_id,
            nivel=logging.WARNING,
        )
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    registrar("consultar_pedido", "Pedido consultado com sucesso", request.state.request_id, pedido_id)
    return pedido
