import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://appuser:appsenha@db.inetz.com.br:5432/appdb"
)

# Sync engine (para Alembic, scripts, etc.)
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c search_path=devprovas,public"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine (para SQLAdmin, FastAPI async routes)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"server_settings": {"search_path": "devprovas,public"}},
)
async_session_maker = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    async with async_session_maker() as session:
        yield session
