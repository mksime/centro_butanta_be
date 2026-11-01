from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.dependencies import get_current_active_admin

router = APIRouter(prefix="/associados", tags=["Associados"])


@router.get("/", response_model=list[schemas.AssociadoOut])
def list_associados(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    return crud.get_associados(db, skip=skip, limit=limit)


@router.get("/{id_associado}", response_model=schemas.AssociadoOut)
def get_associado(
    id_associado: int,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    return associado


@router.post("/", response_model=schemas.AssociadoOut, status_code=201)
def create_associado(
    data: schemas.AssociadoCreate,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    moradia = crud.get_moradia(db, data.id_moradia)
    if not moradia:
        raise HTTPException(status_code=404, detail="Moradia não encontrada")
    if data.id_administrador is not None and data.id_administrador != admin.id_administrador:
        raise HTTPException(status_code=403, detail="Você não pode atribuir outro administrador")

    payload = data.model_dump(exclude={"id_administrador"}, exclude_unset=True)
    payload["id_administrador"] = admin.id_administrador
    return crud.create_associado(db, schemas.AssociadoCreate(**payload))


@router.post("/completo", response_model=schemas.AssociadoOut, status_code=201)
@router.post("/juntos", response_model=schemas.AssociadoOut, status_code=201)
@router.post("/com-moradia", response_model=schemas.AssociadoOut, status_code=201)
def create_associado_completo(
    payload: schemas.AssociadoComMoradiaCreate,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    if payload.moradia is None or payload.associado is None:
        raise HTTPException(
            status_code=422,
            detail="Payload deve conter os dados da moradia e do associado.",
        )
    if payload.associado.id_administrador is not None and payload.associado.id_administrador != admin.id_administrador:
        raise HTTPException(status_code=403, detail="Você não pode atribuir outro administrador")

    associado_payload = payload.associado.model_dump(exclude={"id_administrador"}, exclude_unset=True)
    associado_payload["id_administrador"] = admin.id_administrador
    return crud.create_associado_com_moradia(db, payload.moradia, associado_payload)


@router.put("/{id_associado}", response_model=schemas.AssociadoOut)
def update_associado(
    id_associado: int,
    data: schemas.AssociadoUpdate,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    if data.id_moradia is not None:
        moradia = crud.get_moradia(db, data.id_moradia)
        if not moradia:
            raise HTTPException(status_code=404, detail="Moradia não encontrada")
    if data.id_administrador is not None and data.id_administrador != admin.id_administrador:
        raise HTTPException(status_code=403, detail="Você não pode atribuir outro administrador")

    payload = data.model_dump(exclude={"id_administrador"}, exclude_unset=True)
    payload["id_administrador"] = admin.id_administrador
    return crud.update_associado(db, associado, schemas.AssociadoUpdate(**payload))


@router.put("/completo/{id_associado}", response_model=schemas.AssociadoOut)
@router.put("/juntos/{id_associado}", response_model=schemas.AssociadoOut)
@router.put("/com-moradia/{id_associado}", response_model=schemas.AssociadoOut)
def update_associado_completo(
    id_associado: int,
    payload: schemas.AssociadoComMoradiaUpdate,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    if payload.moradia is None and payload.associado is None:
        raise HTTPException(
            status_code=422,
            detail="Payload deve conter os dados da moradia e/ou do associado.",
        )

    if payload.associado is not None:
        if payload.associado.id_administrador is not None and payload.associado.id_administrador != admin.id_administrador:
            raise HTTPException(status_code=403, detail="Você não pode atribuir outro administrador")
        if payload.associado.id_moradia is not None:
            moradia = crud.get_moradia(db, payload.associado.id_moradia)
            if not moradia:
                raise HTTPException(status_code=404, detail="Moradia não encontrada")

    associado_data = None
    if payload.associado is not None:
        associado_payload = payload.associado.model_dump(exclude={"id_administrador"}, exclude_unset=True)
        associado_payload["id_administrador"] = admin.id_administrador
        associado_data = schemas.AssociadoUpdate(**associado_payload)

    return crud.update_associado_com_moradia(
        db,
        associado,
        moradia_data=payload.moradia,
        associado_data=associado_data,
    )


@router.delete("/{id_associado}", status_code=204)
def delete_associado(
    id_associado: int,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    crud.delete_associado(db, associado)
