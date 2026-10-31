"""Dependências de autenticação para proteger rotas."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth import get_admin_by_token
from app.config import settings
from app.database import get_db
from app import models

# URL do endpoint de login (usada pelo Swagger para preencher o botão "Authorize")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.APP_V1_PREFIX}/auth/token")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.Administrador:
    """Extrai o administrador logado a partir do Bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    admin = get_admin_by_token(db, token)
    if admin is None:
        raise credentials_exception
    return admin


def get_current_active_admin(
    current_admin: models.Administrador = Depends(get_current_admin),
) -> models.Administrador:
    """Administrador autenticado (estende para regras futuras, ex.: inativo/bloqueado)."""
    return current_admin
