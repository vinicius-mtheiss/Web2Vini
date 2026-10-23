"""Entidade `product`: apenas a tabela, sem regra de negócio.

`stock` e `active` não existem no diagrama original — foram acrescentadas para
sustentar o contrato de estoque e a exclusão lógica.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:  # evita import circular em tempo de execução
    from app.models.category import Category


class Product(Base):
    __tablename__ = "product"

    product_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("category.category_id"), nullable=False
    )

    category: Mapped["Category"] = relationship(back_populates="products")
