from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


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
    cep: str | None = Field(None, max_length=10)
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, max_length=50)
    complemento: str | None = Field(None, max_length=200)
    proprietario: str = Field(..., max_length=200)
    numero_residentes: int = 1


class MoradiaCreate(MoradiaBase):
    pass


class MoradiaUpdate(BaseModel):
    rua: str | None = Field(None, max_length=200)
    numero: str | None = Field(None, max_length=20)
    cep: str | None = Field(None, max_length=10)
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, max_length=50)
    complemento: str | None = Field(None, max_length=200)
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
    id_administrador: int | None = None


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
    id_administrador: int | None = None


class AssociadoOut(AssociadoBase):
    data_ultimo_pagamento: date | None = None
    model_config = ConfigDict(from_attributes=True)
    id_associado: int
    id_moradia: int
    id_administrador: int


class MensalidadeUpdate(BaseModel):
    atraso: bool
    data_pagamento: date | None = None

    @model_validator(mode="after")
    def validar_data_pagamento(self):
        if not self.atraso and self.data_pagamento is None:
            raise ValueError("Informe a data do pagamento.")
        if self.atraso and self.data_pagamento is not None:
            raise ValueError("Não informe data de pagamento ao registrar atraso.")
        return self


class AssociadoComMoradiaCreate(BaseModel):
    moradia: MoradiaCreate | None = None
    associado: AssociadoBase | None = None

    rua: str | None = None
    numero: str | None = None
    cep: str | None = None
    cidade: str | None = None
    estado: str | None = None
    complemento: str | None = None
    proprietario: str | None = None
    numero_residentes: int | None = None

    nome: str | None = None
    nome_social: str | None = None
    data_nascimento: date | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    num_carteira_associado: str | None = None
    documento: str | None = None
    tipo_associacao: str | None = None
    situacao_cadastro: str | None = None
    dth_ingresso: datetime | None = None
    dth_saida: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, value):
        if not isinstance(value, dict):
            return value

        moradia = value.get("moradia")
        if moradia is None:
            moradia_fields = {
                key: value[key]
                for key in ("rua", "numero", "cep", "cidade", "estado", "complemento", "proprietario", "numero_residentes")
                if key in value and value[key] is not None
            }
            if moradia_fields:
                value = {**value, "moradia": moradia_fields}

        associado = value.get("associado")
        if associado is None:
            associado_fields = {
                key: value[key]
                for key in (
                    "nome",
                    "nome_social",
                    "data_nascimento",
                    "telefone",
                    "email",
                    "num_carteira_associado",
                    "documento",
                    "tipo_associacao",
                    "situacao_cadastro",
                    "dth_ingresso",
                    "dth_saida",
                    "id_administrador",
                )
                if key in value and value[key] is not None
            }
            if associado_fields:
                value = {**value, "associado": associado_fields}

        return value


class AssociadoComMoradiaUpdate(BaseModel):
    moradia: MoradiaUpdate | None = None
    associado: AssociadoUpdate | None = None

    rua: str | None = None
    numero: str | None = None
    cep: str | None = None
    cidade: str | None = None
    estado: str | None = None
    complemento: str | None = None
    proprietario: str | None = None
    numero_residentes: int | None = None

    nome: str | None = None
    nome_social: str | None = None
    data_nascimento: date | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    num_carteira_associado: str | None = None
    documento: str | None = None
    tipo_associacao: str | None = None
    situacao_cadastro: str | None = None
    dth_ingresso: datetime | None = None
    dth_saida: datetime | None = None
    id_moradia: int | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, value):
        if not isinstance(value, dict):
            return value

        moradia = value.get("moradia")
        if moradia is None:
            moradia_fields = {
                key: value[key]
                for key in (
                    "rua",
                    "numero",
                    "cep",
                    "cidade",
                    "estado",
                    "complemento",
                    "proprietario",
                    "numero_residentes",
                )
                if key in value and value[key] is not None
            }
            if moradia_fields:
                value = {**value, "moradia": moradia_fields}

        associado = value.get("associado")
        if associado is None:
            associado_fields = {
                key: value[key]
                for key in (
                    "nome",
                    "nome_social",
                    "data_nascimento",
                    "telefone",
                    "email",
                    "num_carteira_associado",
                    "documento",
                    "tipo_associacao",
                    "situacao_cadastro",
                    "dth_ingresso",
                    "dth_saida",
                    "id_moradia",
                    "id_administrador",
                )
                if key in value and value[key] is not None
            }
            if associado_fields:
                value = {**value, "associado": associado_fields}

        return value


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
    id_administrador: int | None = None


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
    id_administrador: int
