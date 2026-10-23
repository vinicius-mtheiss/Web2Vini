"""Acesso a dados de `category`. Sem regra de negócio, sem HTTP."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 100) -> list[Category]:
        stmt = select(Category).order_by(Category.category_id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        """Sustenta a regra de nome único, checada no service."""
        stmt = select(Category).where(Category.name == name)
        return self.db.scalars(stmt).first()

    def save(self, category: Category) -> Category:
        """Serve para inserir e para atualizar (a sessão sabe a diferença)."""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()
