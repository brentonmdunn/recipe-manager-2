from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "access"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days,
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "refresh"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None
