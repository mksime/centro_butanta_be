import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoDocumento(str, enum.Enum):
    AGUA = "agua"
    LUZ = "luz"
    OUTRO = "outro"


class Administrador(Base):
    __tablename__ = "administrador"

    id_administrador: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome_administrador: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    setor: Mapped[str] = mapped_column(String(100), nullable=False)

    comprovantes_aprovados: Mapped[list["ComprovanteResidencia"]] = relationship(
        back_populates="aprovador"
    )
    pagamentos_controlados: Mapped[list["Pagamento"]] = relationship(
        back_populates="controlador"
    )


class Moradia(Base):
    __tablename__ = "moradia"

    id_moradia: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rua: Mapped[str] = mapped_column(String(200), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    bloco: Mapped[str] = mapped_column(String(50), nullable=True)
    proprietario: Mapped[str] = mapped_column(String(200), nullable=False)
    numero_residentes: Mapped[int] = mapped_column(Integer, default=1)

    associados: Mapped[list["Associado"]] = relationship(back_populates="moradia")


class Associado(Base):
    __tablename__ = "associado"

    id_associado: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_social: Mapped[str] = mapped_column(String(200), nullable=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(200), nullable=True)
    num_carteira_associado: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    documento: Mapped[str] = mapped_column(String(20), nullable=True)
    tipo_associacao: Mapped[str] = mapped_column(String(50), nullable=True)
    situacao_cadastro: Mapped[str] = mapped_column(String(50), default="ativo")
    dth_ingresso: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    dth_saida: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    id_moradia: Mapped[int] = mapped_column(
        ForeignKey("moradia.id_moradia"), nullable=False
    )

    moradia: Mapped[Moradia] = relationship(back_populates="associados")
    comprovantes: Mapped[list["ComprovanteResidencia"]] = relationship(
        back_populates="associado"
    )
    pagamentos: Mapped[list["Pagamento"]] = relationship(back_populates="associado")


class ComprovanteResidencia(Base):
    __tablename__ = "comprovante_residencia"

    id_comprovante: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tipo_documento: Mapped[TipoDocumento] = mapped_column(
        Enum(TipoDocumento, name="tipo_documento"), nullable=False
    )
    caminho_arquivo: Mapped[str] = mapped_column(String(500), nullable=False)
    status_aprovacao: Mapped[str] = mapped_column(String(50), default="pendente")

    id_associado: Mapped[int] = mapped_column(
        ForeignKey("associado.id_associado"), nullable=False
    )
    id_administrador: Mapped[int | None] = mapped_column(
        ForeignKey("administrador.id_administrador"), nullable=True
    )

    associado: Mapped[Associado] = relationship(back_populates="comprovantes")
    aprovador: Mapped[Administrador | None] = relationship(
        back_populates="comprovantes_aprovados"
    )


class Pagamento(Base):
    __tablename__ = "pagamento"

    id_pagamento: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    recorrente: Mapped[bool] = mapped_column(Boolean, default=False)
    atraso: Mapped[bool] = mapped_column(Boolean, default=False)
    nome_pagador: Mapped[str] = mapped_column(String(200), nullable=False)
    modo_pagamento: Mapped[str] = mapped_column(String(50), nullable=False)
    dth_pagamento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    taxa: Mapped[float] = mapped_column(Float, default=0.0)
    parcial: Mapped[bool] = mapped_column(Boolean, default=False)

    id_associado: Mapped[int] = mapped_column(
        ForeignKey("associado.id_associado"), nullable=False
    )
    id_administrador: Mapped[int | None] = mapped_column(
        ForeignKey("administrador.id_administrador"), nullable=True
    )

    associado: Mapped[Associado] = relationship(back_populates="pagamentos")
    controlador: Mapped[Administrador | None] = relationship(
        back_populates="pagamentos_controlados"
    )
