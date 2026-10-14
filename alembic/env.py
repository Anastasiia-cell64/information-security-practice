import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Додаємо корінь проєкту в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, DATABASE_URL
from app import models  # Імпорт реєструє всі моделі (User, AuditLog)

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

# Передаємо метадані всіх моделей для autogenerate
target_metadata = Base.metadata

# Динамічно підставляємо шлях до бази з нашого app.database
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Запуск міграцій у режимі offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Підтримка SQLite для ALTER TABLE
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск міграцій у режимі online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Підтримка SQLite для ALTER TABLE
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()