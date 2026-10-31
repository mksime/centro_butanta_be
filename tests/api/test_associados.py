"""Testes de API para a entidade Associado (Red → Green → Refactor)."""

from datetime import date, datetime


def _criar_moradia(client, auth_headers):
    """Helper para criar uma moradia válida (pré-requisito do associado)."""
    payload = {
        "rua": "Rua das Flores",
        "numero": "123",
        "proprietario": "João Silva",
    }
    return client.post("/api/v1/moradias/", json=payload, headers=auth_headers).json()


def test_sem_token_retorna_401(client):
    """Qualquer endpoint sem Bearer token deve retornar 401."""
    assert client.get("/api/v1/associados/").status_code == 401


def test_listar_associados_vazio_retorna_lista_vazia(client, auth_headers):
    """Sem nenhum associado cadastrado, deve retornar lista vazia."""
    response = client.get("/api/v1/associados/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_buscar_associado_inexistente_retorna_404(client, auth_headers):
    """GET em um ID que não existe deve retornar 404."""
    response = client.get("/api/v1/associados/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Associado não encontrado"


def test_criar_associado_moradia_inexistente_retorna_404(client, auth_headers):
    """Associado só pode ser criado se a moradia referenciada existir."""
    payload = {
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": 9999,
    }
    response = client.post("/api/v1/associados/", json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Moradia não encontrada"


def test_criar_associado_email_invalido_retorna_422(client, auth_headers):
    """Email malformado deve ser rejeitado com 422 (validação Pydantic)."""
    _criar_moradia(client, auth_headers)
    payload = {
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "nao-e-email",
        "id_moradia": 1,
    }
    response = client.post("/api/v1/associados/", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_criar_associado_sucesso_retorna_201(client, auth_headers):
    """Criação válida deve retornar 201 com os dados do associado."""
    moradia = _criar_moradia(client, auth_headers)
    payload = {
        "nome": "Maria Silva",
        "nome_social": "Maria",
        "data_nascimento": "1990-05-10",
        "telefone": "(11) 99999-9999",
        "email": "maria@example.com",
        "num_carteira_associado": "CART-001",
        "situacao_cadastro": "ativo",
        "id_moradia": moradia["id_moradia"],
    }
    response = client.post("/api/v1/associados/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Maria Silva"
    assert data["email"] == "maria@example.com"
    assert data["situacao_cadastro"] == "ativo"
    assert data["id_moradia"] == moradia["id_moradia"]
    assert "id_associado" in data


def test_criar_associado_com_documento_e_tipo_associacao_retorna_201(client, auth_headers):
    """Documento e tipo_associacao são opcionais e devem ser persistidos."""
    moradia = _criar_moradia(client, auth_headers)
    payload = {
        "nome": "João Pereira",
        "data_nascimento": "1990-01-01",
        "documento": "12345678900",
        "tipo_associacao": "temporaria",
        "id_moradia": moradia["id_moradia"],
    }
    response = client.post("/api/v1/associados/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["documento"] == "12345678900"
    assert data["tipo_associacao"] == "temporaria"


def test_atualizar_associado_inexistente_retorna_404(client, auth_headers):
    """PUT em um ID que não existe deve retornar 404."""
    payload = {"nome": "Nome Qualquer"}
    response = client.put("/api/v1/associados/9999", json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Associado não encontrado"


def test_atualizar_associado_moradia_inexistente_retorna_404(client, auth_headers):
    """Tentar atualizar o id_moradia para uma moradia inexistente deve falhar."""
    moradia = _criar_moradia(client, auth_headers)
    criar = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers)
    associado_id = criar.json()["id_associado"]

    response = client.put(
        f"/api/v1/associados/{associado_id}",
        json={"id_moradia": 9999},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Moradia não encontrada"


def test_deletar_associado_inexistente_retorna_404(client, auth_headers):
    """DELETE em um ID que não existe deve retornar 404."""
    response = client.delete("/api/v1/associados/9999", headers=auth_headers)
    assert response.status_code == 404


def test_deletar_associado_sucesso_retorna_204(client, auth_headers):
    """DELETE válido deve retornar 204 e remover o associado."""
    moradia = _criar_moradia(client, auth_headers)
    criar = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers)
    associado_id = criar.json()["id_associado"]

    deletar = client.delete(f"/api/v1/associados/{associado_id}", headers=auth_headers)
    assert deletar.status_code == 204

    buscar = client.get(f"/api/v1/associados/{associado_id}", headers=auth_headers)
    assert buscar.status_code == 404
