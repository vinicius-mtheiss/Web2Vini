"""Os DTOs (Pydantic). Aqui mora a validação automática do FastAPI."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    # Field(...) == @NotBlank @Size(max = 150) do Bean Validation
    nome: str = Field(min_length=2, max_length=150)
    descricao: str | None = Field(default=None, max_length=500)
    preco: Decimal = Field(gt=0, decimal_places=2)  # @Positive
    estoque: int = Field(default=0, ge=0)
    categoria_id: int


class ProdutoCreate(ProdutoBase):
    """DTO de entrada do POST /produtos."""


class ProdutoUpdate(BaseModel):
    """DTO do PATCH: tudo opcional, só chega o que o cliente quer mudar."""

    nome: str | None = Field(default=None, min_length=2, max_length=150)
    descricao: str | None = Field(default=None, max_length=500)
    preco: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    estoque: int | None = Field(default=None, ge=0)
    categoria_id: int | None = None
    ativo: bool | None = None


class ProdutoOut(ProdutoBase):
    """DTO de saída. Note que ele nunca expõe campos internos sem querer."""

    # from_attributes: ensina o Pydantic a ler direto do objeto SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
    criado_em: datetime
