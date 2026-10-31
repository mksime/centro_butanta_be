from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─── Administrador ──────────────────────────────────────────────────────────

class AdministradorBase(BaseModel):
    nome_administrador: str = Field(..., max_length=200)
    email: EmailStr = Field(..., max_length=200)
    cargo: str = Field(..., max_length=100)
    setor: str = Field(..., max_length=100)


class AdministradorCreate(AdministradorBase):
    senha: str = Field(..., min_length=6, max_length=128)


class AdministradorUpdate(BaseModel):
    nome_administrador: str | None = Field(None, max_length=200)
    email: EmailStr | None = Field(None, max_length=200)
    cargo: str | None = Field(None, max_length=100)
    setor: str | None = Field(None, max_length=100)


class AdministradorOut(AdministradorBase):
    model_config = ConfigDict(from_attributes=True)
    id_administrador: int


# ─── Moradia ────────────────────────────────────────────────────────────────

class MoradiaBase(BaseModel):
    rua: str = Field(..., max_length=200)
    numero: str = Field(..., max_length=20)
    bloco: str | None = Field(None, max_length=50)
    proprietario: str = Field(..., max_length=200)
    numero_residentes: int = 1


class MoradiaCreate(MoradiaBase):
    pass


class MoradiaUpdate(BaseModel):
    rua: str | None = Field(None, max_length=200)
    numero: str | None = Field(None, max_length=20)
    bloco: str | None = Field(None, max_length=50)
    proprietario: str | None = Field(None, max_length=200)
    numero_residentes: int | None = None


class MoradiaOut(MoradiaBase):
    model_config = ConfigDict(from_attributes=True)
    id_moradia: int


# ─── Associado ──────────────────────────────────────────────────────────────

class AssociadoBase(BaseModel):
    nome: str = Field(..., max_length=200)
    nome_social: str | None = Field(None, max_length=200)
    data_nascimento: date
    telefone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    num_carteira_associado: str | None = Field(None, max_length=50)
    documento: str | None = Field(None, max_length=20)
    tipo_associacao: str | None = Field(None, max_length=50)
    situacao_cadastro: str = "ativo"
    dth_ingresso: datetime | None = None
    dth_saida: datetime | None = None


class AssociadoCreate(AssociadoBase):
    id_moradia: int


class AssociadoUpdate(BaseModel):
    nome: str | None = Field(None, max_length=200)
    nome_social: str | None = Field(None, max_length=200)
    data_nascimento: date | None = None
    telefone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    num_carteira_associado: str | None = Field(None, max_length=50)
    documento: str | None = Field(None, max_length=20)
    tipo_associacao: str | None = Field(None, max_length=50)
    situacao_cadastro: str | None = None
    dth_ingresso: datetime | None = None
    dth_saida: datetime | None = None
    id_moradia: int | None = None


class AssociadoOut(AssociadoBase):
    model_config = ConfigDict(from_attributes=True)
    id_associado: int
    id_moradia: int


# ─── ComprovanteResidencia ──────────────────────────────────────────────────

class ComprovanteResidenciaBase(BaseModel):
    tipo_documento: Literal["agua", "luz", "outro"]
    caminho_arquivo: str = Field(..., max_length=500)
    status_aprovacao: str = "pendente"


class ComprovanteResidenciaCreate(ComprovanteResidenciaBase):
    id_associado: int


class ComprovanteResidenciaUpdate(BaseModel):
    tipo_documento: Literal["agua", "luz", "outro"] | None = None
    caminho_arquivo: str | None = Field(None, max_length=500)
    status_aprovacao: str | None = None
    id_administrador: int | None = None


class ComprovanteResidenciaOut(ComprovanteResidenciaBase):
    model_config = ConfigDict(from_attributes=True)
    id_comprovante: int
    id_associado: int
    id_administrador: int | None = None


# ─── Pagamento ──────────────────────────────────────────────────────────────

class PagamentoBase(BaseModel):
    valor: float = Field(..., gt=0)
    recorrente: bool = False
    atraso: bool = False
    nome_pagador: str = Field(..., max_length=200)
    modo_pagamento: str = Field(..., max_length=50)
    dth_pagamento: datetime
    taxa: float = 0.0
    parcial: bool = False


class PagamentoCreate(PagamentoBase):
    id_associado: int


class PagamentoUpdate(BaseModel):
    valor: float | None = Field(None, gt=0)
    recorrente: bool | None = None
    atraso: bool | None = None
    nome_pagador: str | None = Field(None, max_length=200)
    modo_pagamento: str | None = Field(None, max_length=50)
    dth_pagamento: datetime | None = None
    taxa: float | None = None
    parcial: bool | None = None
    id_administrador: int | None = None


class PagamentoOut(PagamentoBase):
    model_config = ConfigDict(from_attributes=True)
    id_pagamento: int
    id_associado: int
    id_administrador: int | None = None
