"""Entidade `category`: apenas a tabela, sem regra de negócio."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:  # evita import circular em tempo de execução
    from app.models.product import Product


class Category(Base):
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category")
