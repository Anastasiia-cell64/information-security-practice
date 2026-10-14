from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Index,
    Integer, String, Table, Text
)
from sqlalchemy.orm import relationship
from app.crypto.encryption import blind_index, decrypt_field, encrypt_field
from app.database import Base

# Таблица связи пользователей и ролей (RBAC)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", secondary=user_roles, back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)

    # PII сохраняется исключительно как шифротекст Fernet[cite: 5]
    _encrypted_email = Column("encrypted_email", String(500), nullable=True)
    email_index = Column(String(64), unique=True, nullable=True, index=True)
    _encrypted_phone = Column("encrypted_phone", String(500), nullable=True)

    password_hash = Column(String(150), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users")

    # Свойства для прозрачного шифрования/расшифрования[cite: 5]
    @property
    def email(self) -> str | None:
        return decrypt_field(self._encrypted_email)

    @email.setter
    def email(self, value: str | None) -> None:
        self._encrypted_email = encrypt_field(value) if value else None
        self.email_index = blind_index(value) if value else None

    @property
    def phone(self) -> str | None:
        return decrypt_field(self._encrypted_phone)

    @phone.setter
    def phone(self, value: str | None) -> None:
        self._encrypted_phone = encrypt_field(value) if value else None

    def __repr__(self):
        return f"<User {self.username}>"