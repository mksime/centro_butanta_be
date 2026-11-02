from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.observability import init_sentry
from app.rate_limit import limiter
from app.routers import administradores, associados, auth, comprovantes, moradias, pagamentos
from app.seed import seed_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # O schema é gerenciado exclusivamente pelo Alembic (alembic upgrade head).
    # Não use Base.metadata.create_all aqui: com múltiplas instâncias, várias
    # réplicas executariam DDL concorrentemente e fora do controle de versão.

    # Seed do primeiro administrador (apenas se habilitado via env)
    if settings.ADMIN_SEED_ENABLED:
        db = SessionLocal()
        try:
            seed_initial_admin(db, settings)
        finally:
            db.close()

    yield


def create_app() -> FastAPI:
    """Monta a aplicação. Em produção, /docs, /redoc e /openapi.json ficam off."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )

    # Rate limit: o handler usa request.app.state.limiter para montar o 429.
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS — origens vêm de CORS_ORIGINS (lista separada por vírgula)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(auth.router, prefix=settings.APP_V1_PREFIX)
    app.include_router(administradores.router, prefix=settings.APP_V1_PREFIX)
    app.include_router(moradias.router, prefix=settings.APP_V1_PREFIX)
    app.include_router(associados.router, prefix=settings.APP_V1_PREFIX)
    app.include_router(comprovantes.router, prefix=settings.APP_V1_PREFIX)
    app.include_router(pagamentos.router, prefix=settings.APP_V1_PREFIX)

    @app.get("/health")
    def health_check():
        """Liveness: o processo está vivo. É o health check usado pelo Render."""
        return {"status": "ok"}

    @app.get("/ready")
    def readiness_check(db: Session = Depends(get_db)):
        """Readiness: confirma que o banco responde.

        Use em monitoramento externo, não como health check do Render: se o
        banco oscilar, o Render reiniciaria instâncias sadias.
        """
        try:
            db.execute(text("SELECT 1"))
        except SQLAlchemyError:
            raise HTTPException(status_code=503, detail="Banco de dados indisponível")
        return {"status": "ok"}

    return app


init_sentry()
app = create_app()
