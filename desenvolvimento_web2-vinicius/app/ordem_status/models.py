from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StatusNome(str, Enum):
    PENDENTE = "Pendente"
    PAGO = "Pago"
    ENVIADO = "Enviado"
    CANCELADO = "Cancelado"
    ENTREGUE = "Entregue"


class OrderStatus(Base):
    __tablename__ = "ordem_status"

    order_status_id: Mapped[int] = mapped_column(primary_key=True)
    status_name: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str | None] = mapped_column(String(200), default=None)
