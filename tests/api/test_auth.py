"""Testes rápidos de autenticação: cadastro → login → rota protegida."""

from app import crud, schemas


def test_cadastro_e_login_fluxo_completo(client, db):
    """Cadastra admin via CRUD, faz login com email, acessa rota protegida com e sem token."""

    # 1) Cadastra admin diretamente no banco (CRUD exige token via HTTP)
    crud.create_administrador(db, schemas.AdministradorCreate(
        nome_administrador="Ana Souza",
        email="ana.souza@example.com",
        senha="senha123",
        cargo="Coordenador",
        setor="Administrativo",
    ))

    # 2) Login para obter o token JWT (username = email)
    login = client.post("/api/v1/auth/token", data={
        "username": "ana.souza@example.com",
        "password": "senha123",
    })
    assert login.status_code == 200, login.text
    token_data = login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 3) Acesso SEM token deve retornar 401
    sem_token = client.get("/api/v1/administradores/")
    assert sem_token.status_code == 401

    # 4) Acesso COM token deve retornar 200
    com_token = client.get(
        "/api/v1/administradores/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert com_token.status_code == 200
    admins = com_token.json()
    assert any(a["nome_administrador"] == "Ana Souza" for a in admins)
    assert any(a["email"] == "ana.souza@example.com" for a in admins)

    # 5) Token com senha errada deve falhar
    login_errado = client.post("/api/v1/auth/token", data={
        "username": "ana.souza@example.com",
        "password": "senha_errada",
    })
    assert login_errado.status_code == 401

    # 6) Usuário inexistente (email) deve falhar
    login_inexistente = client.post("/api/v1/auth/token", data={
        "username": "nao_existe@example.com",
        "password": "qualquercoisa",
    })
    assert login_inexistente.status_code == 401
