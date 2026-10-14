from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.crypto.encryption import blind_index
from app.database import get_db
from app.models import Role, User
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Username вже зайнятий")

    # Поиск дубликата по слепому индексу (HMAC) вместо открытого email
    if db.query(User).filter(User.email_index == blind_index(user_data.email)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email вже зареєстровано")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role:
        new_user.roles.append(student_role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Невірний логін або пароль")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Акаунт деактивовано")

    role_name = user.roles[0].name if user.roles else "student"
    return TokenResponse(
        access_token=create_access_token(user.id, role_name),
        refresh_token=create_refresh_token(user.id),
    )