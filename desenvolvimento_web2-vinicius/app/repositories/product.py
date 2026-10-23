"""Acesso a dados de `product`. Sem regra de negócio, sem HTTP."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        active: bool | None = None,
    ) -> list[Product]:
        """Listagem mais usada da API: paginada e filtrável.

        `selectinload` traz a categoria junto e evita o N+1 na serialização.
        """
        stmt = select(Product).options(selectinload(Product.category))
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        if active is not None:
            stmt = stmt.where(Product.active.is_(active))
        stmt = stmt.order_by(Product.product_id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.product_id == product_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_name(self, name: str) -> Product | None:
        stmt = select(Product).where(Product.name == name)
        return self.db.scalars(stmt).first()

    def count_by_category(self, category_id: int) -> int:
        """Usado pelo CategoryService antes de apagar uma categoria."""
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(Product.category_id == category_id)
        )
        return self.db.scalar(stmt) or 0

    def save(self, product: Product) -> Product:
        """Serve para inserir e para atualizar (a sessão sabe a diferença)."""
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
