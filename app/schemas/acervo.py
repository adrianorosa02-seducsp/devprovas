from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AcervoDigitalBase(BaseModel):
    arquivo_id: str
    titulo: str
    descricao: Optional[str] = None
    tipo_arquivo: Optional[str] = None
    link_google_drive: Optional[str] = None
    link_download_python: Optional[str] = None


class AcervoDigitalCreate(AcervoDigitalBase):
    pass


class AcervoDigitalUpdate(BaseModel):
    arquivo_id: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo_arquivo: Optional[str] = None
    link_google_drive: Optional[str] = None
    link_download_python: Optional[str] = None


class AcervoDigitalRead(AcervoDigitalBase):
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AcervoDigitalListResponse(BaseModel):
    items: list[AcervoDigitalRead]
    total: int
    page: int
    page_size: int