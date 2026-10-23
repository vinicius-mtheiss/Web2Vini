"""Camada de acesso a dados — o seu `JpaRepository`, escrito à mão."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.produtos.models import Produto


class ProdutoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, skip: int = 0, limit: int = 20) -> list[Produto]:
        stmt = select(Produto).offset(skip).limit(limit).order_by(Produto.id)
        return list(self.db.scalars(stmt))

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        return self.db.get(Produto, produto_id)

    def buscar_por_nome(self, nome: str) -> Produto | None:
        return self.db.scalars(select(Produto).where(Produto.nome == nome)).first()

    def salvar(self, produto: Produto) -> Produto:
        self.db.add(produto)
        self.db.commit()
        self.db.refresh(produto)  # traz de volta id e criado_em gerados pelo banco
        return produto

    def deletar(self, produto: Produto) -> None:
        self.db.delete(produto)
        self.db.commit()
