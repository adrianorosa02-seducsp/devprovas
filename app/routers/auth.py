from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenPayload,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.models import Usuario
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

_INVALID_CREDENTIALS = "Email ou senha inválidos."
_INACTIVE_ACCOUNT = "Usuário inativo."


def _get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    statement = select(Usuario).where(Usuario.email == email)
    return db.scalar(statement)


def _raise_invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _raise_inactive_user() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=_INACTIVE_ACCOUNT,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    usuario = _get_usuario_by_email(db, payload.email)
    if not usuario or not verify_password(payload.senha, usuario.senha_hash):
        raise _raise_invalid_credentials()
    if not usuario.ativo:
        raise _raise_inactive_user()

    access_token = create_access_token(subject=str(usuario.id), scope=usuario.tipo)
    refresh_token = create_refresh_token(subject=str(usuario.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        token_payload: TokenPayload = decode_token(payload.refresh_token)
    except JWTError:
        raise _raise_invalid_credentials()

    if token_payload.type != "refresh":
        raise _raise_invalid_credentials()

    try:
        user_id = UUID(token_payload.sub)
    except ValueError:
        raise _raise_invalid_credentials()

    usuario = db.get(Usuario, user_id)
    if usuario is None:
        raise _raise_invalid_credentials()
    if not usuario.ativo:
        raise _raise_inactive_user()

    access_token = create_access_token(subject=token_payload.sub, scope=usuario.tipo)
    refresh_token = create_refresh_token(subject=token_payload.sub)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
