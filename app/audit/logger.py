import json
from typing import Any, Dict, List, Optional
from fastapi import Request
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.models import AuditLog


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def log_event(
    db: Session,
    action: str,
    status: str,
    ip_address: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    resource: Optional[str] = None,
    http_method: Optional[str] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        action=action,
        resource=resource,
        http_method=http_method,
        endpoint=endpoint,
        status=status,
        status_code=status_code,
        details=json.dumps(details, ensure_ascii=False) if details else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_audit_logs(
    db: Session,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if status:
        query = query.filter(AuditLog.status == status)
    return query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()