"""Autenticação: hash de senha (bcrypt) e JWT (OAuth2 Password Bearer)."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app import models, crud

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def authenticate_admin(db, email: str, senha: str):
    """Retorna o administrador se o email (usado como username) e a senha estiverem corretos, senão None."""
    admin = (
        db.query(models.Administrador)
        .filter(models.Administrador.email == email)
        .first()
    )
    if not admin or not verify_password(senha, admin.senha_hash):
        return None
    return admin


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_admin_by_token(db, token: str) -> models.Administrador | None:
    """Decodifica o JWT e retorna o administrador correspondente."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: int | None = payload.get("sub")
        if admin_id is None:
            return None
    except JWTError:
        return None
    return crud.get_administrador(db, admin_id)
