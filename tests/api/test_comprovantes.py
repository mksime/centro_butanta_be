"""Testes de API para a entidade Comprovante de Residência."""


def _criar_associado_com_moradia(client, auth_headers):
    """Helper: cria moradia e associado, retorna os IDs."""
    moradia = client.post("/api/v1/moradias/", json={
        "rua": "Rua das Flores",
        "numero": "123",
        "proprietario": "João Silva",
    }, headers=auth_headers).json()

    associado = client.post("/api/v1/associados/", json={
        "nome": "Maria Silva",
        "data_nascimento": "1990-01-01",
        "email": "maria@example.com",
        "id_moradia": moradia["id_moradia"],
    }, headers=auth_headers).json()

    return moradia, associado


def test_sem_token_retorna_401(client):
    """Qualquer endpoint sem Bearer token deve retornar 401."""
    assert client.get("/api/v1/comprovantes/").status_code == 401


def test_listar_comprovantes_vazio_retorna_lista_vazia(client, auth_headers):
    response = client.get("/api/v1/comprovantes/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_buscar_comprovante_inexistente_retorna_404(client, auth_headers):
    response = client.get("/api/v1/comprovantes/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Comprovante não encontrado"


def test_criar_comprovante_associado_inexistente_retorna_404(client, auth_headers):
    """Comprovante só pode ser criado se o associado existir."""
    payload = {
        "tipo_documento": "agua",
        "caminho_arquivo": "/uploads/comprovante.pdf",
        "id_associado": 9999,
    }
    response = client.post("/api/v1/comprovantes/", json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Associado não encontrado"


def test_criar_comprovante_sucesso_retorna_201(client, auth_headers):
    _, associado = _criar_associado_com_moradia(client, auth_headers)
    payload = {
        "tipo_documento": "agua",
        "caminho_arquivo": "/uploads/comprovante.pdf",
        "id_associado": associado["id_associado"],
    }
    response = client.post("/api/v1/comprovantes/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["tipo_documento"] == "agua"
    assert data["id_associado"] == associado["id_associado"]
    assert data["status_aprovacao"] == "pendente"
    assert "id_comprovante" in data


def test_atualizar_comprovante_inexistente_retorna_404(client, auth_headers):
    response = client.put("/api/v1/comprovantes/9999", json={"status_aprovacao": "aprovado"}, headers=auth_headers)
    assert response.status_code == 404


def test_deletar_comprovante_sucesso_retorna_204(client, auth_headers):
    _, associado = _criar_associado_com_moradia(client, auth_headers)
    criar = client.post("/api/v1/comprovantes/", json={
        "tipo_documento": "luz",
        "caminho_arquivo": "/uploads/luz.pdf",
        "id_associado": associado["id_associado"],
    }, headers=auth_headers)
    comprovante_id = criar.json()["id_comprovante"]

    deletar = client.delete(f"/api/v1/comprovantes/{comprovante_id}", headers=auth_headers)
    assert deletar.status_code == 204

    buscar = client.get(f"/api/v1/comprovantes/{comprovante_id}", headers=auth_headers)
    assert buscar.status_code == 404
