from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.crypto.encryption import blind_index
from app.database import get_db
from app.models import Role, User
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.audit.detector import check_brute_force, check_off_hours_access
from app.audit.logger import get_client_ip, log_login_failed, log_login_success, log_event

router = APIRouter(prefix="/auth", tags=["Auth"])

# ... register функція залишається як була ...

@router.post("/login", response_model=TokenResponse)
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    ip = get_client_ip(request)

    # 1. Brute Force перевіряємо ДО перевірки пароля
    if check_brute_force(db, ip, credentials.username):
        log_login_failed(db, credentials.username, ip, reason="brute_force_blocked")
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail="Забагато невдалих спроб. Спробуйте через 5 хвилин.")

    # 2. Перевірка пароля
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        log_login_failed(db, credentials.username, ip)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Невірний логін або пароль")

    if not user.is_active:
        log_login_failed(db, credentials.username, ip, reason="inactive")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Акаунт деактивовано")

    check_off_hours_access(db, user.id, user.username, ip)
    log_login_success(db, user.id, user.username, ip)

    role_name = user.roles[0].name if user.roles else "student"
    return TokenResponse(
        access_token=create_access_token(user.id, role_name),
        refresh_token=create_refresh_token(user.id),
    )