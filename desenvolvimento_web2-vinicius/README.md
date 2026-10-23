# E-commerce API

API em FastAPI com **arquitetura em camadas** (equivalente ao padrão do Spring Boot).

## Estrutura

```
app/
├── database.py             # engine, SessionLocal, Base, get_db
├── main.py                 # app, registro de routers, /health, create_all
├── models/                 # entidades SQLAlchemy (tabelas)
│   ├── __init__.py         # importa TODOS os models (create_all enxerga)
│   ├── category.py
│   └── product.py
├── schemas/                # DTOs Pydantic (validação de entrada/saída)
├── repositories/           # acesso a dados
├── services/               # regras de negócio
└── routers/                # controllers HTTP (APIRouter)
```

Fluxo da requisição: `router` → `service` → `repository` → banco.

| Camada | Responsabilidade |
| --- | --- |
| `model` | tabela SQLAlchemy, sem lógica |
| `repository` | só query/insert/update/delete |
| `service` | regra de negócio e decisão de erro (`HTTPException`) |
| `schema` | Pydantic `Create` / `Update` / `Out` |
| `router` | recebe request, injeta `get_db`, chama o service |

## De/Para com Spring Boot

| Spring Boot | FastAPI |
| --- | --- |
| `@RestController` | `APIRouter` |
| DTO | Schema Pydantic |
| `@Service` | `services/` |
| `@Repository` | `repositories/` |
| Entidade JPA/Hibernate | Model SQLAlchemy |

## Convenção de erros

| Status | Quando |
| --- | --- |
| `200` | leitura / atualização |
| `201` | criação |
| `204` | remoção / desativação |
| `404` | recurso não encontrado |
| `409` | conflito (nome duplicado, categoria com produtos, estoque insuficiente) |
| `422` | referência inválida (FK para categoria inexistente) |

## Endpoints

| Método | Rota | Status |
| --- | --- | --- |
| GET | `/health` | `200` |
| GET | `/categories` | `200` |
| GET | `/categories/{id}` | `200` · `404` |
| POST | `/categories` | `201` · `409` |
| PATCH | `/categories/{id}` | `200` · `404` · `409` |
| DELETE | `/categories/{id}` | `204` · `404` · `409` (tem produtos vinculados) |
| GET | `/products` | `200` |
| GET | `/products/{id}` | `200` · `404` |
| POST | `/products` | `201` · `409` · `422` |
| PATCH | `/products/{id}` | `200` · `404` |
| DELETE | `/products/{id}` | `204` — desativa (`active = False`), não apaga |
| GET | `/ordem-status` | `200` |
| GET | `/ordem-status/{id}` | `200` · `404` |
| GET | `/orders` | `200` — filtro opcional `?status=Pago` |
| GET | `/orders/{id}` | `200` · `404` — já traz os itens |
| GET | `/users/{id}/orders` | `200` · `404` (usuário não existe) |
| POST | `/orders` | `201` · `422` (usuário não existe) — nasce `Pendente` e vazio |
| PATCH | `/orders/{id}/status` | `200` · `404` · `409` (transição inválida) · `422` (pagar sem itens) |
| POST | `/orders/{id}/cancel` | `200` · `404` · `409` — devolve o estoque dos itens |

## Contrato de estoque

A coluna `stock` é alterada **exclusivamente** dentro do `ProductService`. O módulo
de pedidos chama:

```python
ProductService(db).decrease_stock(product_id, qty)  # 409 se qty > stock
ProductService(db).increase_stock(product_id, qty)  # devolve ao cancelar
```

## Ciclo de vida do pedido

```
Pendente ──► Pago ──► Enviado ──► Entregue
    │          │
    └──────────┴────► Cancelado
```

- Qualquer outra transição responde `409`.
- Pagar (`PATCH` ou `POST /orders/{id}/close`) exige pelo menos um item (`422`).
- **Cancelar sempre devolve o estoque**, inclusive via `PATCH .../status` com
  `"Cancelado"`: o `OrderService.change_status` desvia para `cancel`, que valida a
  transição primeiro e só então chama `OrderItemService.restore_stock_for_order`.

## Testes

```bash
pip install pytest httpx
pytest
```

## Como rodar

```bash
pip install -r requirements.txt        # ou: uv sync
uvicorn app.main:app --reload          # http://127.0.0.1:8000/docs
```

Banco via `DATABASE_URL` (default `sqlite:///./ecommerce.db`). As tabelas são criadas
no startup com `Base.metadata.create_all` — sem Alembic por enquanto.
