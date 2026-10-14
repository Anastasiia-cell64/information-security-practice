import os

# Секрети лише зі змінних оточення. Без fallback: немає ключа — додаток не стартує[cite: 17]
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if len(SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET_KEY не задано або коротший за 32 символи (openssl rand -hex 32)")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://localhost").split(",")