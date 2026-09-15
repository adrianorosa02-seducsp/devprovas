from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def get_model_or_404(session: Session, model: type, obj_id) -> object:
    obj = session.get(model, obj_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado.",
        )
    return obj


def apply_updates(instance: object, payload) -> None:
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(instance, key, value)
