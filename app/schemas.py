"""Contratos de entrada e saída da API."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated


Cliente = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Descricao = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class PedidoEntrada(BaseModel):
    cliente: Cliente = Field(description="Nome ou identificação do cliente", examples=["Maria Silva"])
    descricao: Descricao = Field(description="Descrição do pedido", examples=["Teclado mecânico"])
    valor: float = Field(
        gt=0,
        allow_inf_nan=False,
        description="Valor do pedido, maior que zero",
        examples=[249.90],
    )


class PedidoSaida(PedidoEntrada):
    id: UUID = Field(description="Identificador único do pedido")
    status: Literal["CRIADO"] = Field(default="CRIADO", description="Situação inicial do pedido")


class RespostaErro(BaseModel):
    detail: str = Field(examples=["Pedido não encontrado."])
