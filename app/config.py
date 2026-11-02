from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

DEFAULT_SECRET_KEY = "mude-em-producao-chave-secreta-min-32-caracteres"
DEFAULT_ADMIN_SEED_PASSWORD = "admin123"
MIN_SECRET_KEY_LENGTH = 32
MIN_SEED_PASSWORD_LENGTH = 12


def normalize_database_url(url: str) -> str:
    """Normaliza a URL do banco para o driver psycopg2 do SQLAlchemy.

    Plataformas como o Render entregam ``postgresql://...`` (e algumas
    versões antigas ``postgres://``). O SQLAlchemy 2.x rejeita o prefixo
    ``postgres://`` e precisa do driver explícito.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url.split("://", 1)[1]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url.split("://", 1)[1]
    return url


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Ambiente: controla CORS, /docs e validações de produção
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"

    # Database
    # DATABASE_URL tem precedência (Render, Cloud Run, etc.). Quando ausente,
    # a URL é montada a partir das variáveis POSTGRES_* (desenvolvimento local).
    DATABASE_URL: str | None = None
    POSTGRES_USER: str = "cbbe"
    POSTGRES_PASSWORD: str = "cbbe_secret"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "centro_butanta"

    # App
    APP_NAME: str = "Centro Comunitário Butantã API"
    APP_V1_PREFIX: str = "/api/v1"

    # CORS — lista de origens separadas por vírgula
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Auth
    SECRET_KEY: str = DEFAULT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate limit (slowapi)
    RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT: str = "5/minute"
    # "memory://" funciona com uma instância. Para várias instâncias use
    # "redis://host:porta" (requer o pacote `redis` instalado).
    RATE_LIMIT_STORAGE_URI: str = "memory://"

    # Observabilidade (Sentry) — desativado se SENTRY_DSN não for definida
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.0, ge=0.0, le=1.0)
    SENTRY_RELEASE: str | None = None

    # Seed do administrador inicial (desenvolvimento / primeiro deploy)
    ADMIN_SEED_ENABLED: bool = False
    ADMIN_SEED_EMAIL: str = "admin@centrobutanta.com"
    ADMIN_SEED_PASSWORD: str = DEFAULT_ADMIN_SEED_PASSWORD
    ADMIN_SEED_CARGO: str = "Coordenador"
    ADMIN_SEED_SETOR: str = "Administrativo"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins(self) -> list[str]:
        """Origens permitidas, ignorando espaços e entradas vazias."""
        return [origem.strip() for origem in self.CORS_ORIGINS.split(",") if origem.strip()]

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str | URL:
        """URL de conexão usada pelo SQLAlchemy e pelo Alembic."""
        if self.DATABASE_URL:
            return normalize_database_url(self.DATABASE_URL)

        # URL.create faz o escape correto de senhas com @, :, / etc.
        return URL.create(
            "postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )

    @model_validator(mode="after")
    def _validate_production_settings(self) -> "Settings":
        """Falha no startup se produção estiver com configuração insegura."""
        if not self.is_production:
            return self

        erros: list[str] = []

        if self.SECRET_KEY == DEFAULT_SECRET_KEY:
            erros.append(
                "SECRET_KEY ainda é o valor padrão; defina uma chave aleatória "
                "(ex.: `openssl rand -hex 32`)."
            )
        elif len(self.SECRET_KEY.strip()) < MIN_SECRET_KEY_LENGTH:
            erros.append(
                f"SECRET_KEY deve ter ao menos {MIN_SECRET_KEY_LENGTH} caracteres."
            )

        if self.ADMIN_SEED_ENABLED and (
            self.ADMIN_SEED_PASSWORD == DEFAULT_ADMIN_SEED_PASSWORD
            or len(self.ADMIN_SEED_PASSWORD) < MIN_SEED_PASSWORD_LENGTH
        ):
            erros.append(
                "ADMIN_SEED_PASSWORD é fraca; use ao menos "
                f"{MIN_SEED_PASSWORD_LENGTH} caracteres e troque a senha após o "
                "primeiro acesso."
            )

        if erros:
            raise ValueError(" ".join(erros))

        return self


settings = Settings()
