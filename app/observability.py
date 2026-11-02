"""Integração opcional com o Sentry.

Só é ativada quando SENTRY_DSN está definida, então desenvolvimento e testes
seguem sem dependência de rede.
"""

from typing import Any

from app.config import settings

# Headers que nunca devem sair do processo (tokens de autenticação).
HEADERS_SENSIVEIS = {"authorization", "cookie", "set-cookie", "x-api-key"}


def _scrub_event(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any]:
    """Remove dados pessoais do evento antes do envio (LGPD).

    O corpo da requisição pode conter documento, endereço e telefone; por isso
    ele é descartado inteiro, junto com cookies e headers de autenticação.
    """
    event.pop("user", None)

    request = event.get("request")
    if isinstance(request, dict):
        request.pop("data", None)
        request.pop("cookies", None)
        headers = request.get("headers")
        if isinstance(headers, dict):
            for header in list(headers):
                if header.lower() in HEADERS_SENSIVEIS:
                    headers.pop(header)

    return event


def init_sentry() -> None:
    """Inicializa o Sentry se houver DSN configurada."""
    if not settings.SENTRY_DSN:
        return

    # Import tardio: evita custo e erro de importação quando o Sentry está off.
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.SENTRY_RELEASE or None,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
        max_request_body_size="never",
        integrations=[StarletteIntegration(), FastApiIntegration()],
        before_send=_scrub_event,
    )
