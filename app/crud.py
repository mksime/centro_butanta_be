"""CRUD operations for all entities."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_password_hash


# ─── Administrador ──────────────────────────────────────────────────────────

def get_administrador(db: Session, id_administrador: int) -> models.Administrador | None:
    return db.get(models.Administrador, id_administrador)


def get_administradores(db: Session, skip: int = 0, limit: int = 100) -> list[models.Administrador]:
    return list(db.scalars(select(models.Administrador).offset(skip).limit(limit)))


def create_administrador(db: Session, data: schemas.AdministradorCreate) -> models.Administrador:
    admin = models.Administrador(
        **data.model_dump(exclude={"senha"}),
        senha_hash=get_password_hash(data.senha),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def update_administrador(
    db: Session, admin: models.Administrador, data: schemas.AdministradorUpdate
) -> models.Administrador:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(admin, field, value)
    db.commit()
    db.refresh(admin)
    return admin


def delete_administrador(db: Session, admin: models.Administrador) -> None:
    db.delete(admin)
    db.commit()


# ─── Moradia ────────────────────────────────────────────────────────────────

def get_moradia(db: Session, id_moradia: int) -> models.Moradia | None:
    return db.get(models.Moradia, id_moradia)


def get_moradias(db: Session, skip: int = 0, limit: int = 100) -> list[models.Moradia]:
    return list(db.scalars(select(models.Moradia).offset(skip).limit(limit)))


def get_moradia_by_endereco(
    db: Session, cep: str | None, rua: str, numero: str
) -> models.Moradia | None:
    """Busca uma moradia já cadastrada pelo endereço (CEP + rua + número)."""
    return (
        db.scalars(
            select(models.Moradia).filter(
                models.Moradia.cep == cep,
                models.Moradia.rua == rua,
                models.Moradia.numero == numero,
            )
        )
        .first()
    )


def create_moradia(db: Session, data: schemas.MoradiaCreate) -> models.Moradia:
    """Cria uma moradia, mas reaproveita a existente para o mesmo endereço."""
    moradia_existente = get_moradia_by_endereco(db, data.cep, data.rua, data.numero)
    if moradia_existente:
        return moradia_existente
    moradia = models.Moradia(**data.model_dump())
    db.add(moradia)
    db.commit()
    db.refresh(moradia)
    return moradia


def update_moradia(
    db: Session, moradia: models.Moradia, data: schemas.MoradiaUpdate
) -> models.Moradia:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(moradia, field, value)
    db.commit()
    db.refresh(moradia)
    return moradia


def delete_moradia(db: Session, moradia: models.Moradia) -> None:
    db.delete(moradia)
    db.commit()


# ─── Associado ──────────────────────────────────────────────────────────────

def get_associado(db: Session, id_associado: int) -> models.Associado | None:
    return db.get(models.Associado, id_associado)


def get_associados(db: Session, skip: int = 0, limit: int = 100) -> list[models.Associado]:
    return list(db.scalars(select(models.Associado).offset(skip).limit(limit)))


def create_associado(db: Session, data: schemas.AssociadoCreate) -> models.Associado:
    associado = models.Associado(**data.model_dump())
    db.add(associado)
    db.commit()
    db.refresh(associado)
    return associado


def create_associado_com_moradia(
    db: Session,
    moradia_data: schemas.MoradiaCreate,
    associado_data: dict | schemas.AssociadoBase,
) -> models.Associado:
    moradia = create_moradia(db, moradia_data)
    if isinstance(associado_data, dict):
        payload = dict(associado_data)
    else:
        payload = associado_data.model_dump()

    payload["id_moradia"] = moradia.id_moradia
    associado = create_associado(db, schemas.AssociadoCreate(**payload))
    return associado


def update_associado(
    db: Session, associado: models.Associado, data: schemas.AssociadoUpdate
) -> models.Associado:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(associado, field, value)
    db.commit()
    db.refresh(associado)
    return associado


def update_associado_com_moradia(
    db: Session,
    associado: models.Associado,
    moradia_data: schemas.MoradiaUpdate | None = None,
    associado_data: schemas.AssociadoUpdate | None = None,
) -> models.Associado:
    if moradia_data is not None:
        moradia_update = moradia_data.model_dump(exclude_unset=True)
        if moradia_update:
            moradia_existente = get_moradia_by_endereco(
                db,
                moradia_update.get("cep", associado.moradia.cep),
                moradia_update.get("rua", associado.moradia.rua),
                moradia_update.get("numero", associado.moradia.numero),
            )
            if moradia_existente and moradia_existente.id_moradia != associado.id_moradia:
                associado.id_moradia = moradia_existente.id_moradia
                db.commit()
                db.refresh(associado)
            else:
                update_moradia(db, associado.moradia, moradia_data)
                db.refresh(associado)

    if associado_data is not None:
        associado_update = associado_data.model_dump(exclude_unset=True)
        if "id_moradia" in associado_update and associado_update["id_moradia"] is not None:
            associado.id_moradia = associado_update.pop("id_moradia")
        if associado_update:
            associado = update_associado(db, associado, schemas.AssociadoUpdate(**associado_update))

    return associado


def delete_associado(db: Session, associado: models.Associado) -> None:
    db.delete(associado)
    db.commit()


# ─── ComprovanteResidencia ──────────────────────────────────────────────────

def get_comprovante(db: Session, id_comprovante: int) -> models.ComprovanteResidencia | None:
    return db.get(models.ComprovanteResidencia, id_comprovante)


def get_comprovantes(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.ComprovanteResidencia]:
    return list(db.scalars(select(models.ComprovanteResidencia).offset(skip).limit(limit)))


def create_comprovante(
    db: Session, data: schemas.ComprovanteResidenciaCreate
) -> models.ComprovanteResidencia:
    comprovante = models.ComprovanteResidencia(**data.model_dump())
    db.add(comprovante)
    db.commit()
    db.refresh(comprovante)
    return comprovante


def update_comprovante(
    db: Session,
    comprovante: models.ComprovanteResidencia,
    data: schemas.ComprovanteResidenciaUpdate,
) -> models.ComprovanteResidencia:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(comprovante, field, value)
    db.commit()
    db.refresh(comprovante)
    return comprovante


def delete_comprovante(db: Session, comprovante: models.ComprovanteResidencia) -> None:
    db.delete(comprovante)
    db.commit()


# ─── Pagamento ──────────────────────────────────────────────────────────────

def get_pagamento(db: Session, id_pagamento: int) -> models.Pagamento | None:
    return db.get(models.Pagamento, id_pagamento)


def get_pagamentos(db: Session, skip: int = 0, limit: int = 100) -> list[models.Pagamento]:
    return list(db.scalars(select(models.Pagamento).offset(skip).limit(limit)))


def create_pagamento(db: Session, data: schemas.PagamentoCreate) -> models.Pagamento:
    pagamento = models.Pagamento(**data.model_dump())
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def update_pagamento(
    db: Session, pagamento: models.Pagamento, data: schemas.PagamentoUpdate
) -> models.Pagamento:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pagamento, field, value)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def delete_pagamento(db: Session, pagamento: models.Pagamento) -> None:
    db.delete(pagamento)
    db.commit()


def registrar_mensalidade(
    db: Session, associado: models.Associado, data: schemas.MensalidadeUpdate,
    id_administrador: int,
) -> models.Associado:
    associado.situacao_cadastro = "mensalidade_atrasada" if data.atraso else "ativo"
    if not data.atraso:
        associado.data_ultimo_pagamento = data.data_pagamento
    associado.id_administrador = id_administrador
    db.commit()
    db.refresh(associado)
    return associado
