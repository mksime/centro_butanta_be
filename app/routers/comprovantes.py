from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/comprovantes", tags=["Comprovantes de Residência"])


@router.get("/", response_model=list[schemas.ComprovanteResidenciaOut])
def list_comprovantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_comprovantes(db, skip=skip, limit=limit)


@router.get("/{id_comprovante}", response_model=schemas.ComprovanteResidenciaOut)
def get_comprovante(id_comprovante: int, db: Session = Depends(get_db)):
    comprovante = crud.get_comprovante(db, id_comprovante)
    if not comprovante:
        raise HTTPException(status_code=404, detail="Comprovante não encontrado")
    return comprovante


@router.post("/", response_model=schemas.ComprovanteResidenciaOut, status_code=201)
def create_comprovante(
    data: schemas.ComprovanteResidenciaCreate, db: Session = Depends(get_db)
):
    associado = crud.get_associado(db, data.id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    return crud.create_comprovante(db, data)


@router.put("/{id_comprovante}", response_model=schemas.ComprovanteResidenciaOut)
def update_comprovante(
    id_comprovante: int,
    data: schemas.ComprovanteResidenciaUpdate,
    db: Session = Depends(get_db),
):
    comprovante = crud.get_comprovante(db, id_comprovante)
    if not comprovante:
        raise HTTPException(status_code=404, detail="Comprovante não encontrado")
    if data.id_administrador is not None:
        admin = crud.get_administrador(db, data.id_administrador)
        if not admin:
            raise HTTPException(status_code=404, detail="Administrador não encontrado")
    return crud.update_comprovante(db, comprovante, data)


@router.delete("/{id_comprovante}", status_code=204)
def delete_comprovante(id_comprovante: int, db: Session = Depends(get_db)):
    comprovante = crud.get_comprovante(db, id_comprovante)
    if not comprovante:
        raise HTTPException(status_code=404, detail="Comprovante não encontrado")
    crud.delete_comprovante(db, comprovante)
