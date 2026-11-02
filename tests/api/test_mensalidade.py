import pytest


def create_person(client, headers, status="ativo"):
    home = client.post('/api/v1/moradias/', json={"rua": "Rua Teste", "numero": "1", "proprietario": "Pessoa Teste"}, headers=headers).json()
    return client.post('/api/v1/associados/', json={"nome": "Pessoa Teste", "data_nascimento": "1990-01-01", "id_moradia": home['id_moradia'], "situacao_cadastro": status}, headers=headers).json()


def test_pagamento_e_atraso_persistem_sem_criar_pagamento_ficticio(client, auth_headers):
    person = create_person(client, auth_headers)
    url = f"/api/v1/associados/{person['id_associado']}/mensalidade"
    paid = client.put(url, json={"atraso": False, "data_pagamento": "2026-11-01"}, headers=auth_headers)
    assert paid.status_code == 200
    assert paid.json()['situacao_cadastro'] == 'ativo'
    assert paid.json()['data_ultimo_pagamento'] == '2026-11-01'
    late = client.put(url, json={"atraso": True}, headers=auth_headers)
    assert late.status_code == 200
    saved = client.get(f"/api/v1/associados/{person['id_associado']}", headers=auth_headers).json()
    assert saved['situacao_cadastro'] == 'mensalidade_atrasada'
    assert saved['data_ultimo_pagamento'] == '2026-11-01'
    paid_again = client.put(url, json={"atraso": False, "data_pagamento": "2026-11-02"}, headers=auth_headers)
    assert paid_again.json()['situacao_cadastro'] == 'ativo'
    assert paid_again.json()['data_ultimo_pagamento'] == '2026-11-02'
    assert client.get('/api/v1/pagamentos/', headers=auth_headers).json() == []


@pytest.mark.parametrize('body', [
    {"atraso": False}, {"atraso": False, "data_pagamento": "2026-02-31"},
    {"atraso": True, "data_pagamento": "2026-11-01"}, {},
])
def test_mensalidade_rejeita_payload_invalido(client, auth_headers, body):
    person = create_person(client, auth_headers)
    response = client.put(f"/api/v1/associados/{person['id_associado']}/mensalidade", json=body, headers=auth_headers)
    assert response.status_code == 422
    saved = client.get(f"/api/v1/associados/{person['id_associado']}", headers=auth_headers).json()
    assert saved['situacao_cadastro'] == 'ativo'


def test_mensalidade_exige_autenticacao_e_associado_existente(client, auth_headers):
    assert client.put('/api/v1/associados/999/mensalidade', json={"atraso": True}).status_code == 401
    assert client.put('/api/v1/associados/999/mensalidade', json={"atraso": True}, headers=auth_headers).status_code == 404


@pytest.mark.parametrize('status', ['pendente', 'inativo'])
def test_mensalidade_nao_ativa_cadastro_pendente_ou_inativo(client, auth_headers, status):
    person = create_person(client, auth_headers, status)
    response = client.put(f"/api/v1/associados/{person['id_associado']}/mensalidade", json={"atraso": True}, headers=auth_headers)
    assert response.status_code == 409
