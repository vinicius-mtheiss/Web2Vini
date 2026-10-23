"""Controller do item de pedido — só traduz HTTP."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.order_item.schemas import ItemCreate, ItemOut, ItemUpdate
from app.order_item.services import OrderItemService

router = APIRouter(tags=["Itens de pedido"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> OrderItemService:
    return OrderItemService(db)


Service = Annotated[OrderItemService, Depends(get_service)]


@router.get(
    "/orders/{order_id}/items",
    response_model=list[ItemOut],
    status_code=status.HTTP_200_OK,
)
def listar_itens(order_id: int, service: Service):
    return service.list_items(order_id)


@router.post(
    "/orders/{order_id}/items",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_item(order_id: int, dados: ItemCreate, service: Service):
    return service.add_item(order_id, dados)


@router.patch(
    "/orders/{order_id}/items/{product_id}",
    response_model=ItemOut,
    status_code=status.HTTP_200_OK,
)
def atualizar_quantidade(
    order_id: int, product_id: int, dados: ItemUpdate, service: Service
):
    return service.update_quantity(order_id, product_id, dados)


@router.delete(
    "/orders/{order_id}/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_item(order_id: int, product_id: int, service: Service) -> None:
    service.remove_item(order_id, product_id)


# Sem response_model de propósito: não temos o schema de saída do pedido
# (é da fatia do Lucas). Se ele já tiver um PedidoOut/OrderOut, troque este
# dict por response_model=OrderOut e "return pedido" direto.
#
# Decisão do time: "fechar pedido" = status PAGO. Esta rota chama o
# change_status do Lucas por baixo; não duplica a regra de transição.
@router.post("/orders/{order_id}/close", status_code=status.HTTP_200_OK)
def fechar_pedido(order_id: int, service: Service):
    pedido = service.close_order(order_id)
    return {
        "order_id": pedido.order_id,
        "status": pedido.ordem_status.status_name,
        "total_value": str(pedido.total_value),
    }