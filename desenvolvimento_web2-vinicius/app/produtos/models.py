"""A Entidade (SQLAlchemy) — o seu `@Entity` do Hibernate/JPA."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.categorias.models import Categoria
from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"  # @Table(name = "produtos")

    # @Id @GeneratedValue(strategy = IDENTITY)
    id: Mapped[int] = mapped_column(primary_key=True)

    # @Column(nullable = false, length = 150)
    nome: Mapped[str] = mapped_column(String(150), index=True)
    descricao: Mapped[str | None] = mapped_column(String(500), default=None)

    # Dinheiro NUNCA é float. Numeric(10, 2) == BigDecimal do Java.
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    estoque: Mapped[int] = mapped_column(default=0)
    ativo: Mapped[bool] = mapped_column(default=True)

    # @ManyToOne + @JoinColumn(name = "categoria_id")
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    categoria: Mapped[Categoria] = relationship(back_populates="produtos")

    # O banco preenche sozinho (equivale ao @CreationTimestamp).
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"<Produto id={self.id} nome={self.nome!r} preco={self.preco}>"
