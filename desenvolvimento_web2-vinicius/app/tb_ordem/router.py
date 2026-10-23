"""O Controller de tb_ordem — o ciclo de vida do pedido."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.tb_ordem.schemas import OrderCreate, OrderOut, StatusUpdate
from app.tb_ordem.services import OrderService

router = APIRouter(tags=["Pedidos"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> OrderService:
    return OrderService(db)


Service = Annotated[OrderService, Depends(get_service)]


@router.get("/orders", response_model=list[OrderOut])
def listar_pedidos(
    service: Service,
    status_name: str | None = Query(default=None, alias="status"),
):
    return service.listar(status_name=status_name)


@router.get("/orders/{order_id}", response_model=OrderOut)
def buscar_pedido(order_id: int, service: Service):
    return service.buscar(order_id)


@router.get("/users/{user_id}/orders", response_model=list[OrderOut])
def listar_pedidos_do_usuario(user_id: int, service: Service):
    return service.listar_por_usuario(user_id)


@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def criar_pedido(dados: OrderCreate, service: Service):
    return service.criar(dados)


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def mudar_status_pedido(order_id: int, dados: StatusUpdate, service: Service):
    return service.change_status(order_id, dados.status)


@router.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancelar_pedido(order_id: int, service: Service):
    """Atalho para cancelar: muda o status para Cancelado e devolve o estoque."""
    return service.cancel(order_id)
