"""Seed inicial: cria o primeiro administrador se a tabela estiver vazia."""

from app import crud, schemas
from app.config import Settings


def seed_initial_admin(db, settings: Settings) -> None:
    """Cria o administrador inicial apenas se não existir nenhum cadastrado.

    Evita o problema do "ovo e a galinha": para criar um administrador via
    HTTP é preciso estar autenticado, mas para se autenticar já é preciso
    ter um administrador no banco.
    """
    from app import models

    existente = db.query(models.Administrador).first()
    if existente:
        return  # já tem admin, não faz nada

    crud.create_administrador(db, schemas.AdministradorCreate(
        nome_administrador="Administrador",
        email=settings.ADMIN_SEED_EMAIL,
        senha=settings.ADMIN_SEED_PASSWORD,
        cargo=settings.ADMIN_SEED_CARGO,
        setor=settings.ADMIN_SEED_SETOR,
    ))
