"""Acesso a dados de `order_item`. Sem HTTP e sem regra de negócio."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.order_item.models import OrderItem


class OrderItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _with_product(self):
        return select(OrderItem).options(selectinload(OrderItem.product))

    def get(self, order_id: int, product_id: int) -> OrderItem | None:
        stmt = self._with_product().where(
            OrderItem.order_id == order_id,
            OrderItem.product_id == product_id,
        )
        return self.db.scalars(stmt).first()

    def list_by_order(self, order_id: int) -> list[OrderItem]:
        stmt = (
            self._with_product()
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.product_id)
        )
        return list(self.db.scalars(stmt).all())

    def save(self, item: OrderItem) -> OrderItem:
        """Persiste sem commit: o service confirma a transação no fim."""
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def delete(self, item: OrderItem) -> None:
        self.db.delete(item)
        self.db.flush()
