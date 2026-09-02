from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    dni: Mapped[str] = mapped_column(String(8), nullable=False, unique=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[str | None] = mapped_column(String(100))
    celular: Mapped[str | None] = mapped_column(String(9))
    correo: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    creado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="SET NULL")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modificado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="SET NULL")
    )
    modificado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


Index("uq_usuario_correo_lower", func.lower(Usuario.correo), unique=True)


class UsuarioPerfil(db.Model):
    __tablename__ = "usuario_perfil"

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"), primary_key=True
    )
    id_perfil: Mapped[int] = mapped_column(
        ForeignKey("perfil.id_perfil"), primary_key=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    asignado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="SET NULL")
    )
    asignado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modificado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="SET NULL")
    )
    modificado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
