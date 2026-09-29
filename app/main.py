from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import administradores, associados, comprovantes, moradias, pagamentos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(administradores.router, prefix=settings.APP_V1_PREFIX)
app.include_router(moradias.router, prefix=settings.APP_V1_PREFIX)
app.include_router(associados.router, prefix=settings.APP_V1_PREFIX)
app.include_router(comprovantes.router, prefix=settings.APP_V1_PREFIX)
app.include_router(pagamentos.router, prefix=settings.APP_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok"}
