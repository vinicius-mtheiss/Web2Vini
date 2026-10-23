"""Regra de negócio — o seu `@Service`.

O Router não conhece o banco. O Service decide o que é válido no domínio.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.categorias.models import Categoria
from app.produtos.models import Produto
from app.produtos.repository import ProdutoRepository
from app.produtos.schemas import ProdutoCreate, ProdutoUpdate


class ProdutoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProdutoRepository(db)

    def listar(self, skip: int = 0, limit: int = 20) -> list[Produto]:
        return self.repo.listar(skip=skip, limit=limit)

    def buscar(self, produto_id: int) -> Produto:
        produto = self.repo.buscar_por_id(produto_id)
        if produto is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto {produto_id} não encontrado.",
            )
        return produto

    def criar(self, dados: ProdutoCreate) -> Produto:
        self._validar_categoria(dados.categoria_id)

        if self.repo.buscar_por_nome(dados.nome) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um produto chamado '{dados.nome}'.",
            )

        return self.repo.salvar(Produto(**dados.model_dump()))

    def atualizar(self, produto_id: int, dados: ProdutoUpdate) -> Produto:
        produto = self.buscar(produto_id)
        alteracoes = dados.model_dump(exclude_unset=True)

        if "categoria_id" in alteracoes:
            self._validar_categoria(alteracoes["categoria_id"])

        for campo, valor in alteracoes.items():
            setattr(produto, campo, valor)

        return self.repo.salvar(produto)

    def deletar(self, produto_id: int) -> None:
        self.repo.deletar(self.buscar(produto_id))

    def _validar_categoria(self, categoria_id: int) -> None:
        if self.db.get(Categoria, categoria_id) is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Categoria {categoria_id} não existe.",
            )
