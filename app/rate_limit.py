"""Rate limit compartilhado pela aplicação (slowapi).

O storage padrão é em memória, adequado a uma única instância. Ao escalar
horizontalmente, configure RATE_LIMIT_STORAGE_URI com um Redis (ex.: Render
Key Value) para que o limite seja compartilhado entre as instâncias.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=[],
)
