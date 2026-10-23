"""Camada HTTP de `category`: recebe, delega ao service, devolve."""

from fastapi import APIRouter, Query, status

from app.database import DbSession
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut], status_code=status.HTTP_200_OK)
def list_categories(
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    return CategoryService(db).list(skip=skip, limit=limit)


@router.get(
    "/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK
)
def get_category(category_id: int, db: DbSession):
    return CategoryService(db).get(category_id)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: DbSession):
    return CategoryService(db).create(data)


@router.patch(
    "/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK
)
def update_category(category_id: int, data: CategoryUpdate, db: DbSession):
    return CategoryService(db).update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: DbSession) -> None:
    CategoryService(db).delete(category_id)
