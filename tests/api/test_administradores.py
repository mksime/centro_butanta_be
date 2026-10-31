"""Testes de API para a entidade Administrador."""


def test_sem_token_retorna_401(client):
    """Qualquer endpoint sem Bearer token deve retornar 401."""
    assert client.get("/api/v1/administradores/").status_code == 401


def test_listar_administradores_retorna_200(client, auth_headers):
    """A listagem exige autenticação e retorna os administradores cadastrados."""
    response = client.get("/api/v1/administradores/", headers=auth_headers)
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert any(a["nome_administrador"] == "Admin Teste" for a in dados)
    assert any(a["email"] == "admin@teste.com" for a in dados)


def test_buscar_administrador_inexistente_retorna_404(client, auth_headers):
    response = client.get("/api/v1/administradores/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Administrador não encontrado"


def test_criar_administrador_sucesso_retorna_201(client, auth_headers):
    payload = {
        "nome_administrador": "Ana Souza",
        "email": "ana.souza@example.com",
        "senha": "senha123",
        "cargo": "Coordenador",
        "setor": "Administrativo",
    }
    response = client.post("/api/v1/administradores/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nome_administrador"] == "Ana Souza"
    assert data["email"] == "ana.souza@example.com"
    assert data["cargo"] == "Coordenador"
    assert data["setor"] == "Administrativo"
    assert "id_administrador" in data


def test_criar_administrador_sem_email_retorna_422(client, auth_headers):
    """E-mail é obrigatório (usado como username no login)."""
    payload = {
        "nome_administrador": "Ana Souza",
        "senha": "senha123",
        "cargo": "Coordenador",
        "setor": "Administrativo",
    }
    response = client.post("/api/v1/administradores/", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_criar_administrador_email_invalido_retorna_422(client, auth_headers):
    """Email malformado deve ser rejeitado com 422 (validação Pydantic)."""
    payload = {
        "nome_administrador": "Ana Souza",
        "email": "nao-e-email",
        "senha": "senha123",
        "cargo": "Coordenador",
        "setor": "Administrativo",
    }
    response = client.post("/api/v1/administradores/", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_criar_administrador_senha_curta_retorna_422(client, auth_headers):
    """Senha deve ter no mínimo 6 caracteres."""
    payload = {
        "nome_administrador": "Ana Souza",
        "email": "ana.souza@example.com",
        "senha": "123",
        "cargo": "Coordenador",
        "setor": "Administrativo",
    }
    response = client.post("/api/v1/administradores/", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_atualizar_administrador_inexistente_retorna_404(client, auth_headers):
    response = client.put("/api/v1/administradores/9999", json={"cargo": "Gerente"}, headers=auth_headers)
    assert response.status_code == 404


def test_deletar_administrador_sucesso_retorna_204(client, auth_headers):
    criar = client.post("/api/v1/administradores/", json={
        "nome_administrador": "Ana Souza",
        "email": "ana.souza@example.com",
        "senha": "senha123",
        "cargo": "Coordenador",
        "setor": "Administrativo",
    }, headers=auth_headers)
    admin_id = criar.json()["id_administrador"]

    deletar = client.delete(f"/api/v1/administradores/{admin_id}", headers=auth_headers)
    assert deletar.status_code == 204

    buscar = client.get(f"/api/v1/administradores/{admin_id}", headers=auth_headers)
    assert buscar.status_code == 404
