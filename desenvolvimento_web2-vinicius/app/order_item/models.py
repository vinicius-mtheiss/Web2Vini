"""Tabela associativa pedido ↔ produto. Sem validação e sem regra de negócio."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.product import Product

if TYPE_CHECKING:
    from app.tb_ordem.models import tb_ordem


class OrderItem(Base):
    __tablename__ = "order_item"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("tabela_ordem.order_id"), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.product_id"), primary_key=True
    )
    # Preço congelado no momento da compra — não é o preço atual do catálogo.
    price: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["tb_ordem"] = relationship(back_populates="itens")
    product: Mapped[Product] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity
