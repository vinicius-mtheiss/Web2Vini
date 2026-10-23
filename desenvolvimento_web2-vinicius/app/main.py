"""Ponto de entrada da aplicação."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  registra os models na Base antes do create_all
from app.database import Base, engine
from app.order_item import router as order_item_router
from app.ordem_status import router as ordem_status_router
from app.routers import category as category_router
from app.routers import product as product_router
from app.tb_ordem import router as tb_ordem_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sem Alembic por enquanto: as tabelas nascem no startup.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="E-commerce API",
    version="0.1.0",
    description="API de e-commerce em arquitetura em camadas.",
    lifespan=lifespan,
)

# Um router por linha — cada dev acrescenta a sua e o merge fica trivial.
app.include_router(category_router.router)
app.include_router(product_router.router)
app.include_router(order_item_router.router)
app.include_router(ordem_status_router.router)
app.include_router(tb_ordem_router.router)



@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
