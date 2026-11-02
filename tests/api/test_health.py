"""Testes dos endpoints de saúde e readiness."""

from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


def test_health_responde_ok(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_ready_responde_ok_com_banco_disponivel(client):
    resposta = client.get("/ready")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_ready_retorna_503_com_banco_indisponivel(client):
    class SessaoIndisponivel:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("banco fora do ar"))

    def override_indisponivel():
        yield SessaoIndisponivel()

    original = app.dependency_overrides[get_db]
    app.dependency_overrides[get_db] = override_indisponivel
    try:
        resposta = client.get("/ready")
    finally:
        app.dependency_overrides[get_db] = original

    assert resposta.status_code == 503
    assert resposta.json()["detail"] == "Banco de dados indisponível"
