from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel, model_validator

from app.core.database import get_db
from app.models.models import MaterialDidatico


router = APIRouter(prefix="/materiais", tags=["Materiais Didáticos"])


class MaterialArquivo(BaseModel):
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


class MaterialResponse(BaseModel):
    codCronogramaAula: int
    idCronogramaAula: int
    titulo: Optional[str] = None
    referenciaId: Optional[int] = None
    referencia: Optional[str] = None
    tipo: Optional[str] = None
    ordenacao: Optional[int] = None
    semana: Optional[int] = None
    ano: int
    aulasComTarefa: Optional[bool] = None
    linkUrlYoutube: Optional[str] = None
    exibirMunicipio: Optional[bool] = None
    arquivos: List[MaterialArquivo] = []
    arrayLinksYoutube: Optional[str] = None
    id: str
    ano_referencia: int
    bimestre: int
    serie: str
    componente: str

    @model_validator(mode="before")
    @classmethod
    def map_fields(cls, data):
        if isinstance(data, MaterialDidatico):
            m = data
            return {
                "codCronogramaAula": m.cod_cronograma,
                "idCronogramaAula": m.id_cronograma,
                "titulo": m.titulo,
                "referenciaId": m.referencia_id,
                "referencia": str(m.referencia_id) if m.referencia_id else None,
                "tipo": m.tipo,
                "ordenacao": m.ordenacao,
                "semana": m.semana,
                "ano": m.ano_referencia,
                "aulasComTarefa": m.aulas_com_tarefa,
                "linkUrlYoutube": m.link_url_youtube,
                "exibirMunicipio": m.exibir_municipio,
                "arquivos": m.arquivos or [],
                "arrayLinksYoutube": m.array_links_youtube,
                "id": str(m.id),
                "ano_referencia": m.ano_referencia,
                "bimestre": m.bimestre,
                "serie": m.serie,
                "componente": m.componente,
            }
        return data

    class Config:
        from_attributes = True


class MaterialListResponse(BaseModel):
    items: List[MaterialResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=MaterialListResponse)
def listar_materiais(
    ano_referencia: int = Query(..., description="Ano de referência (ex: 2026)"),
    componente: str = Query(..., description="Código do componente (ex: 13=Matemática)"),
    bimestre: int = Query(..., ge=1, le=4, description="Bimestre (1-4)"),
    semana: Optional[int] = Query(None, ge=1, le=8, description="Semana (1-8). Se não informado, retorna todas as semanas."),
    db: Session = Depends(get_db),
):
    """Lista materiais didáticos filtrados por ano, componente, bimestre e opcionalmente semana, ordenados por ordenação."""

    query = (
        select(MaterialDidatico)
        .where(MaterialDidatico.ano_referencia == ano_referencia)
        .where(MaterialDidatico.componente == componente)
        .where(MaterialDidatico.bimestre == bimestre)
        .order_by(MaterialDidatico.ordenacao.asc())
    )

    if semana:
        query = query.where(MaterialDidatico.semana == semana)

    results = db.execute(query).scalars().all()
    total = len(results)

    items = [MaterialResponse.model_validate(r, from_attributes=True) for r in results]

    return MaterialListResponse(
        items=items,
        total=total,
        page=1,
        page_size=total
    )


@router.get("/{material_id}", response_model=MaterialResponse)
def obter_material(material_id: str, db: Session = Depends(get_db)):
    """Obtém um material específico por ID."""
    material = db.get(MaterialDidatico, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return MaterialResponse.model_validate(material, from_attributes=True)


@router.get("/filtros/opcoes")
def listar_opcoes_filtros(db: Session = Depends(get_db)):
    """Retorna valores distintos para popular filtros (dropdowns)."""
    anos = db.execute(
        select(MaterialDidatico.ano_referencia).distinct().order_by(MaterialDidatico.ano_referencia.desc())
    ).scalars().all()

    bimestres = db.execute(
        select(MaterialDidatico.bimestre).distinct().order_by(MaterialDidatico.bimestre)
    ).scalars().all()

    series = db.execute(
        select(MaterialDidatico.serie).distinct().order_by(MaterialDidatico.serie)
    ).scalars().all()

    componentes = db.execute(
        select(MaterialDidatico.componente).distinct().order_by(MaterialDidatico.componente)
    ).scalars().all()

    tipos = db.execute(
        select(MaterialDidatico.tipo).distinct().order_by(MaterialDidatico.tipo)
    ).scalars().all()

    return {
        "anos": anos,
        "bimestres": bimestres,
        "series": series,
        "componentes": componentes,
        "tipos": tipos,
    }