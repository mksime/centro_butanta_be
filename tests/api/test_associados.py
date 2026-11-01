"""Testes de API para a entidade Associado (Red → Green → Refactor)."""

def _criar_moradia(client, auth_headers):
    """Helper para criar uma moradia válida (endereço)."""
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


def test_criar_associado_ignora_id_administrador_do_cliente(client, auth_headers, db):
    """O administrador autenticado deve ser o único registro persistido no campo id_administrador."""
    moradia = _criar_moradia(client, auth_headers)
    admin = db.query(__import__('app.models', fromlist=['Administrador']).Administrador).filter_by(email="admin@teste.com").first()
    payload = {
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
        "id_administrador": admin.id_administrador + 999,
    }
    response = client.post("/api/v1/associados/", json=payload, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Você não pode atribuir outro administrador"


def test_criar_associado_com_documento_e_tipo_associacao_retorna_201(client, auth_headers):
    """Documento e tipo_associacao são opcionais e devem ser persistidos."""
    moradia = _criar_moradia(client, auth_headers)
    response = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "documento": "12345678900",
        "tipo_associacao": "temporaria",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["documento"] == "12345678900"
    assert data["tipo_associacao"] == "temporaria"


def test_criar_associado_sucesso_retorna_201(client, auth_headers):
    """Criação válida deve retornar 201 com os dados do associado."""
    moradia = _criar_moradia(client, auth_headers)
    response = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "nome_social": "Maria",
        "data_nascimento": "1990-05-10",
        "telefone": "(11) 99999-9999",
        "email": "maria@example.com",
        "num_carteira_associado": "CART-001",
        "situacao_cadastro": "ativo",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Maria Silva"
    assert data["email"] == "maria@example.com"
    assert data["situacao_cadastro"] == "ativo"
    assert data["id_moradia"] == moradia["id_moradia"]
    assert "id_associado" in data


def test_criar_moradia_e_associado_juntos_reaproveita_endereco(client, auth_headers):
    """A criação conjunta deve criar a moradia quando ainda não existir e reaproveitar o ID existente."""
    payload = {
        "moradia": {
            "rua": "Rua das Flores",
            "numero": "123",
            "cep": "01311-000",
            "cidade": "São Paulo",
            "estado": "SP",
            "complemento": "Apto 10",
            "proprietario": "João Silva",
        },
        "associado": {
            "nome": "Maria Silva",
            "data_nascimento": "1990-01-01",
            "email": "maria@example.com",
        },
    }

    primeira = client.post("/api/v1/associados/completo", json=payload, headers=auth_headers)
    segunda = client.post("/api/v1/associados/completo", json=payload, headers=auth_headers)

    assert primeira.status_code == 201
    assert segunda.status_code == 201
    assert segunda.json()["id_moradia"] == primeira.json()["id_moradia"]
    assert segunda.json()["id_associado"] != primeira.json()["id_associado"]


def test_atualizar_associado_e_moradia_juntos_retorna_200(client, auth_headers, db):
    """PUT conjunto deve atualizar os dados do associado e da moradia vinculada."""
    moradia = _criar_moradia(client, auth_headers)
    associado = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers).json()

    response = client.put(f"/api/v1/associados/completo/{associado['id_associado']}", json={
        "moradia": {
            "rua": "Rua Nova",
            "numero": "456",
            "cep": "01000-000",
            "cidade": "São Paulo",
            "estado": "SP",
            "proprietario": "João Souza",
        },
        "associado": {
            "nome": "Maria Souza",
            "email": "maria.nova@example.com",
        },
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Maria Souza"
    assert data["email"] == "maria.nova@example.com"
    assert data["id_associado"] == associado["id_associado"]
    assert data["id_moradia"] == moradia["id_moradia"]


def test_atualizar_associado_inexistente_retorna_404(client, auth_headers):
    """PUT em um ID que não existe deve retornar 404."""
    response = client.put("/api/v1/associados/9999", json={"nome": "Nome Qualquer"}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Associado não encontrado"


def test_atualizar_associado_moradia_inexistente_retorna_404(client, auth_headers):
    """Tentar atualizar o id_moradia para uma moradia inexistente deve falhar."""
    moradia = _criar_moradia(client, auth_headers)
    associado = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers).json()
    response = client.put(f"/api/v1/associados/{associado['id_associado']}", json={"id_moradia": 9999}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Moradia não encontrada"


def test_deletar_associado_inexistente_retorna_404(client, auth_headers):
    """DELETE em um ID que não existe deve retornar 404."""
    response = client.delete("/api/v1/associados/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Associado não encontrado"


def test_deletar_associado_sucesso_retorna_204(client, auth_headers):
    """DELETE válido deve retornar 204 e remover o associado."""
    moradia = _criar_moradia(client, auth_headers)
    associado = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers).json()
    associado_id = associado["id_associado"]

    deletar = client.delete(f"/api/v1/associados/{associado_id}", headers=auth_headers)
    assert deletar.status_code == 204

    buscar = client.get(f"/api/v1/associados/{associado_id}", headers=auth_headers)
    assert buscar.status_code == 404
