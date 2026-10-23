"""Contrato HTTP do item: o cliente nunca envia preço."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class ItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    product_id: int
    quantity: int
    price: Decimal
    product_name: str
    subtotal: Decimal
