"""Regras de negócio de tb_ordem"""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ordem_status.models import StatusNome
from app.ordem_status.repository import OrderStatusRepository
from app.ordem_status.services import transicao_valida
from app.tb_ordem.models import tb_ordem
from app.tb_ordem.repository import OrderRepository
from app.tb_ordem.schemas import OrderCreate


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)
        self.status_repo = OrderStatusRepository(db)

    # --- leitura --------------------------------------------------------------

    def listar(self, user_id: int | None = None, status_name: str | None = None) -> list[tb_ordem]:
        return self.repo.listar(user_id=user_id, status_name=status_name)

    def listar_por_usuario(self, user_id: int) -> list[tb_ordem]:
        """GET /users/{id}/orders: usuário que não existe é 404, não lista vazia."""
        if not self.repo.usuario_existe(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {user_id} não encontrado.",
            )
        return self.repo.listar_por_usuario(user_id)

    def buscar(self, order_id: int) -> tb_ordem:
        ordem = self.repo.buscar_por_id(order_id)
        if ordem is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido {order_id} não encontrado.",
            )
        return ordem

    # --- criação --------------------------------------------------------------

    def criar(self, dados: OrderCreate) -> tb_ordem:
        if not self.repo.usuario_existe(dados.user_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Usuário {dados.user_id} não existe.",
            )

        status_inicial = self.status_repo.buscar_por_nome(StatusNome.PENDENTE.value)
        if status_inicial is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Status 'Pendente' não está cadastrado — rode o seed antes.",
            )

        nova_ordem = tb_ordem(
            user_id=dados.user_id,
            order_status_id=status_inicial.order_status_id,
            total_value=Decimal("0.00"),
        )
        return self.repo.salvar(nova_ordem)

    # --- ciclo de vida --------------------------------------------------------

    def change_status(self, order_id: int, novo_status: StatusNome) -> tb_ordem:
        """Único ponto de entrada para mudar o status de um pedido.

        Cancelar SEMPRE passa por `cancel`, senão o PATCH /orders/{id}/status
        com "Cancelado" mudaria o status sem devolver o estoque dos itens.
        """
        if novo_status == StatusNome.CANCELADO:
            return self.cancel(order_id)
        return self._aplicar_status(self.buscar(order_id), novo_status)

    def cancel(self, order_id: int) -> tb_ordem:
        """Cancela o pedido e devolve ao estoque cada item dele.

        A transição é validada ANTES de mexer no estoque: cancelar um pedido
        já Entregue dá 409 e não devolve nada. A devolução usa o contrato do
        Vini (`restore_stock_for_order`), que por baixo chama o
        `ProductService.increase_stock` do Isac.
        """
        ordem = self.buscar(order_id)
        self._validar_transicao(ordem, StatusNome.CANCELADO)

        # Import tardio: order_item.services importa este módulo, e um import
        # no topo criaria um ciclo.
        from app.order_item.services import OrderItemService

        OrderItemService(self.db).restore_stock_for_order(order_id)
        return self._aplicar_status(self.buscar(order_id), StatusNome.CANCELADO)

    def recalculate_total(self, order_id: int) -> tb_ordem:
        """Contrato com o Vini: soma quantity * price de cada item."""
        ordem = self.buscar(order_id)
        # Recarrega os itens do banco: a coleção já carregada na sessão pode
        # estar velha se o item foi gravado direto (sem passar pela relação).
        self.db.refresh(ordem, ["itens"])
        ordem.total_value = sum(
            (item.quantity * item.price for item in ordem.itens),
            Decimal("0.00"),
        )
        return self.repo.salvar(ordem)

    # --- internos -------------------------------------------------------------

    def _validar_transicao(self, ordem: tb_ordem, novo_status: StatusNome) -> StatusNome:
        atual = StatusNome(ordem.ordem_status.status_name)
        if not transicao_valida(atual, novo_status):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transição de '{atual.value}' para '{novo_status.value}' não é permitida.",
            )
        return atual

    def _aplicar_status(self, ordem: tb_ordem, novo_status: StatusNome) -> tb_ordem:
        self._validar_transicao(ordem, novo_status)

        # Pagar (= fechar) exige item: vale também para o PATCH, não só para o
        # POST /orders/{id}/close do Vini.
        if novo_status == StatusNome.PAGO and not ordem.itens:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Pedido {ordem.order_id} não tem itens e não pode ser pago.",
            )

        novo_status_row = self.status_repo.buscar_por_nome(novo_status.value)
        if novo_status_row is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Status '{novo_status.value}' não está cadastrado — rode o seed antes.",
            )

        ordem.order_status_id = novo_status_row.order_status_id
        return self.repo.salvar(ordem)
