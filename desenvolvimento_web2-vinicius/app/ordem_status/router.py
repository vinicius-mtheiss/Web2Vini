"""O Controller de order_status, só leitura, como o enunciado pede."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ordem_status.schemas import OrderStatusOut
from app.ordem_status.services import OrderStatusService
from app.database import get_db

router = APIRouter(prefix="/ordem-status", tags=["Ordem Status"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> OrderStatusService:
    return OrderStatusService(db)


Service = Annotated[OrderStatusService, Depends(get_service)]


@router.get("", response_model=list[OrderStatusOut])
def listar_status(service: Service):
    return service.listar()


@router.get("/{order_status_id}", response_model=OrderStatusOut)
def buscar_status(order_status_id: int, service: Service):
    return service.buscar(order_status_id)
