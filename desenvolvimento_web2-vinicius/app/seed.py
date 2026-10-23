"""
Popula o banco com o mínimo pra testar os endpoints no Swagger:
uma categoria, um produto, um usuário, o status PENDENTE e um pedido vazio.

Rode da raiz do projeto, com o venv ativo:
    python -m app.seed
"""

import itertools
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Enum, Integer, inspect, select

from app import models  # registra todas as classes no Base.metadata
from app.database import Base, SessionLocal, engine
from app.ordem_status.models import StatusNome

_contador = itertools.count(1)


def _modelo(tabela: str):
    """Acha a classe mapeada pra uma tabela, sem depender do nome da classe."""
    for mapper in Base.registry.mappers:
        if mapper.local_table.name == tabela:
            return mapper.class_
    raise LookupError(f"Nenhum model mapeado para a tabela '{tabela}'.")


def _valor_padrao(coluna, chave: str):
    tipo = coluna.type
    if isinstance(tipo, Enum):
        return tipo.enums[0]
    try:
        py = tipo.python_type
    except NotImplementedError:
        return None
    if py is str:
        return f"{chave}-{next(_contador)}"
    if py is bool:
        return True
    if py is int:
        return 0
    if py in (Decimal, float):
        return py(0)
    if py is datetime:
        return datetime.now()
    if py is date:
        return date.today()
    return None


def _criar(db, cls, **valores):
    """Cria e grava, preenchendo sozinho as colunas obrigatórias não informadas."""
    for attr in inspect(cls).column_attrs:
        coluna = attr.columns[0]
        if attr.key in valores or coluna.nullable or coluna.foreign_keys:
            continue
        if coluna.default is not None or coluna.server_default is not None:
            continue
        if coluna.primary_key and isinstance(coluna.type, Integer):
            continue
        valores[attr.key] = _valor_padrao(coluna, attr.key)

    obj = cls(**valores)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _obter_ou_criar(db, cls, busca: dict, **extra):
    """Reaproveita um registro existente em vez de duplicar (idempotente)."""
    existente = db.scalars(select(cls).filter_by(**busca)).first()
    if existente is not None:
        return existente
    return _criar(db, cls, **busca, **extra)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        Categoria = _modelo("category")
        Produto = _modelo("product")
        Usuario = _modelo("tb_usuarios")
        OrdemStatus = _modelo("ordem_status")
        Pedido = _modelo("tabela_ordem")

        # --- Ajuste os nomes de campo abaixo se não baterem com seu schema ---

        categoria = _obter_ou_criar(db, Categoria, busca={"name": "Categoria Teste"})
        categoria_id = inspect(categoria).identity[0]

        produto = _obter_ou_criar(
            db, Produto,
            busca={"name": "Produto Teste"},
            price=Decimal("19.90"),
            stock=50,
            active=True,
            category_id=categoria_id,
        )
        produto_id = inspect(produto).identity[0]

        usuario = db.scalars(select(Usuario)).first()
        if usuario is None:
            usuario = _criar(db, Usuario)  # campos obrigatórios preenchidos sozinhos
        usuario_id = inspect(usuario).identity[0]

        # Cria todos os status do enum, não só o PENDENTE — o change_status
        # do Lucas busca a linha pelo nome, e sem ela vira AttributeError
        # em cima de None.
        status_por_nome = {}
        for membro in StatusNome:
            linha = _obter_ou_criar(db, OrdemStatus, busca={"status_name": membro.value})
            status_por_nome[membro] = linha

        status_id = inspect(status_por_nome[StatusNome.PENDENTE]).identity[0]

        pedido = db.scalars(
            select(Pedido).filter_by(user_id=usuario_id, order_status_id=status_id)
        ).first()
        if pedido is None:
            pedido = _criar(
                db, Pedido,
                user_id=usuario_id,
                order_status_id=status_id,
                total_value=Decimal("0"),
            )
        pedido_id = inspect(pedido).identity[0]

        print("Seed concluído:")
        print(f"  categoria_id = {categoria_id}")
        print(f"  produto_id   = {produto_id}")
        print(f"  usuario_id   = {usuario_id}")
        print(f"  status_id    = {status_id}  ({StatusNome.PENDENTE.value})")
        print(f"  status criados: {[m.value for m in StatusNome]}")
        print(f"  pedido_id    = {pedido_id}")
        print()
        print(f"Teste no Swagger: POST /orders/{pedido_id}/items")
        print(f'  body: {{"product_id": {produto_id}, "quantity": 2}}')
    finally:
        db.close()


if __name__ == "__main__":
    seed()