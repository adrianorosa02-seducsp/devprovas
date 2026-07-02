import os
from datetime import datetime, timedelta
from typing import Literal, Optional

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "devprovas-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_HOURS", "168"))

TokenType = Literal["access", "refresh"]


class TokenPayload(BaseModel):
    sub: str
    type: TokenType
    exp: int
    iat: int
    scope: Optional[str] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, scope: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, "access", expires_delta, scope)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    return _create_token(subject, "refresh", expires_delta)


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    scope: Optional[str] = None,
) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "type": token_type,
        "scope": scope,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    compact_payload = {key: value for key, value in payload.items() if value is not None}
    return jwt.encode(compact_payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise exc
    return TokenPayload(**payload)
