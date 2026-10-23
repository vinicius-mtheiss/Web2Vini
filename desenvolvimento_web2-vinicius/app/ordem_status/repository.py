"""Camada de acesso a dados de order_status."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ordem_status.models import OrderStatus


class OrderStatusRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self) -> list[OrderStatus]:
        stmt = select(OrderStatus).order_by(OrderStatus.order_status_id)
        return list(self.db.scalars(stmt))

    def buscar_por_id(self, order_status_id: int) -> OrderStatus | None:
        return self.db.get(OrderStatus, order_status_id)

    def buscar_por_nome(self, status_name: str) -> OrderStatus | None:
        stmt = select(OrderStatus).where(OrderStatus.status_name == status_name)
        return self.db.scalars(stmt).first()
