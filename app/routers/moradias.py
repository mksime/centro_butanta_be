from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/moradias", tags=["Moradias"])


@router.get("/", response_model=list[schemas.MoradiaOut])
def list_moradias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_moradias(db, skip=skip, limit=limit)


@router.get("/{id_moradia}", response_model=schemas.MoradiaOut)
def get_moradia(id_moradia: int, db: Session = Depends(get_db)):
    moradia = crud.get_moradia(db, id_moradia)
    if not moradia:
        raise HTTPException(status_code=404, detail="Moradia não encontrada")
    return moradia


@router.post("/", response_model=schemas.MoradiaOut, status_code=201)
def create_moradia(data: schemas.MoradiaCreate, db: Session = Depends(get_db)):
    return crud.create_moradia(db, data)


@router.put("/{id_moradia}", response_model=schemas.MoradiaOut)
def update_moradia(
    id_moradia: int, data: schemas.MoradiaUpdate, db: Session = Depends(get_db)
):
    moradia = crud.get_moradia(db, id_moradia)
    if not moradia:
        raise HTTPException(status_code=404, detail="Moradia não encontrada")
    return crud.update_moradia(db, moradia, data)


@router.delete("/{id_moradia}", status_code=204)
def delete_moradia(id_moradia: int, db: Session = Depends(get_db)):
    moradia = crud.get_moradia(db, id_moradia)
    if not moradia:
        raise HTTPException(status_code=404, detail="Moradia não encontrada")
    crud.delete_moradia(db, moradia)
