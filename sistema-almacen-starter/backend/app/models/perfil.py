from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class Perfil(db.Model):
    __tablename__ = "perfil"

    id_perfil: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(250))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modificado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    def to_dict(self):
        return {
            "id_perfil": self.id_perfil,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "activo": self.activo,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "modificado_en": (
                self.modificado_en.isoformat() if self.modificado_en else None
            ),
        }

