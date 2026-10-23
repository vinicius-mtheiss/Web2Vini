"""DTOs Pydantic de `product` (entrada e saída)."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryOut


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, max_digits=8, decimal_places=2)
    stock: int = Field(ge=0)
    category_id: int


class ProductUpdate(BaseModel):
    """Atualização parcial: só o que vier no corpo é alterado."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    price: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    active: bool | None = None
    category_id: int | None = None


class ProductOut(BaseModel):
    """A categoria vai aninhada (id + nome) para quem consome não precisar
    de uma segunda chamada."""

    model_config = ConfigDict(from_attributes=True)

    product_id: int
    name: str
    price: Decimal
    stock: int
    active: bool
    category: CategoryOut
