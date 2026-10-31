"""Testes de API para a entidade Moradia."""


def test_sem_token_retorna_401(client):
    """Qualquer endpoint sem Bearer token deve retornar 401."""
    assert client.get("/api/v1/moradias/").status_code == 401


def test_listar_moradias_vazio_retorna_lista_vazia(client, auth_headers):
    response = client.get("/api/v1/moradias/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_buscar_moradia_inexistente_retorna_404(client, auth_headers):
    response = client.get("/api/v1/moradias/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Moradia não encontrada"


def test_criar_moradia_sucesso_retorna_201(client, auth_headers):
    payload = {
        "rua": "Rua das Flores",
        "numero": "123",
        "bloco": "A",
        "proprietario": "João Silva",
        "numero_residentes": 3,
    }
    response = client.post("/api/v1/moradias/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["rua"] == "Rua das Flores"
    assert data["numero_residentes"] == 3
    assert "id_moradia" in data


def test_atualizar_moradia_inexistente_retorna_404(client, auth_headers):
    response = client.put("/api/v1/moradias/9999", json={"rua": "Nova Rua"}, headers=auth_headers)
    assert response.status_code == 404


def test_deletar_moradia_sucesso_retorna_204(client, auth_headers):
    criar = client.post("/api/v1/moradias/", json={
        "rua": "Rua das Flores",
        "numero": "123",
        "proprietario": "João Silva",
    }, headers=auth_headers)
    moradia_id = criar.json()["id_moradia"]

    deletar = client.delete(f"/api/v1/moradias/{moradia_id}", headers=auth_headers)
    assert deletar.status_code == 204

    buscar = client.get(f"/api/v1/moradias/{moradia_id}", headers=auth_headers)
    assert buscar.status_code == 404
