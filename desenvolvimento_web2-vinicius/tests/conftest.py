from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.category import Category
from app.models.product import Product
from app.ordem_status.models import OrderStatus, StatusNome
from app.tb_ordem.models import tb_ordem

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    categoria = Category(name="Eletrônicos")
    session.add(categoria)
    session.flush()

    mouse = Product(
        name="Mouse",
        price=Decimal("79.90"),
        stock=10,
        category_id=categoria.category_id,
    )
    teclado = Product(
        name="Teclado",
        price=Decimal("199.00"),
        stock=5,
        category_id=categoria.category_id,
    )
    cabo = Product(
        name="Cabo",
        price=Decimal("20.00"),
        stock=1,
        category_id=categoria.category_id,
    )
    session.add_all([mouse, teclado, cabo])

    for nome in StatusNome:
        session.add(OrderStatus(status_name=nome.value, description=nome.value))
    session.flush()

    pendente = (
        session.query(OrderStatus).filter_by(status_name=StatusNome.PENDENTE.value).one()
    )
    pago = session.query(OrderStatus).filter_by(status_name=StatusNome.PAGO.value).one()
    aberto = tb_ordem(
        user_id=1,
        order_status_id=pendente.order_status_id,
        total_value=Decimal("0.00"),
    )
    fechado = tb_ordem(
        user_id=1,
        order_status_id=pago.order_status_id,
        total_value=Decimal("0.00"),
    )
    session.add_all([aberto, fechado])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def ids(db: Session) -> dict[str, int]:
    mouse = db.query(Product).filter_by(name="Mouse").one()
    teclado = db.query(Product).filter_by(name="Teclado").one()
    cabo = db.query(Product).filter_by(name="Cabo").one()
    aberto = db.query(tb_ordem).filter(tb_ordem.total_value == Decimal("0.00")).all()
    pendente = (
        db.query(OrderStatus).filter_by(status_name=StatusNome.PENDENTE.value).one()
    )
    order_aberto = next(o for o in aberto if o.order_status_id == pendente.order_status_id)
    order_fechado = next(o for o in aberto if o.order_status_id != pendente.order_status_id)
    return {
        "mouse": mouse.product_id,
        "teclado": teclado.product_id,
        "cabo": cabo.product_id,
        "order": order_aberto.order_id,
        "closed_order": order_fechado.order_id,
    }
