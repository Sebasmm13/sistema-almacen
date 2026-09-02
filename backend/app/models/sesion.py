import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class Sesion(db.Model):
    __tablename__ = "sesion"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_usuario", "id_perfil"],
            ["usuario_perfil.id_usuario", "usuario_perfil.id_perfil"],
        ),
    )

    id_sesion: Mapped[uuid.UUID] = mapped_column(
        db.Uuid, primary_key=True, default=uuid.uuid4
    )
    jti: Mapped[uuid.UUID] = mapped_column(db.Uuid, nullable=False, unique=True)
    id_usuario: Mapped[int] = mapped_column(ID_TYPE, nullable=False)
    id_perfil: Mapped[int] = mapped_column(ID_TYPE, nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revocada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String)

