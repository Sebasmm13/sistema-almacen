from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class Permiso(db.Model):
    __tablename__ = "permiso"

    id_permiso: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(250))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class PerfilPermiso(db.Model):
    __tablename__ = "perfil_permiso"

    id_perfil: Mapped[int] = mapped_column(
        ForeignKey("perfil.id_perfil"), primary_key=True
    )
    id_permiso: Mapped[int] = mapped_column(
        ForeignKey("permiso.id_permiso"), primary_key=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

