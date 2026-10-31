"""Testes unitários da camada CRUD (sem HTTP)."""


def test_create_and_get_administrador(db):
    from app import crud, schemas

    admin = crud.create_administrador(db, schemas.AdministradorCreate(
        nome_administrador="Ana Souza",
        email="ana.souza@example.com",
        senha="senha123",
        cargo="Coordenador",
        setor="Administrativo",
    ))
    assert admin.id_administrador is not None

    buscado = crud.get_administrador(db, admin.id_administrador)
    assert buscado is not None
    assert buscado.nome_administrador == "Ana Souza"
    assert buscado.email == "ana.souza@example.com"


def test_get_administradores_limita_resultados(db):
    from app import crud, schemas

    for i in range(15):
        crud.create_administrador(db, schemas.AdministradorCreate(
            nome_administrador=f"Admin {i}",
            email=f"admin{i}@example.com",
            senha="senha123",
            cargo="Cargo",
            setor="Setor",
        ))

    todos = crud.get_administradores(db)
    assert len(todos) == 15

    limitados = crud.get_administradores(db, skip=0, limit=5)
    assert len(limitados) == 5


def test_update_and_delete_administrador(db):
    from app import crud, schemas

    admin = crud.create_administrador(db, schemas.AdministradorCreate(
        nome_administrador="Ana Souza",
        email="ana.souza@example.com",
        senha="senha123",
        cargo="Coordenador",
        setor="Administrativo",
    ))

    atualizado = crud.update_administrador(
        db, admin, schemas.AdministradorUpdate(cargo="Gerente")
    )
    assert atualizado.cargo == "Gerente"
    assert atualizado.nome_administrador == "Ana Souza"

    crud.delete_administrador(db, admin)
    assert crud.get_administrador(db, admin.id_administrador) is None
