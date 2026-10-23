"""Fatia do Lucas, parte A: order_status (somente leitura)."""

from app.ordem_status.models import StatusNome


def test_listar_status_devolve_todos_do_enum(client):
    resp = client.get("/ordem-status")

    assert resp.status_code == 200
    nomes = {s["status_name"] for s in resp.json()}
    assert nomes == {m.value for m in StatusNome}


def test_buscar_status_por_id(client):
    primeiro = client.get("/ordem-status").json()[0]

    resp = client.get(f"/ordem-status/{primeiro['order_status_id']}")

    assert resp.status_code == 200
    assert resp.json()["status_name"] == primeiro["status_name"]


def test_buscar_status_inexistente_retorna_404(client):
    resp = client.get("/ordem-status/9999")

    assert resp.status_code == 404
