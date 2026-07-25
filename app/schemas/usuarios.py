from pydantic import BaseModel, EmailStr, Field

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    tipo: str
    escola_id: str
    ativo: bool = True
    senha: str = Field(..., max_length=72, description="Senha limitada a 72 bytes devido ao bcrypt")

class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: EmailStr
    tipo: str
    ativo: bool

    class Config:
        from_attributes = True