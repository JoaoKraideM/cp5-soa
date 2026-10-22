"""Armazenamento dos pedidos exclusivamente em memória."""

from uuid import UUID

from app.schemas import PedidoSaida


class RepositorioPedidos:
    def __init__(self) -> None:
        self._pedidos: dict[UUID, PedidoSaida] = {}

    def salvar(self, pedido: PedidoSaida) -> None:
        self._pedidos[pedido.id] = pedido

    def buscar_por_id(self, pedido_id: UUID) -> PedidoSaida | None:
        return self._pedidos.get(pedido_id)
