from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.product import Product
from app.tb_ordem.models import tb_ordem


def test_health(client) -> None:
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_adicionar_tres_itens_fecha_com_total_e_estoque(
    client, db: Session, ids: dict[str, int]
) -> None:
    r1 = client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["mouse"], "quantity": 2},
    )
    r2 = client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["teclado"], "quantity": 1},
    )
    r3 = client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["cabo"], "quantity": 1},
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201
    assert r1.json()["product_name"] == "Mouse"
    assert Decimal(r1.json()["subtotal"]) == Decimal("159.80")

    db.expire_all()
    pedido = db.get(tb_ordem, ids["order"])
    assert pedido.total_value == Decimal("378.80")
    assert db.get(Product, ids["mouse"]).stock == 8
    assert db.get(Product, ids["teclado"]).stock == 4
    assert db.get(Product, ids["cabo"]).stock == 0


def test_estoque_insuficiente_nao_altera_banco(
    client, db: Session, ids: dict[str, int]
) -> None:
    estoque_antes = db.get(Product, ids["cabo"]).stock
    resposta = client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["cabo"], "quantity": 2},
    )
    assert resposta.status_code == 409
    db.expire_all()
    assert db.get(Product, ids["cabo"]).stock == estoque_antes
    assert db.get(tb_ordem, ids["order"]).itens == []


def test_produto_inativo_retorna_422(client, db: Session, ids: dict[str, int]) -> None:
    produto = db.get(Product, ids["mouse"])
    produto.active = False
    db.commit()
    resposta = client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["mouse"], "quantity": 1},
    )
    assert resposta.status_code == 422


def test_pedido_fechado_retorna_409(client, ids: dict[str, int]) -> None:
    resposta = client.post(
        f"/orders/{ids['closed_order']}/items",
        json={"product_id": ids["mouse"], "quantity": 1},
    )
    assert resposta.status_code == 409


def test_atualizar_quantidade_ajusta_so_a_diferenca(
    client, db: Session, ids: dict[str, int]
) -> None:
    client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["mouse"], "quantity": 2},
    )
    resposta = client.patch(
        f"/orders/{ids['order']}/items/{ids['mouse']}",
        json={"quantity": 5},
    )
    assert resposta.status_code == 200
    assert resposta.json()["quantity"] == 5
    db.expire_all()
    assert db.get(Product, ids["mouse"]).stock == 5
    assert db.get(tb_ordem, ids["order"]).total_value == Decimal("399.50")


def test_remover_item_devolve_estoque(client, db: Session, ids: dict[str, int]) -> None:
    client.post(
        f"/orders/{ids['order']}/items",
        json={"product_id": ids["teclado"], "quantity": 1},
    )
    resposta = client.delete(f"/orders/{ids['order']}/items/{ids['teclado']}")
    assert resposta.status_code == 204
    db.expire_all()
    assert db.get(Product, ids["teclado"]).stock == 5
    assert db.get(tb_ordem, ids["order"]).itens == []
    assert db.get(tb_ordem, ids["order"]).total_value == Decimal("0.00")
