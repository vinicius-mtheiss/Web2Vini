from sqlalchemy.orm import Session
from app.usuarios.models import Usuario

def listar(skip: int, limit: int, db: Session):
    """Paginando desde o começo para evitar sobrecarga de memória na API"""
    return db.query(Usuario).offset(skip).limit(limit).all()

def get_by_id(id: int, db: Session):
    """Busca direta pela chave primária"""
    return db.query(Usuario).filter(Usuario.id == id).first()

def get_by_email(email: str, db: Session):
    """Serve para verificar duplicidade no cadastro e localizar o usuário no login."""
    return db.query(Usuario).filter(Usuario.email == email).first()

def salvar(user: Usuario, db: Session):
    """Serve tanto para criar (INSERT) quanto para atualizar (UPDATE)."""
    db.add(user)
    db.commit()
    db.refresh(user) #Recarrega o objeto para trazer o ID gerado pelo banco
    return user

def remover(user: Usuario, db: Session):
    """Remove o registro definitivamente"""
    db.delete(user)
    db.commit()