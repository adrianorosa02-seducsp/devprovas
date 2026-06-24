from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.core.database import engine

app = FastAPI(title="DevProvas API", version="0.1.0")


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
