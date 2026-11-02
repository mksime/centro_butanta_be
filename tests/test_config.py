"""Testes das validações de configuração e do comportamento por ambiente."""

import pytest
from pydantic import ValidationError

from app.config import DEFAULT_SECRET_KEY, MIN_SECRET_KEY_LENGTH, Settings


def test_desenvolvimento_aceita_secret_key_padrao(monkeypatch):
    # _env_file=None só ignora o .env; variáveis de ambiente (como o SECRET_KEY
    # definido no job do CI) continuam tendo precedência. Remova-a para testar
    # de fato o valor padrão.
    monkeypatch.delenv("SECRET_KEY", raising=False)
    settings = Settings(_env_file=None, ENVIRONMENT="development")
    assert settings.is_production is False
    assert settings.SECRET_KEY == DEFAULT_SECRET_KEY


def test_producao_rejeita_secret_key_padrao():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=DEFAULT_SECRET_KEY)


def test_producao_rejeita_secret_key_curta():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="curta")


def test_producao_aceita_secret_key_forte():
    chave = "a" * MIN_SECRET_KEY_LENGTH
    settings = Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=chave)
    assert settings.is_production is True


def test_producao_rejeita_seed_com_senha_padrao():
    with pytest.raises(ValidationError, match="ADMIN_SEED_PASSWORD"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            SECRET_KEY="a" * MIN_SECRET_KEY_LENGTH,
            ADMIN_SEED_ENABLED=True,
            ADMIN_SEED_PASSWORD="admin123",
        )


def test_producao_aceita_seed_com_senha_forte():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        SECRET_KEY="a" * MIN_SECRET_KEY_LENGTH,
        ADMIN_SEED_ENABLED=True,
        ADMIN_SEED_PASSWORD="senha-bem-longa-123",
    )
    assert settings.ADMIN_SEED_ENABLED is True


def test_cors_origins_vem_de_string_separada_por_virgula():
    settings = Settings(
        _env_file=None,
        CORS_ORIGINS="https://app.exemplo.org, https://admin.exemplo.org ,",
    )
    assert settings.cors_origins == [
        "https://app.exemplo.org",
        "https://admin.exemplo.org",
    ]


def test_docs_desabilitados_em_producao(monkeypatch):
    from app.config import settings
    from app.main import create_app

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    app_prod = create_app()
    assert app_prod.docs_url is None
    assert app_prod.redoc_url is None
    assert app_prod.openapi_url is None

    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    app_dev = create_app()
    assert app_dev.docs_url == "/docs"
    assert app_dev.openapi_url == "/openapi.json"
