"""Regras de negócio do item de pedido.

Uma transação só: se qualquer passo falhar, nada fica gravado. O preço
nunca vem do cliente — é copiado do catálogo. Estoque só muda via
ProductService; o total do pedido só muda via OrderService.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.ordem_status.models import StatusNome
from app.order_item.models import OrderItem
from app.order_item.repository import OrderItemRepository
from app.order_item.schemas import ItemCreate, ItemUpdate
from app.services.product import ProductService
from app.tb_ordem.models import tb_ordem
from app.tb_ordem.services import OrderService


class OrderItemService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderItemRepository(db)
        self.products = ProductService(db)
        self.orders = OrderService(db)

    def add_item(self, order_id: int, dados: ItemCreate) -> OrderItem:
        try:
            ordem = self._pedido_aberto(order_id)
            if self.repo.get(order_id, dados.product_id) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Produto {dados.product_id} já está no pedido {order_id}."
                    ),
                )

            produto = self._produto_ativo(dados.product_id)

            item = OrderItem(
                order_id=ordem.order_id,
                product_id=produto.product_id,
                price=produto.price,
                quantity=dados.quantity,
            )
            self.repo.save(item)
            self.products.decrease_stock(produto.product_id, dados.quantity)
            self.orders.recalculate_total(order_id)
            self.db.commit()
            return self._obrigatorio(order_id, dados.product_id)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def update_quantity(
        self, order_id: int, product_id: int, dados: ItemUpdate
    ) -> OrderItem:
        try:
            self._pedido_aberto(order_id)
            item = self._obrigatorio(order_id, product_id)
            delta = dados.quantity - item.quantity

            if delta > 0:
                self.products.decrease_stock(product_id, delta)
            elif delta < 0:
                self.products.increase_stock(product_id, -delta)

            item.quantity = dados.quantity
            self.repo.save(item)
            self.orders.recalculate_total(order_id)
            self.db.commit()
            return self._obrigatorio(order_id, product_id)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def remove_item(self, order_id: int, product_id: int) -> None:
        try:
            self._pedido_aberto(order_id)
            item = self._obrigatorio(order_id, product_id)
            self.products.increase_stock(product_id, item.quantity)
            self.repo.delete(item)
            self.orders.recalculate_total(order_id)
            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def list_items(self, order_id: int) -> list[OrderItem]:
        """Lista os itens de um pedido. 404 se o pedido não existir."""
        self.orders.buscar(order_id)
        return self.repo.list_by_order(order_id)

    def close_order(self, order_id: int) -> tb_ordem:
        """
        Fecha o pedido: exige pelo menos um item e marca como pago.

        Decisão do time: "fechado" = StatusNome.PAGO. Esta rota é um atalho
        de conveniência sobre o change_status do Lucas, exposta no Swagger
        para não precisar chamar o PATCH /orders/{id}/status manualmente.
        """
        try:
            self._pedido_aberto(order_id)  # 409 se já não estiver PENDENTE

            itens = self.repo.list_by_order(order_id)
            if not itens:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Pedido {order_id} não tem itens e não pode ser fechado.",
                )

            pedido = self.orders.change_status(order_id, StatusNome.PAGO)
            self.db.commit()
            return pedido
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def restore_stock_for_order(self, order_id: int) -> None:
        """Contrato com o Lucas: ao cancelar, devolve o estoque de cada item."""
        try:
            for item in self.repo.list_by_order(order_id):
                self.products.increase_stock(item.product_id, item.quantity)
            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def _pedido_aberto(self, order_id: int) -> tb_ordem:
        ordem = self.orders.buscar(order_id)
        atual = StatusNome(ordem.ordem_status.status_name)
        if atual != StatusNome.PENDENTE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Pedido {order_id} já fechado (status '{atual.value}')."
                ),
            )
        return ordem

    def _produto_ativo(self, product_id: int) -> Product:
        produto = self.products.get(product_id)
        if not produto.active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Produto {product_id} está inativo.",
            )
        return produto

    def _obrigatorio(self, order_id: int, product_id: int) -> OrderItem:
        item = self.repo.get(order_id, product_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Item do produto {product_id} não encontrado "
                    f"no pedido {order_id}."
                ),
            )
        return item