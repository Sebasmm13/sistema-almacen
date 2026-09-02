from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    id_usuario: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="SET NULL")
    )
    id_perfil: Mapped[int | None] = mapped_column(
        ForeignKey("perfil.id_perfil", ondelete="SET NULL")
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    entidad: Mapped[str] = mapped_column(String(100), nullable=False)
    id_registro: Mapped[str | None] = mapped_column(String(100))
    detalle: Mapped[dict | None] = mapped_column(JSON)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String)

