"""O Controller — @RestController + @RequestMapping("/produtos")."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.produtos.schemas import ProdutoCreate, ProdutoOut, ProdutoUpdate
from app.produtos.services import ProdutoService
from app.database import get_db

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> ProdutoService:
    """@Autowired: o FastAPI monta o Service com a sessão já injetada."""
    return ProdutoService(db)


Service = Annotated[ProdutoService, Depends(get_service)]


@router.get("", response_model=list[ProdutoOut])  # @GetMapping
def listar_produtos(
    service: Service,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return service.listar(skip=skip, limit=limit)


@router.get("/{produto_id}", response_model=ProdutoOut)
def buscar_produto(produto_id: int, service: Service):
    return service.buscar(produto_id)


@router.post("", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar_produto(dados: ProdutoCreate, service: Service):  # @RequestBody @Valid
    return service.criar(dados)


@router.patch("/{produto_id}", response_model=ProdutoOut)
def atualizar_produto(produto_id: int, dados: ProdutoUpdate, service: Service):
    return service.atualizar(produto_id, dados)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(produto_id: int, service: Service):
    service.deletar(produto_id)
