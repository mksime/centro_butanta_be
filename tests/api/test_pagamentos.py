"""Testes de API para a entidade Pagamento."""


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
    assert client.get("/api/v1/pagamentos/").status_code == 401


def test_listar_pagamentos_vazio_retorna_lista_vazia(client, auth_headers):
    response = client.get("/api/v1/pagamentos/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_buscar_pagamento_inexistente_retorna_404(client, auth_headers):
    response = client.get("/api/v1/pagamentos/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Pagamento não encontrado"


def test_criar_pagamento_associado_inexistente_retorna_404(client, auth_headers):
    """Pagamento só pode ser criado se o associado existir."""
    from datetime import datetime

    payload = {
        "valor": 100.0,
        "nome_pagador": "Maria Silva",
        "modo_pagamento": "pix",
        "dth_pagamento": datetime.now().isoformat(),
        "id_associado": 9999,
    }
    response = client.post("/api/v1/pagamentos/", json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Associado não encontrado"


def test_criar_pagamento_valor_invalido_retorna_422(client, auth_headers):
    """Valor deve ser maior que zero."""
    _, associado = _criar_associado_com_moradia(client, auth_headers)
    from datetime import datetime

    payload = {
        "valor": 0,
        "nome_pagador": "Maria Silva",
        "modo_pagamento": "pix",
        "dth_pagamento": datetime.now().isoformat(),
        "id_associado": associado["id_associado"],
    }
    response = client.post("/api/v1/pagamentos/", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_criar_pagamento_sucesso_retorna_201(client, auth_headers):
    _, associado = _criar_associado_com_moradia(client, auth_headers)
    from datetime import datetime

    payload = {
        "valor": 150.0,
        "recorrente": True,
        "atraso": False,
        "nome_pagador": "Maria Silva",
        "modo_pagamento": "pix",
        "dth_pagamento": datetime.now().isoformat(),
        "taxa": 2.5,
        "parcial": False,
        "id_associado": associado["id_associado"],
    }
    response = client.post("/api/v1/pagamentos/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["valor"] == 150.0
    assert data["recorrente"] is True
    assert data["id_associado"] == associado["id_associado"]
    assert "id_pagamento" in data


def test_atualizar_pagamento_inexistente_retorna_404(client, auth_headers):
    response = client.put("/api/v1/pagamentos/9999", json={"valor": 200.0}, headers=auth_headers)
    assert response.status_code == 404


def test_deletar_pagamento_sucesso_retorna_204(client, auth_headers):
    _, associado = _criar_associado_com_moradia(client, auth_headers)
    from datetime import datetime

    criar = client.post("/api/v1/pagamentos/", json={
        "valor": 100.0,
        "nome_pagador": "Maria Silva",
        "modo_pagamento": "pix",
        "dth_pagamento": datetime.now().isoformat(),
        "id_associado": associado["id_associado"],
    }, headers=auth_headers)
    pagamento_id = criar.json()["id_pagamento"]

    deletar = client.delete(f"/api/v1/pagamentos/{pagamento_id}", headers=auth_headers)
    assert deletar.status_code == 204

    buscar = client.get(f"/api/v1/pagamentos/{pagamento_id}", headers=auth_headers)
    assert buscar.status_code == 404
