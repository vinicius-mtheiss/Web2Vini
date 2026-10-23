"""Regra de negócio de `product`, incluindo o contrato de estoque.

A coluna `stock` só é alterada aqui: `decrease_stock` e `increase_stock` são o
que o service de pedidos chama ao fechar e ao cancelar um pedido.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session) -> None:
        self.repository = ProductRepository(db)
        self.categories = CategoryRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        active: bool | None = True,
    ) -> list[Product]:
        """Por padrão esconde inativos: produto desativado não some do banco,
        só sai da vitrine."""
        return self.repository.list(
            skip=skip, limit=limit, category_id=category_id, active=active
        )

    def get(self, product_id: int) -> Product:
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto {product_id} não encontrado.",
            )
        return product

    def create(self, data: ProductCreate) -> Product:
        self._ensure_category_exists(data.category_id)
        self._ensure_name_is_free(data.name)

        product = Product(
            name=data.name,
            price=data.price,
            stock=data.stock,
            category_id=data.category_id,
            active=True,
        )
        self.repository.save(product)
        return self.get(product.product_id)

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get(product_id)

        if data.category_id is not None and data.category_id != product.category_id:
            self._ensure_category_exists(data.category_id)
            product.category_id = data.category_id

        if data.name is not None and data.name != product.name:
            self._ensure_name_is_free(data.name)
            product.name = data.name

        if data.price is not None:
            product.price = data.price
        if data.stock is not None:
            product.stock = data.stock
        if data.active is not None:
            product.active = data.active

        self.repository.save(product)
        return self.get(product.product_id)

    def deactivate(self, product_id: int) -> None:
        """O que o DELETE realmente faz.

        Produto que já apareceu em pedido não pode ser apagado — a FK do item de
        pedido segura. Por isso a exclusão é lógica.
        """
        product = self.get(product_id)
        if product.active:
            product.active = False
            self.repository.save(product)

    # --- contrato de estoque (consumido pelo módulo de pedidos) ---------------

    def decrease_stock(self, product_id: int, qty: int) -> Product:
        """Baixa `qty` unidades. Recusa com 409 se não houver saldo."""
        self._ensure_positive_qty(qty)
        product = self.get(product_id)

        if qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Estoque insuficiente para o produto {product_id}: "
                    f"disponível {product.stock}, solicitado {qty}."
                ),
            )

        product.stock -= qty
        return self.repository.save(product)

    def increase_stock(self, product_id: int, qty: int) -> Product:
        """Devolve `qty` unidades ao estoque (usado no cancelamento de pedido)."""
        self._ensure_positive_qty(qty)
        product = self.get(product_id)

        product.stock += qty
        return self.repository.save(product)

    # --- validações internas -------------------------------------------------

    def _ensure_category_exists(self, category_id: int) -> None:
        if self.categories.get_by_id(category_id) is None:
            raise HTTPException(
                status_code=422,  # referência inválida
                detail=f"Categoria {category_id} não existe.",
            )

    def _ensure_name_is_free(self, name: str) -> None:
        if self.repository.get_by_name(name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um produto com o nome '{name}'.",
            )

    @staticmethod
    def _ensure_positive_qty(qty: int) -> None:
        if qty <= 0:
            raise HTTPException(
                status_code=422,  # quantidade inválida
                detail="A quantidade deve ser maior que zero.",
            )
