import re

from flask import Blueprint, jsonify, request

from ..errors import error_response
from ..extensions import db
from ..models import Perfil

bp = Blueprint("perfiles", __name__)
CODIGO_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def validar_payload(payload, parcial=False):
    errors = {}
    codigo = payload.get("codigo")
    nombre = payload.get("nombre")

    if not parcial or codigo is not None:
        codigo = (codigo or "").strip().lower()
        if not CODIGO_RE.fullmatch(codigo):
            errors["codigo"] = [
                "Use minúsculas, números y guion bajo; empiece con una letra."
            ]

    if not parcial or nombre is not None:
        nombre = (nombre or "").strip()
        if not nombre:
            errors["nombre"] = ["El nombre es obligatorio."]
        elif len(nombre) > 100:
            errors["nombre"] = ["El nombre admite como máximo 100 caracteres."]

    descripcion = payload.get("descripcion")
    if descripcion is not None and len(descripcion.strip()) > 250:
        errors["descripcion"] = [
            "La descripción admite como máximo 250 caracteres."
        ]

    return errors


@bp.get("")
def listar_perfiles():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    incluir_inactivos = request.args.get("incluir_inactivos") == "true"

    query = db.select(Perfil).order_by(Perfil.nombre)
    if not incluir_inactivos:
        query = query.where(Perfil.activo.is_(True))

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "items": [perfil.to_dict() for perfil in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    )


@bp.post("")
def crear_perfil():
    payload = request.get_json(silent=True) or {}
    errors = validar_payload(payload)
    if errors:
        return error_response(
            "validation_error", "Revise los datos enviados.", 422, errors
        )

    codigo = payload["codigo"].strip().lower()
    existente = db.session.scalar(db.select(Perfil).where(Perfil.codigo == codigo))
    if existente:
        return error_response(
            "conflict",
            "Ya existe un perfil con ese código.",
            409,
            {"codigo": ["El código debe ser único."]},
        )

    perfil = Perfil(
        codigo=codigo,
        nombre=payload["nombre"].strip(),
        descripcion=(payload.get("descripcion") or "").strip() or None,
    )
    db.session.add(perfil)
    db.session.commit()
    return jsonify(perfil.to_dict()), 201


@bp.put("/<int:id_perfil>")
def actualizar_perfil(id_perfil):
    perfil = db.get_or_404(Perfil, id_perfil)
    payload = request.get_json(silent=True) or {}
    errors = validar_payload(payload)
    if errors:
        return error_response(
            "validation_error", "Revise los datos enviados.", 422, errors
        )

    codigo = payload["codigo"].strip().lower()
    duplicado = db.session.scalar(
        db.select(Perfil).where(
            Perfil.codigo == codigo,
            Perfil.id_perfil != id_perfil,
        )
    )
    if duplicado:
        return error_response(
            "conflict",
            "Ya existe un perfil con ese código.",
            409,
            {"codigo": ["El código debe ser único."]},
        )

    perfil.codigo = codigo
    perfil.nombre = payload["nombre"].strip()
    perfil.descripcion = (payload.get("descripcion") or "").strip() or None
    db.session.commit()
    return jsonify(perfil.to_dict())


@bp.patch("/<int:id_perfil>/estado")
def cambiar_estado(id_perfil):
    perfil = db.get_or_404(Perfil, id_perfil)
    payload = request.get_json(silent=True) or {}
    activo = payload.get("activo")
    if not isinstance(activo, bool):
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            {"activo": ["Debe enviar true o false."]},
        )

    perfil.activo = activo
    db.session.commit()
    return jsonify(perfil.to_dict())

