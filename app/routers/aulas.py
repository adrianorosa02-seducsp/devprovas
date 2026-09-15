from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AulaConteudo
from app.services.openai_client import create_embeddings


class AulaMetadata(BaseModel):
    titulo: str | None = None
    competencia: str | None = None
    tem_roteiro: bool = False


class AulaConteudoPayload(BaseModel):
    id_aula: str = Field(..., max_length=50)
    componente: str
    conteudo_vetor: str
    metadata: AulaMetadata


class AulaProcessResult(BaseModel):
    id_aula: str
    updated: bool
    message: str


router = APIRouter(prefix="/aulas", tags=["aulas"])


@router.post("/conteudos", response_model=List[AulaProcessResult])
def ingest_conteudos(
    payload: List[AulaConteudoPayload],
    db: Session = Depends(get_db),
) -> List[AulaProcessResult]:
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum conteúdo informado."
        )

    textos = [item.conteudo_vetor for item in payload]

    try:
        embeddings = create_embeddings(textos)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    ids = [item.id_aula for item in payload]
    existing = {
        row[0]
        for row in db.execute(
            select(AulaConteudo.id_aula).where(AulaConteudo.id_aula.in_(ids))
        ).all()
    }

    responses: List[AulaProcessResult] = []

    for item, embedding in zip(payload, embeddings):
        values = {
            "id_aula": item.id_aula,
            "componente": item.componente,
            "titulo": item.metadata.titulo,
            "competencia": item.metadata.competencia,
            "tem_roteiro": item.metadata.tem_roteiro,
            "conteudo_bruto": item.conteudo_vetor,
            "embedding": embedding,
        }

        stmt = (
            insert(AulaConteudo)
            .values(**values)
            .on_conflict_do_update(
                index_elements=[AulaConteudo.id_aula],
                set_={
                    "componente": item.componente,
                    "titulo": item.metadata.titulo,
                    "competencia": item.metadata.competencia,
                    "tem_roteiro": item.metadata.tem_roteiro,
                    "conteudo_bruto": item.conteudo_vetor,
                    "embedding": embedding,
                    "updated_at": func.now(),
                },
            )
        )

        db.execute(stmt)

        processed = item.id_aula in existing
        responses.append(
            AulaProcessResult(
                id_aula=item.id_aula,
                updated=processed,
                message="Conteúdo atualizado"
                if processed
                else "Conteúdo registrado",
            )
        )

    db.commit()

    return responses
