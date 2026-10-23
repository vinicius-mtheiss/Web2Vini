"""Importa TODOS os models para que `Base.metadata.create_all` os enxergue.

Cada dev acrescenta uma linha aqui ao criar sua entidade.
"""

from app.models.category import Category
from app.models.product import Product
from app.ordem_status.models import OrderStatus
from app.order_item.models import OrderItem
from app.tb_ordem.models import tb_ordem
from app.usuarios.models import Usuario # noqa: F401

__all__ = ["Category", "Product", "OrderStatus", "tb_ordem", "OrderItem", "Usuario"]
