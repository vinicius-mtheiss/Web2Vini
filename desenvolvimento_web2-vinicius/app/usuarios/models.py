from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from app.database import Base

class Usuario(Base):
    __tablename__ = 'tb_usuarios'

    usuario_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    phone = Column(String(11))
    uf = Column(String(2))
    city = Column(String(200))
    neighborhood = Column(String(200))
    address = Column(String(200))
    password_hash = Column(String(255), nullable=False)
