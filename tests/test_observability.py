"""Testes da integração opcional com o Sentry."""

import pytest

from app import observability
from app.config import settings
from app.observability import _scrub_event, init_sentry


def test_sem_dsn_nao_inicializa(monkeypatch):
    import sentry_sdk

    monkeypatch.setattr(settings, "SENTRY_DSN", None)
    monkeypatch.setattr(sentry_sdk, "init", lambda **kwargs: pytest.fail("não deveria inicializar"))

    init_sentry()


def test_com_dsn_inicializa_sem_enviar_pii(monkeypatch):
    import sentry_sdk

    capturado = {}
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://abc123@o0.ingest.sentry.io/1")
    monkeypatch.setattr(sentry_sdk, "init", lambda **kwargs: capturado.update(kwargs))

    observability.init_sentry()

    assert capturado["dsn"] == settings.SENTRY_DSN
    assert capturado["environment"] == settings.ENVIRONMENT
    assert capturado["send_default_pii"] is False
    assert capturado["max_request_body_size"] == "never"
    assert capturado["before_send"] is observability._scrub_event


def test_scrub_remove_dados_pessoais():
    evento = {
        "user": {"email": "associado@example.com"},
        "request": {
            "data": {"documento": "123.456.789-00", "cidade": "São Paulo"},
            "cookies": {"session": "abc"},
            "headers": {
                "Authorization": "Bearer segredo",
                "Cookie": "session=abc",
                "Content-Type": "application/json",
            },
        },
    }

    limpo = _scrub_event(evento, {})

    assert "user" not in limpo
    assert "data" not in limpo["request"]
    assert "cookies" not in limpo["request"]
    assert limpo["request"]["headers"] == {"Content-Type": "application/json"}
