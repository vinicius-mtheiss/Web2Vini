"""DTOs Pydantic de `category` (entrada e saída)."""

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class CategoryUpdate(BaseModel):
    """Atualização parcial: só o que vier no corpo é alterado."""

    name: str | None = Field(default=None, min_length=1, max_length=200)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str
