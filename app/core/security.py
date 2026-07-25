import os
from datetime import datetime, timedelta
from typing import Literal, Optional

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

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
    # bcrypt tem limite de 72 bytes - trunca se necessário
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt tem limite de 72 bytes - trunca se necessário (deve corresponder ao hash)
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


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
