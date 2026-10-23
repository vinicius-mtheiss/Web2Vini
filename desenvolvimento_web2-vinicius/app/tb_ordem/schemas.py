"""Os DTOs (Pydantic) de tb_ordem."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.order_item.schemas import ItemOut
from app.ordem_status.models import StatusNome


class OrderCreate(BaseModel):
    """DTO de entrada do POST /orders. O pedido nasce vazio (decisão com o Vini):
    só precisa do usuário. Os itens entram depois, em POST /orders/{id}/items."""

    user_id: int


class OrderOut(BaseModel):
    """DTO de saída. Status por nome (não id), com a lista de itens embutida.

    Reaproveita o ItemOut do Vini (product_id, quantity, price congelado,
    product_name e subtotal), então o item tem o mesmo formato aqui e em
    GET /orders/{id}/items.
    """

    model_config = ConfigDict(from_attributes=True)

    order_id: int
    total_value: Decimal
    number_nf: int | None
    created_at: datetime
    user_id: int
    status: str
    itens: list[ItemOut] = []


class StatusUpdate(BaseModel):
    """DTO de entrada do PATCH /orders/{id}/status."""

    status: StatusNome
