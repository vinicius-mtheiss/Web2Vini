from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from . import schemas
from .services import ServicoUsuario

# Importaremos a conexão do banco no próximo passo
# from database import get_db

router = APIRouter(prefix="/users", tags=["Cadastro de Clientes"])

@router.get("/", response_model=List[schemas.UsuarioOut], status_code=status.HTTP_200_OK)
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ServicoUsuario.listar(skip, limit, db)

@router.get("/{user_id}", response_model=schemas.UsuarioOut, status_code=status.HTTP_200_OK)
def get_usuario(user_id: int, db: Session = Depends(get_db)):
    return ServicoUsuario.get(user_id, db)

@router.post("/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: schemas.CriarUsuario, db: Session = Depends(get_db)):
    return ServicoUsuario.criar(dados, db)

@router.patch("/{user_id}", response_model=schemas.UsuarioOut, status_code=status.HTTP_200_OK)
def atualizar_usuario(user_id: int, dados: schemas.AtualizarUsuario, db: Session = Depends(get_db)):
    return ServicoUsuario.atualizar(user_id, dados, db)

@router.patch("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
def alterar_senha(user_id: int, dados: schemas.SenhaUsuario, db: Session = Depends(get_db)):
    ServicoUsuario.change_password(user_id, dados, db)
    return

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_usuario(user_id: int, db: Session = Depends(get_db)):
    ServicoUsuario.delete(user_id, db)
    return