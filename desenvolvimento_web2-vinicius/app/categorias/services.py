from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import schemas, repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ServicoUsuario:

    @staticmethod
    def listar(skip: int, limit: int, db: Session):
        return repository.listar(skip, limit, db)

    @staticmethod
    def get(user_id: int, db: Session):
        user = repository.get_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return user

    @staticmethod
    def criar(dados: schemas.CriarUsuario, db: Session):
        if repository.get_by_email(dados.email, db):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")

        hash_password = pwd_context.hash(dados.password)

        user_data = dados.model_dump(exclude={"password"})
        user_data["password_hash"] = hash_password

        # Nomenclatura atualizada: o repository usa salvar() para inserts e updates
        return repository.salvar(repository.models.Usuario(**user_data), db)

    @staticmethod
    def atualizar(user_id: int, dados: schemas.AtualizarUsuario, db: Session):
        user = ServicoUsuario.get(user_id, db)

        if dados.email and dados.email != user.email:
            if repository.get_by_email(dados.email, db):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

        dados_dict = dados.model_dump(exclude_unset=True)
        for key, value in dados_dict.items():
            setattr(user, key, value)

        return repository.salvar(user, db) # Atualizado para o nome correto

    @staticmethod
    def change_password(user_id: int, dados: schemas.SenhaUsuario, db: Session):
        user = ServicoUsuario.get(user_id, db)

        # Atualizado: Puxando o nome da propriedade exata que criaste no schema
        if not pwd_context.verify(dados.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Senha atual incorreta")

        # Atualizado: Gerando hash apenas da nova senha
        user.password_hash = pwd_context.hash(dados.new_password)
        return repository.salvar(user, db)

    @staticmethod
    def delete(user_id: int, db: Session):
        user = ServicoUsuario.get(user_id, db) # Precisa buscar o objeto primeiro
        try:
            repository.remover(user, db) # Atualizado para o nome correto e passando o objeto
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário possui pedidos atrelados e não pode ser deletado"
            )