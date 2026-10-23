from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ordem_status.models import OrderStatus, StatusNome
from app.ordem_status.repository import OrderStatusRepository

TRANSICOES_PERMITIDAS: dict[StatusNome, list[StatusNome]] = {
    # Transição de status permitida para cada status atual.
    StatusNome.PENDENTE: [StatusNome.PAGO, StatusNome.CANCELADO],
    StatusNome.PAGO: [StatusNome.ENVIADO, StatusNome.CANCELADO],
    StatusNome.ENVIADO: [StatusNome.ENTREGUE],
    StatusNome.CANCELADO: [],
    StatusNome.ENTREGUE: [],
}


def transicao_valida(atual: StatusNome, novo: StatusNome) -> bool:
    """Verifica se a transição de status é válida."""
    return novo in TRANSICOES_PERMITIDAS.get(atual, [])


class OrderStatusService:
    """Camada fina sobre o repository — na Fatia A é praticamente leitura."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderStatusRepository(db)

    def listar(self) -> list[OrderStatus]:
        return self.repo.listar()

    def buscar(self, order_status_id: int) -> OrderStatus:
        order_status = self.repo.buscar_por_id(order_status_id)
        if order_status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Status {order_status_id} não encontrado.",
            )
        return order_status

    def buscar_por_nome(self, status_name: str) -> OrderStatus:
        order_status = self.repo.buscar_por_nome(status_name)
        if order_status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Status '{status_name}' não encontrado.",
            )
        return order_status
