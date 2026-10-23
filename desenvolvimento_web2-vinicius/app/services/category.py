"""Regra de negócio de `category`. É aqui que o erro HTTP é decidido."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.repository = CategoryRepository(db)
        # Só para responder "esta categoria tem produtos?" sem consultar a
        # tabela de produtos direto daqui.
        self.products = ProductRepository(db)

    def list(self, skip: int = 0, limit: int = 100) -> list[Category]:
        return self.repository.list(skip=skip, limit=limit)

    def get(self, category_id: int) -> Category:
        category = self.repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria {category_id} não encontrada.",
            )
        return category

    def create(self, data: CategoryCreate) -> Category:
        if self.repository.get_by_name(data.name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma categoria com o nome '{data.name}'.",
            )
        return self.repository.save(Category(name=data.name))

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.get(category_id)

        if data.name is not None and data.name != category.name:
            if self.repository.get_by_name(data.name) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe uma categoria com o nome '{data.name}'.",
                )
            category.name = data.name

        return self.repository.save(category)

    def delete(self, category_id: int) -> None:
        category = self.get(category_id)

        vinculados = self.products.count_by_category(category_id)
        if vinculados > 0:
            # Melhor devolver 409 legível do que deixar a FK estourar como 500.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Categoria {category_id} possui {vinculados} produto(s) "
                    "vinculado(s) e não pode ser removida."
                ),
            )

        self.repository.delete(category)
