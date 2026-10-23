from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.ordem_status.models import OrderStatus
from app.database import Base

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from app.order_item.models import OrderItem


class tb_ordem(Base):
    __tablename__ = "tabela_ordem"  # PENDENTE: confirmar nome com o grupo

    order_id: Mapped[int] = mapped_column(primary_key=True)
    total_value: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    number_nf: Mapped[int | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("tb_usuarios.usuario_id"))
    order_status_id: Mapped[int] = mapped_column(ForeignKey("ordem_status.order_status_id"))

    ordem_status: Mapped["OrderStatus"] = relationship()
    itens: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    @property
    def status(self) -> str:
        """Usado pelo OrderOut: devolve o nome do status, não o id."""
        return self.ordem_status.status_name
