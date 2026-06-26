from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.core.database import engine
from app.routers import aulas_router

app = FastAPI(title="DevProvas API", version="0.1.0")
app.include_router(aulas_router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except OperationalError:
        return {"status": "unhealthy", "database": "disconnected"}
