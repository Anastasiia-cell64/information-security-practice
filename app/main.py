from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_router
from app.routers.auth_router import router as auth_router
from app.config import CORS_ORIGINS
from app.crypto.key_manager import get_blind_index_key, get_fernet
from app.database import Base

# Fail fast: перевірка ключів при старті
get_fernet()
get_blind_index_key()

app = FastAPI(title="Електронний деканат", version="2.0.0")

# Аудит-middleware
app.add_middleware(AuditMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Роутери
app.include_router(auth_router)
app.include_router(audit_router)


@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API"}


@app.get("/health")
def health():
    return {"status": "healthy", "database": "SQLite", "tables": len(Base.metadata.tables)}