"""Camada de acesso a dados de tb_ordem."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.tb_ordem.models import tb_ordem
from app.usuarios.models import Usuario


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, user_id: int | None = None, status_name: str | None = None) -> list[tb_ordem]:
        stmt = select(tb_ordem).options(
            joinedload(tb_ordem.ordem_status),
            joinedload(tb_ordem.itens),
        )
        if user_id is not None:
            stmt = stmt.where(tb_ordem.user_id == user_id)
        if status_name is not None:
            stmt = stmt.join(tb_ordem.ordem_status).where(
                tb_ordem.ordem_status.has(status_name=status_name)
            )
        return list(self.db.scalars(stmt).unique())

    def buscar_por_id(self, order_id: int) -> tb_ordem | None:
        stmt = (
            select(tb_ordem)
            .options(
                joinedload(tb_ordem.ordem_status),
                joinedload(tb_ordem.itens),
            )
            .where(tb_ordem.order_id == order_id)
        )
        return self.db.scalars(stmt).unique().first()

    def listar_por_usuario(self, user_id: int) -> list[tb_ordem]:
        return self.listar(user_id=user_id)

    def usuario_existe(self, user_id: int) -> bool:
        """Checa direto na tabela de usuários. O SQLite não valida FK por
        padrão, então sem isso um pedido com user_id inventado seria gravado.
        Quando o Felipe publicar o UsuarioService/Repository, troque aqui."""
        return self.db.get(Usuario, user_id) is not None

    def salvar(self, ordem: tb_ordem) -> tb_ordem:
        self.db.add(ordem)
        self.db.commit()
        self.db.refresh(ordem)
        return ordem
