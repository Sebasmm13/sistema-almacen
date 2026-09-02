from sqlalchemy import Boolean, ForeignKey, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class OpcionMenu(db.Model):
    __tablename__ = "opcion_menu"
    __table_args__ = (Index("ix_opcion_menu_padre_orden", "id_padre", "orden"),)

    id_opcion_menu: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    ruta: Mapped[str | None] = mapped_column(String(200), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(300))
    icono: Mapped[str | None] = mapped_column(String(80))
    id_padre: Mapped[int | None] = mapped_column(
        ForeignKey("opcion_menu.id_opcion_menu")
    )
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class PerfilOpcionMenu(db.Model):
    __tablename__ = "perfil_opcion_menu"

    id_perfil: Mapped[int] = mapped_column(
        ForeignKey("perfil.id_perfil"), primary_key=True
    )
    id_opcion_menu: Mapped[int] = mapped_column(
        ForeignKey("opcion_menu.id_opcion_menu"), primary_key=True
    )
    orden: Mapped[int | None] = mapped_column(SmallInteger)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

