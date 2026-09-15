from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SedArquivo(BaseModel):
    idCronograma: int
    idArquivo: int
    nomeArquivo: str
    linkDownload: str
    baixou: bool
    utilizou: bool
    avaliou: bool
    ativo: bool
    dtArquivo: datetime
    tipoArquivo: int


class SedMaterial(BaseModel):
    codCronogramaAula: int
    idCronogramaAula: int
    titulo: str
    referenciaId: int
    referencia: str
    tipo: str
    ordenacao: int
    semana: int
    ano: int
    aulasComTarefa: bool
    linkUrlYoutube: Optional[str]
    exibirMunicipio: bool
    arquivos: list[SedArquivo]
    arrayLinksYoutube: str


class SedRequest(BaseModel):
    key: str
    Ano: str
    TipoEnsino: str
    Serie: str
    Bimestre: str
    Componente: str
    IsPrepara: bool
    IsPreparaReforco: bool


class SedResponse(BaseModel):
    request: SedRequest
    response: list[SedMaterial]
    metadata: dict


class SedMaterialFilters(BaseModel):
    ano: int
    tipo_ensino: int
    serie: int
    bimestre: int
    componente: int
    is_prepara: bool = False
    is_prepara_reforco: bool = False