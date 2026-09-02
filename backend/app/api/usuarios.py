import re

from argon2 import PasswordHasher
from flask import Blueprint, jsonify, request

from ..errors import error_response
from ..extensions import db
from ..models import Perfil, Usuario, UsuarioPerfil


bp = Blueprint("usuarios", __name__)
password_hasher = PasswordHasher()
CORREO_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def serializar_usuario(usuario):
    perfiles = db.session.execute(
        db.select(Perfil.id_perfil, Perfil.codigo, Perfil.nombre)
        .join(
            UsuarioPerfil,
            UsuarioPerfil.id_perfil == Perfil.id_perfil,
        )
        .where(
            UsuarioPerfil.id_usuario == usuario.id_usuario,
            UsuarioPerfil.activo.is_(True),
        )
        .order_by(Perfil.nombre)
    ).all()

    return {
        "id_usuario": usuario.id_usuario,
        "dni": usuario.dni,
        "nombres": usuario.nombres,
        "apellido_paterno": usuario.apellido_paterno,
        "apellido_materno": usuario.apellido_materno,
        "celular": usuario.celular,
        "correo": usuario.correo,
        "activo": usuario.activo,
        "perfiles": [
            {
                "id_perfil": perfil.id_perfil,
                "codigo": perfil.codigo,
                "nombre": perfil.nombre,
            }
            for perfil in perfiles
        ],
        "creado_en": (
            usuario.creado_en.isoformat()
            if usuario.creado_en
            else None
        ),
    }


@bp.get("")
def listar_usuarios():
    incluir_inactivos = (
        request.args.get("incluir_inactivos") == "true"
    )

    consulta = db.select(Usuario).order_by(
        Usuario.apellido_paterno,
        Usuario.nombres,
    )

    if not incluir_inactivos:
        consulta = consulta.where(Usuario.activo.is_(True))

    usuarios = db.session.scalars(consulta).all()

    return jsonify({
        "items": [
            serializar_usuario(usuario)
            for usuario in usuarios
        ]
    })


@bp.post("")
def crear_usuario():
    payload = request.get_json(silent=True) or {}

    dni = (payload.get("dni") or "").strip()
    nombres = (payload.get("nombres") or "").strip()
    apellido_paterno = (
        payload.get("apellido_paterno") or ""
    ).strip()
    apellido_materno = (
        payload.get("apellido_materno") or ""
    ).strip() or None
    celular = (payload.get("celular") or "").strip() or None
    correo = (payload.get("correo") or "").strip().lower()
    password = payload.get("password") or ""
    ids_perfil = payload.get("perfiles")

    errors = {}

    if not re.fullmatch(r"\d{8}", dni):
        errors["dni"] = [
            "El DNI debe tener exactamente 8 dígitos."
        ]

    if not nombres:
        errors["nombres"] = ["Los nombres son obligatorios."]

    if not apellido_paterno:
        errors["apellido_paterno"] = [
            "El apellido paterno es obligatorio."
        ]

    if celular and not re.fullmatch(r"9\d{8}", celular):
        errors["celular"] = [
            "El celular debe tener 9 dígitos y empezar en 9."
        ]

    if not CORREO_RE.fullmatch(correo):
        errors["correo"] = ["Ingrese un correo válido."]

    if len(password) < 8:
        errors["password"] = [
            "La contraseña debe tener como mínimo 8 caracteres."
        ]

    if (
        not isinstance(ids_perfil, list)
        or not ids_perfil
        or any(type(item) is not int for item in ids_perfil)
    ):
        errors["perfiles"] = [
            "Seleccione al menos un perfil válido."
        ]
    else:
        ids_perfil = list(dict.fromkeys(ids_perfil))

    if errors:
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            errors,
        )

    usuario_dni = db.session.scalar(
        db.select(Usuario).where(Usuario.dni == dni)
    )

    usuario_correo = db.session.scalar(
        db.select(Usuario).where(
            db.func.lower(Usuario.correo) == correo
        )
    )

    if usuario_dni:
        errors["dni"] = [
            "Ya existe un usuario con ese DNI."
        ]

    if usuario_correo:
        errors["correo"] = [
            "Ya existe un usuario con ese correo."
        ]

    perfiles = db.session.scalars(
        db.select(Perfil).where(
            Perfil.id_perfil.in_(ids_perfil),
            Perfil.activo.is_(True),
        )
    ).all()

    if len(perfiles) != len(ids_perfil):
        errors["perfiles"] = [
            "Uno o más perfiles no existen o están inactivos."
        ]

    if errors:
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            errors,
        )

    usuario = Usuario(
        dni=dni,
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        celular=celular,
        correo=correo,
        password_hash=password_hasher.hash(password),
    )

    db.session.add(usuario)
    db.session.flush()

    for id_perfil in ids_perfil:
        db.session.add(
            UsuarioPerfil(
                id_usuario=usuario.id_usuario,
                id_perfil=id_perfil,
                activo=True,
            )
        )

    db.session.commit()

    return jsonify(serializar_usuario(usuario)), 201

@bp.put("/<int:id_usuario>")
def actualizar_usuario(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)
    payload = request.get_json(silent=True) or {}

    dni = (payload.get("dni") or "").strip()
    nombres = (payload.get("nombres") or "").strip()
    apellido_paterno = (
        payload.get("apellido_paterno") or ""
    ).strip()
    apellido_materno = (
        payload.get("apellido_materno") or ""
    ).strip() or None
    celular = (payload.get("celular") or "").strip() or None
    correo = (payload.get("correo") or "").strip().lower()
    password = payload.get("password") or ""
    ids_perfil = payload.get("perfiles")

    errors = {}

    if not re.fullmatch(r"\d{8}", dni):
        errors["dni"] = [
            "El DNI debe tener exactamente 8 dígitos."
        ]

    if not nombres:
        errors["nombres"] = [
            "Los nombres son obligatorios."
        ]

    if not apellido_paterno:
        errors["apellido_paterno"] = [
            "El apellido paterno es obligatorio."
        ]

    if celular and not re.fullmatch(r"9\d{8}", celular):
        errors["celular"] = [
            "El celular debe tener 9 dígitos y empezar en 9."
        ]

    if not CORREO_RE.fullmatch(correo):
        errors["correo"] = [
            "Ingrese un correo válido."
        ]

    # En la edición la contraseña puede quedar vacía.
    if password and len(password) < 8:
        errors["password"] = [
            "La contraseña debe tener como mínimo 8 caracteres."
        ]

    if (
        not isinstance(ids_perfil, list)
        or not ids_perfil
        or any(type(item) is not int for item in ids_perfil)
    ):
        errors["perfiles"] = [
            "Seleccione al menos un perfil válido."
        ]
    else:
        ids_perfil = list(dict.fromkeys(ids_perfil))

    if errors:
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            errors,
        )

    dni_duplicado = db.session.scalar(
        db.select(Usuario).where(
            Usuario.dni == dni,
            Usuario.id_usuario != id_usuario,
        )
    )

    correo_duplicado = db.session.scalar(
        db.select(Usuario).where(
            db.func.lower(Usuario.correo) == correo,
            Usuario.id_usuario != id_usuario,
        )
    )

    if dni_duplicado:
        errors["dni"] = [
            "Ya existe otro usuario con ese DNI."
        ]

    if correo_duplicado:
        errors["correo"] = [
            "Ya existe otro usuario con ese correo."
        ]

    perfiles = db.session.scalars(
        db.select(Perfil).where(
            Perfil.id_perfil.in_(ids_perfil),
            Perfil.activo.is_(True),
        )
    ).all()

    if len(perfiles) != len(ids_perfil):
        errors["perfiles"] = [
            "Uno o más perfiles no existen o están inactivos."
        ]

    if errors:
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            errors,
        )

    usuario.dni = dni
    usuario.nombres = nombres
    usuario.apellido_paterno = apellido_paterno
    usuario.apellido_materno = apellido_materno
    usuario.celular = celular
    usuario.correo = correo

    # Solo cambia la contraseña si se envía una nueva.
    if password:
        usuario.password_hash = password_hasher.hash(password)

    relaciones = db.session.scalars(
        db.select(UsuarioPerfil).where(
            UsuarioPerfil.id_usuario == id_usuario
        )
    ).all()

    relaciones_por_perfil = {
        relacion.id_perfil: relacion
        for relacion in relaciones
    }

    perfiles_seleccionados = set(ids_perfil)

    # Desactiva las relaciones que ya no estén seleccionadas.
    for relacion in relaciones:
        relacion.activo = (
            relacion.id_perfil in perfiles_seleccionados
        )

    # Crea las relaciones que todavía no existan.
    for id_perfil in perfiles_seleccionados:
        if id_perfil not in relaciones_por_perfil:
            db.session.add(
                UsuarioPerfil(
                    id_usuario=id_usuario,
                    id_perfil=id_perfil,
                    activo=True,
                )
            )

    db.session.commit()

    return jsonify(serializar_usuario(usuario))

@bp.patch("/<int:id_usuario>/estado")
def cambiar_estado_usuario(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)
    payload = request.get_json(silent=True) or {}

    activo = payload.get("activo")

    if not isinstance(activo, bool):
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            {
                "activo": [
                    "Debe enviar true o false."
                ]
            },
        )

    usuario.activo = activo
    db.session.commit()

    return jsonify(serializar_usuario(usuario))