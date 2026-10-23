"""Os DTOs (Pydantic) de order_status."""

from pydantic import BaseModel, ConfigDict, Field

from app.ordem_status.models import StatusNome


class OrderStatusOut(BaseModel):
    """DTO de saída. É o formato que o GET devolve pro cliente."""

    model_config = ConfigDict(from_attributes=True)

    order_status_id: int
    status_name: str
    description: str | None = None


class OrderStatusCreate(BaseModel):
    """DTO de entrada, só usado se o grupo decidir manter o POST administrativo."""

    status_name: StatusNome
    description: str | None = Field(default=None, max_length=200)
