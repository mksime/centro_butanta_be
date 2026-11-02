"""Rotas de autenticação (login/token)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.auth import authenticate_admin, create_access_token
from app.config import settings
from app.database import get_db
from app.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
@limiter.limit(settings.LOGIN_RATE_LIMIT)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica o administrador e devolve um JWT Bearer.

    Usado pelo Swagger (Authorize) e pelo frontend Vue.
    O campo `username` recebe o **email** do administrador (email como username);
    o campo `password` recebe a senha.
    Enviar no corpo: grant_type, username, senha, scope, client_id, client_secret.
    """
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(admin.id_administrador)})
    return {"access_token": access_token, "token_type": "bearer"}
