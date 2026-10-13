from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import auth_router

# Створення всіх таблиць у SQLite перед стартом
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Електронний деканат")

app.include_router(auth_router.router)


@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API"}


@app.get("/health")
def health():
    return {"status": "healthy", "database": "SQLite", "tables": len(Base.metadata.tables)}