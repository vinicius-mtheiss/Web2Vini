"""Fatia do Lucas, parte B: tb_ordem (ciclo de vida do pedido)."""

from decimal import Decimal

import pytest

from app.models.product import Product
from app.ordem_status.models import OrderStatus, StatusNome
from app.tb_ordem.models import tb_ordem
from app.usuarios.models import Usuario


@pytest.fixture
def usuario(db) -> Usuario:
    u = Usuario(
        first_name="Lucas",
        last_name="Teste",
        email="lucas@teste.com",
        password_hash="x",
    )
    db.add(u)
    db.commit()
    return u


def _estoque(db, product_id: int) -> int:
    db.expire_all()
    return db.get(Product, product_id).stock


def _definir_status(db, order_id: int, nome: StatusNome) -> None:
    linha = db.query(OrderStatus).filter_by(status_name=nome.value).one()
    db.get(tb_ordem, order_id).order_status_id = linha.order_status_id
    db.commit()


# --- criação e leitura --------------------------------------------------------


def test_criar_pedido_nasce_pendente_e_zerado(client, usuario):
    resp = client.post("/orders", json={"user_id": usuario.usuario_id})

    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "Pendente"
    assert Decimal(body["total_value"]) == Decimal("0.00")
    assert body["itens"] == []


def test_criar_pedido_de_usuario_inexistente_retorna_422(client):
    resp = client.post("/orders", json={"user_id": 9999})

    assert resp.status_code == 422


def test_buscar_pedido_inexistente_retorna_404(client):
    assert client.get("/orders/9999").status_code == 404


def test_pedido_traz_itens_com_formato_do_order_item(client, ids):
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 2})

    body = client.get(f"/orders/{ids['order']}").json()

    assert Decimal(body["total_value"]) == Decimal("159.80")
    assert len(body["itens"]) == 1
    item = body["itens"][0]
    assert item["product_name"] == "Mouse"
    assert Decimal(item["price"]) == Decimal("79.90")
    assert Decimal(item["subtotal"]) == Decimal("159.80")


def test_listar_filtra_por_status(client, ids):
    resp = client.get("/orders", params={"status": "Pago"})

    assert resp.status_code == 200
    assert [o["order_id"] for o in resp.json()] == [ids["closed_order"]]


def test_listar_pedidos_do_usuario_filtra_pelo_dono(client, db, usuario):
    # O conftest já cria 2 pedidos com user_id=1, que é o id deste usuário.
    pedido = client.post("/orders", json={"user_id": usuario.usuario_id}).json()
    outro = Usuario(first_name="Outro", last_name="Teste", email="outro@teste.com", password_hash="x")
    db.add(outro)
    db.commit()

    do_usuario = client.get(f"/users/{usuario.usuario_id}/orders")
    do_outro = client.get(f"/users/{outro.usuario_id}/orders")

    assert do_usuario.status_code == 200
    assert pedido["order_id"] in [o["order_id"] for o in do_usuario.json()]
    assert all(o["user_id"] == usuario.usuario_id for o in do_usuario.json())
    assert do_outro.status_code == 200
    assert do_outro.json() == []


def test_listar_pedidos_de_usuario_inexistente_retorna_404(client):
    assert client.get("/users/9999/orders").status_code == 404


# --- transições de status -----------------------------------------------------


def test_fluxo_completo_pendente_pago_enviado_entregue(client, ids):
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 1})

    for destino in ("Pago", "Enviado", "Entregue"):
        resp = client.patch(f"/orders/{ids['order']}/status", json={"status": destino})
        assert resp.status_code == 200
        assert resp.json()["status"] == destino


def test_transicao_invalida_retorna_409(client, ids):
    # Pendente -> Enviado pula o Pago.
    resp = client.patch(f"/orders/{ids['order']}/status", json={"status": "Enviado"})

    assert resp.status_code == 409


def test_status_desconhecido_retorna_422(client, ids):
    resp = client.patch(f"/orders/{ids['order']}/status", json={"status": "Inventado"})

    assert resp.status_code == 422


def test_pagar_pedido_sem_itens_retorna_422(client, ids):
    resp = client.patch(f"/orders/{ids['order']}/status", json={"status": "Pago"})

    assert resp.status_code == 422


# --- cancelamento e estoque ---------------------------------------------------


def test_cancelar_pedido_pendente_devolve_estoque(client, db, ids):
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 3})
    assert _estoque(db, ids["mouse"]) == 7

    resp = client.post(f"/orders/{ids['order']}/cancel")

    assert resp.status_code == 200
    assert resp.json()["status"] == "Cancelado"
    assert _estoque(db, ids["mouse"]) == 10


def test_cancelar_pedido_pago_devolve_estoque_de_todos_os_itens(client, db, ids):
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 2})
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["teclado"], "quantity": 4})
    client.patch(f"/orders/{ids['order']}/status", json={"status": "Pago"})

    resp = client.post(f"/orders/{ids['order']}/cancel")

    assert resp.status_code == 200
    assert _estoque(db, ids["mouse"]) == 10
    assert _estoque(db, ids["teclado"]) == 5


def test_cancelar_via_patch_tambem_devolve_estoque(client, db, ids):
    """O PATCH com 'Cancelado' não pode ser um caminho que pula a devolução."""
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 3})

    resp = client.patch(f"/orders/{ids['order']}/status", json={"status": "Cancelado"})

    assert resp.status_code == 200
    assert resp.json()["status"] == "Cancelado"
    assert _estoque(db, ids["mouse"]) == 10


def test_cancelar_pedido_entregue_retorna_409_e_nao_mexe_no_estoque(client, db, ids):
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 3})
    _definir_status(db, ids["order"], StatusNome.ENTREGUE)

    resp = client.post(f"/orders/{ids['order']}/cancel")

    assert resp.status_code == 409
    assert _estoque(db, ids["mouse"]) == 7


def test_cancelar_duas_vezes_nao_devolve_estoque_duas_vezes(client, db, ids):
    client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 3})
    client.post(f"/orders/{ids['order']}/cancel")

    resp = client.post(f"/orders/{ids['order']}/cancel")

    assert resp.status_code == 409
    assert _estoque(db, ids["mouse"]) == 10


def test_cancelar_pedido_inexistente_retorna_404(client):
    assert client.post("/orders/9999/cancel").status_code == 404


def test_pedido_cancelado_nao_aceita_mais_itens(client, ids):
    client.post(f"/orders/{ids['order']}/cancel")

    resp = client.post(f"/orders/{ids['order']}/items", json={"product_id": ids["mouse"], "quantity": 1})

    assert resp.status_code == 409
