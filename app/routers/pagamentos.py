from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


@router.get("/", response_model=list[schemas.PagamentoOut])
def list_pagamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pagamentos(db, skip=skip, limit=limit)


@router.get("/{id_pagamento}", response_model=schemas.PagamentoOut)
def get_pagamento(id_pagamento: int, db: Session = Depends(get_db)):
    pagamento = crud.get_pagamento(db, id_pagamento)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento


@router.post("/", response_model=schemas.PagamentoOut, status_code=201)
def create_pagamento(data: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    associado = crud.get_associado(db, data.id_associado)
    if not associado:
        raise HTTPException(status_code=404, detail="Associado não encontrado")
    return crud.create_pagamento(db, data)


@router.put("/{id_pagamento}", response_model=schemas.PagamentoOut)
def update_pagamento(
    id_pagamento: int, data: schemas.PagamentoUpdate, db: Session = Depends(get_db)
):
    pagamento = crud.get_pagamento(db, id_pagamento)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    if data.id_administrador is not None:
        admin = crud.get_administrador(db, data.id_administrador)
        if not admin:
            raise HTTPException(status_code=404, detail="Administrador não encontrado")
    return crud.update_pagamento(db, pagamento, data)


@router.delete("/{id_pagamento}", status_code=204)
def delete_pagamento(id_pagamento: int, db: Session = Depends(get_db)):
    pagamento = crud.get_pagamento(db, id_pagamento)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    crud.delete_pagamento(db, pagamento)
