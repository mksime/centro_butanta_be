from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.dependencies import get_current_active_admin

router = APIRouter(prefix="/administradores", tags=["Administradores"])


@router.get("/", response_model=list[schemas.AdministradorOut])
def list_administradores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    return crud.get_administradores(db, skip=skip, limit=limit)


@router.get("/{id_administrador}", response_model=schemas.AdministradorOut)
def get_administrador(
    id_administrador: int,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    admin_db = crud.get_administrador(db, id_administrador)
    if not admin_db:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")
    return admin_db


@router.post("/", response_model=schemas.AdministradorOut, status_code=201)
def create_administrador(
    data: schemas.AdministradorCreate,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    return crud.create_administrador(db, data)


@router.put("/{id_administrador}", response_model=schemas.AdministradorOut)
def update_administrador(
    id_administrador: int,
    data: schemas.AdministradorUpdate,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    admin_db = crud.get_administrador(db, id_administrador)
    if not admin_db:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")
    return crud.update_administrador(db, admin_db, data)


@router.delete("/{id_administrador}", status_code=204)
def delete_administrador(
    id_administrador: int,
    db: Session = Depends(get_db),
    admin: models.Administrador = Depends(get_current_active_admin),
):
    admin_db = crud.get_administrador(db, id_administrador)
    if not admin_db:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")
    crud.delete_administrador(db, admin_db)
