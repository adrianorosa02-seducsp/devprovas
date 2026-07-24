from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

TipoUsuario = Literal["admin", "professor", "aluno"]

class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=255)
    email: EmailStr
    tipo: TipoUsuario
    escola_id: Optional[UUID] = None
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=8)

# Testando exatamente os dados do seu cURL:
dados_teste = {
    "nome": "arosa725",
    "email": "arosa725@gmail.com",
    "tipo": "admin",
    "escola_id": "dfb572e3-44d2-49f8-b7dd-ed0aa112796e",
    "ativo": True,
    "senha": "AnigerAilec725"
}

try:
    usuario = UsuarioCreate(**dados_teste)
    print("Sucesso! O Pydantic aceitou os dados:", usuario)
except Exception as e:
    print("ERRO CAPTURADO PELO PYDANTIC:")
    print(e)