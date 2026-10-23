"""Configuração da conexão com o banco.

Equivalente ao seu `application.properties` + `EntityManagerFactory` do Spring.
"""

import os
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# URL fora do código: copie .env.example para .env. Trocar SQLite por
# Postgres é só mudar a variável, sem alterar Python.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

engine = create_engine(
    DATABASE_URL,
    # check_same_thread é uma exigência exclusiva do SQLite.
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe-mãe de todas as entidades. É o seu `@Entity` do JPA."""


def get_db() -> Generator[Session, None, None]:
    """Injeção de dependência: entrega uma sessão e garante o fechamento.

    É o `@PersistenceContext` / `@Transactional` do Spring, só que explícito.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]