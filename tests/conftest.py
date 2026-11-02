"""Fixtures compartilhadas para os testes da API."""

import os

# Precisa ser definido antes de importar app.config/app.main. O teste dedicado
# ao rate limit habilita o limiter explicitamente.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import normalize_database_url
from app.database import Base, get_db
from app.main import app

# Banco de testes:
# - TEST_DATABASE_URL definida → PostgreSQL real (usado no CI), o que exercita
#   ENUM nativo, constraints, SERIAL e tipos que o SQLite não reproduz.
# - Sem ela → SQLite em memória, para rodar rápido e sem dependências.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if TEST_DATABASE_URL:
    engine = create_engine(normalize_database_url(TEST_DATABASE_URL), pool_pre_ping=True)
    BANCO_POSTGRES = True
else:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # obrigatório para :memory: ser compartilhado
    )
    BANCO_POSTGRES = False

SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def tabelas():
    """Cria todas as tabelas uma vez por sessão de testes.

    No PostgreSQL as tabelas já vêm das migrations (o CI roda
    `alembic upgrade head`); o create_all é idempotente e serve de fallback.
    """
    Base.metadata.create_all(bind=engine)
    yield
    if not BANCO_POSTGRES:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(tabelas):
    """Sessão de banco isolada por teste.

    Desfaz transações não commitadas E remove linhas já commitadas,
    garantindo isolamento entre testes mesmo com SQLite em memória.
    """
    session = SessionTeste()
    try:
        yield session
    finally:
        session.rollback()
        # Remove dados já commitados pelos endpoints (ex.: db.commit() no CRUD)
        for tabela in reversed(Base.metadata.sorted_tables):
            session.execute(tabela.delete())
        session.commit()
        session.close()


@pytest.fixture()
def client(db):
    """TestClient com a dependência get_db sobrescrita pelo banco de teste."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(client, db):
    """Cadastra um administrador diretamente no banco e retorna o token JWT."""
    from app import crud, schemas

    # Cadastra admin direto no CRUD (evita dependência circular: criar admin exige token)
    crud.create_administrador(db, schemas.AdministradorCreate(
        nome_administrador="Admin Teste",
        email="admin@teste.com",
        senha="senha123",
        cargo="Coordenador",
        setor="TI",
    ))
    # Faz login via HTTP (username = email)
    login = client.post("/api/v1/auth/token", data={
        "username": "admin@teste.com",
        "password": "senha123",
    })
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token):
    """Headers com Bearer token para requisições autenticadas."""
    return {"Authorization": f"Bearer {admin_token}"}
