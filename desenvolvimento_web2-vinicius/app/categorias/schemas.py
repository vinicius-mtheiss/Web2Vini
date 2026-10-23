from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CriarUsuario(BaseModel):
    first_name: str = Field(..., max_length=200)
    last_name: str = Field(..., max_length=200)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\d+$', min_length=10, max_length=11)
    uf: str = Field(..., min_length=2, max_length=2)
    city: str = Field(..., max_length=200)
    neighborhood: str = Field(..., max_length=200)
    address: str = Field(..., max_length=200)
    password: str = Field(..., min_length=8)

class AtualizarUsuario(BaseModel):
    first_name: Optional[str] = Field(None, max_length=200)
    last_name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\d+$', min_length=10, max_length=11)
    uf: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = Field(None, max_length=200)
    neighborhood: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=200)

class UsuarioOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    uf: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

class SenhaUsuario(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
