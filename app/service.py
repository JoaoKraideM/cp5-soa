"""Lógica de negócio para criação e consulta de pedidos."""

from uuid import UUID, uuid4

from app.repository import RepositorioPedidos
from app.schemas import PedidoEntrada, PedidoSaida


class ServicoPedidos:
    def __init__(self, repositorio: RepositorioPedidos) -> None:
        self._repositorio = repositorio

    def criar(self, entrada: PedidoEntrada) -> PedidoSaida:
        pedido = PedidoSaida(
            id=uuid4(),
            cliente=entrada.cliente,
            descricao=entrada.descricao,
            valor=entrada.valor,
            status="CRIADO",
        )
        self._repositorio.salvar(pedido)
        return pedido

    def buscar(self, pedido_id: UUID) -> PedidoSaida | None:
        return self._repositorio.buscar_por_id(pedido_id)
