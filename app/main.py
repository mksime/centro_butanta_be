from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import administradores, associados, auth, comprovantes, moradias, pagamentos
from app.seed import seed_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    Base.metadata.create_all(bind=engine)

    # Seed do primeiro administrador (apenas se habilitado via env)
    if settings.ADMIN_SEED_ENABLED:
        db = SessionLocal()
        try:
            seed_initial_admin(db, settings)
        finally:
            db.close()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — ajuste allow_origins para o domínio do frontend Vue em produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.APP_V1_PREFIX)
app.include_router(administradores.router, prefix=settings.APP_V1_PREFIX)
app.include_router(moradias.router, prefix=settings.APP_V1_PREFIX)
app.include_router(associados.router, prefix=settings.APP_V1_PREFIX)
app.include_router(comprovantes.router, prefix=settings.APP_V1_PREFIX)
app.include_router(pagamentos.router, prefix=settings.APP_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok"}
