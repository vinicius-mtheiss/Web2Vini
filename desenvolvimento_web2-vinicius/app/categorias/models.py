from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.produtos.models import Produto


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(255), default=None)

    produtos: Mapped[list["Produto"]] = relationship(back_populates="categoria")