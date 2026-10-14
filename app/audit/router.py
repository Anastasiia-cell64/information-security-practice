from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.audit.logger import get_audit_logs
from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import AuditLog, User

router = APIRouter(prefix="/admin/audit", tags=["Audit Log"])


@router.get("/logs")
def read_audit_logs(
    action: Optional[str] = Query(None, description="Фільтр за дією (наприклад, login_failed)"),
    user_id: Optional[int] = Query(None, description="Фільтр за ID користувача"),
    status: Optional[str] = Query(None, description="Фільтр за статусом (success|failure|warning|error)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """
    Перегляд логів аудиту безпеки (тільки для адміністраторів).
    """
    logs = get_audit_logs(
        db=db,
        action=action,
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "user_id": log.user_id,
            "username": log.username,
            "ip_address": log.ip_address,
            "action": log.action,
            "resource": log.resource,
            "http_method": log.http_method,
            "endpoint": log.endpoint,
            "status": log.status,
            "status_code": log.status_code,
            "details": log.details,
        }
        for log in logs
    ]