from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/associados", tags=["Associados"])


@router.get("/", response_model=list[schemas.AssociadoOut])
def list_associados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_associados(db, skip=skip, limit=limit)


@router.get("/{id_associado}", response_model=schemas.AssociadoOut)
def get_associado(id_associado: int, db: Session = Depends(get_db)):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    return associado


@router.post("/", response_model=schemas.AssociadoOut, status_code=201)
def create_associado(data: schemas.AssociadoCreate, db: Session = Depends(get_db)):
    moradia = crud.get_moradia(db, data.id_moradia)
    if not moradia:
        raise HTTPException(status_code=404, detail="Moradia não encontrada")
    return crud.create_associado(db, data)


@router.put("/{id_associado}", response_model=schemas.AssociadoOut)
def update_associado(
    id_associado: int, data: schemas.AssociadoUpdate, db: Session = Depends(get_db)
):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    if data.id_moradia is not None:
        moradia = crud.get_moradia(db, data.id_moradia)
        if not moradia:
            raise HTTPException(status_code=404, detail="Moradia não encontrada")
    return crud.update_associado(db, associado, data)


@router.delete("/{id_associado}", status_code=204)
def delete_associado(id_associado: int, db: Session = Depends(get_db)):
    associado = crud.get_associado(db, id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    crud.delete_associado(db, associado)
