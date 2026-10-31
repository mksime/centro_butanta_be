"""Fixtures compartilhadas para os testes da API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Banco em memória (SQLite) — não depende do PostgreSQL rodar
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # obrigatório para :memory: ser compartilhado entre sessões
)
SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def tabelas():
    """Cria todas as tabelas uma vez por sessão de testes."""
    Base.metadata.create_all(bind=engine)
    yield
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
