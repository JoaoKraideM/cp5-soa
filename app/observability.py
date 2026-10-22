"""Logs JSON com timestamp, nível, operação e requestId."""

import json
import logging
import sys
from datetime import datetime, timezone
from uuid import UUID


class FormatadorJSON(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        dados = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "operacao": getattr(record, "operacao", "sistema"),
            "mensagem": record.getMessage(),
            "requestId": getattr(record, "request_id", None),
        }
        pedido_id: UUID | None = getattr(record, "pedido_id", None)
        if pedido_id is not None:
            dados["pedidoId"] = str(pedido_id)
        return json.dumps(dados, ensure_ascii=False)


logger = logging.getLogger("cp5.soa.pedidos")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FormatadorJSON())
    logger.addHandler(handler)


def registrar(operacao: str, mensagem: str, request_id: str, pedido_id: UUID | None = None, *, nivel: int = logging.INFO) -> None:
    logger.log(
        nivel,
        mensagem,
        extra={"operacao": operacao, "request_id": request_id, "pedido_id": pedido_id},
    )
