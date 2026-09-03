import re

from flask import Blueprint, jsonify, request

from ..errors import error_response
from ..extensions import db
from ..models import OpcionMenu

bp = Blueprint("opciones_menu", __name__)
CODIGO_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def serializar_opcion(opcion):
    padre = db.session.get(OpcionMenu, opcion.id_padre) if opcion.id_padre else None
    return {
        "id_opcion_menu": opcion.id_opcion_menu,
        "codigo": opcion.codigo,
        "nombre": opcion.nombre,
        "ruta": opcion.ruta,
        "descripcion": opcion.descripcion,
        "icono": opcion.icono,
        "id_padre": opcion.id_padre,
        "nombre_padre": padre.nombre if padre else None,
        "orden": opcion.orden,
        "activo": opcion.activo,
    }


def normalizar_payload(payload):
    id_padre = payload.get("id_padre")
    return {
        "codigo": (payload.get("codigo") or "").strip().lower(),
        "nombre": (payload.get("nombre") or "").strip(),
        "ruta": (payload.get("ruta") or "").strip() or None,
        "descripcion": (payload.get("descripcion") or "").strip() or None,
        "icono": (payload.get("icono") or "").strip() or None,
        "id_padre": id_padre,
        "orden": payload.get("orden", 1),
    }


def validar_payload(datos):
    errors = {}
    if not CODIGO_RE.fullmatch(datos["codigo"]):
        errors["codigo"] = [
            "Use minúsculas, números y guion bajo; empiece con una letra."
        ]
    if not datos["nombre"]:
        errors["nombre"] = ["El nombre es obligatorio."]
    elif len(datos["nombre"]) > 100:
        errors["nombre"] = ["Admite como máximo 100 caracteres."]
    if datos["ruta"] and not datos["ruta"].startswith("/"):
        errors["ruta"] = ["La ruta debe empezar con /. "]
    if datos["ruta"] and len(datos["ruta"]) > 200:
        errors["ruta"] = ["Admite como máximo 200 caracteres."]
    if datos["descripcion"] and len(datos["descripcion"]) > 300:
        errors["descripcion"] = ["Admite como máximo 300 caracteres."]
    if datos["icono"] and len(datos["icono"]) > 80:
        errors["icono"] = ["Admite como máximo 80 caracteres."]
    if datos["id_padre"] is not None and type(datos["id_padre"]) is not int:
        errors["id_padre"] = ["Debe ser un identificador o null."]
    if type(datos["orden"]) is not int or not 1 <= datos["orden"] <= 32767:
        errors["orden"] = ["Debe ser un entero entre 1 y 32767."]
    return errors


def validar_relaciones(datos, id_actual=None):
    errors = {}
    duplicado_codigo = db.session.scalar(
        db.select(OpcionMenu).where(OpcionMenu.codigo == datos["codigo"])
    )
    if duplicado_codigo and duplicado_codigo.id_opcion_menu != id_actual:
        errors["codigo"] = ["Ya existe una opción con ese código."]

    if datos["ruta"]:
        duplicado_ruta = db.session.scalar(
            db.select(OpcionMenu).where(OpcionMenu.ruta == datos["ruta"])
        )
        if duplicado_ruta and duplicado_ruta.id_opcion_menu != id_actual:
            errors["ruta"] = ["Ya existe una opción con esa ruta."]

    id_padre = datos["id_padre"]
    if id_padre is None:
        return errors
    if id_actual is not None and id_padre == id_actual:
        errors["id_padre"] = ["Una opción no puede ser su propio padre."]
        return errors
    padre = db.session.get(OpcionMenu, id_padre)
    if padre is None:
        errors["id_padre"] = ["La opción padre no existe."]
        return errors

    visitados = set()
    ancestro = padre
    while ancestro:
        if ancestro.id_opcion_menu in visitados:
            errors["id_padre"] = ["La jerarquía contiene un ciclo."]
            break
        if id_actual is not None and ancestro.id_opcion_menu == id_actual:
            errors["id_padre"] = ["La opción padre generaría un ciclo."]
            break
        visitados.add(ancestro.id_opcion_menu)
        ancestro = (
            db.session.get(OpcionMenu, ancestro.id_padre)
            if ancestro.id_padre
            else None
        )
    return errors


@bp.get("")
def listar_opciones():
    incluir_inactivos = request.args.get("incluir_inactivos") == "true"
    consulta = db.select(OpcionMenu).order_by(
        OpcionMenu.id_padre.nullsfirst(), OpcionMenu.orden, OpcionMenu.nombre
    )
    if not incluir_inactivos:
        consulta = consulta.where(OpcionMenu.activo.is_(True))
    opciones = db.session.scalars(consulta).all()
    return jsonify({"items": [serializar_opcion(item) for item in opciones]})


@bp.post("")
def crear_opcion():
    datos = normalizar_payload(request.get_json(silent=True) or {})
    errors = validar_payload(datos)
    if not errors:
        errors.update(validar_relaciones(datos))
    if errors:
        return error_response(
            "validation_error", "Revise los datos enviados.", 422, errors
        )

    opcion = OpcionMenu(**datos)
    db.session.add(opcion)
    db.session.commit()
    return jsonify(serializar_opcion(opcion)), 201


@bp.put("/<int:id_opcion_menu>")
def actualizar_opcion(id_opcion_menu):
    opcion = db.get_or_404(OpcionMenu, id_opcion_menu)
    datos = normalizar_payload(request.get_json(silent=True) or {})
    errors = validar_payload(datos)
    if not errors:
        errors.update(validar_relaciones(datos, id_opcion_menu))
    if errors:
        return error_response(
            "validation_error", "Revise los datos enviados.", 422, errors
        )

    for campo, valor in datos.items():
        setattr(opcion, campo, valor)
    db.session.commit()
    return jsonify(serializar_opcion(opcion))


@bp.patch("/<int:id_opcion_menu>/estado")
def cambiar_estado(id_opcion_menu):
    opcion = db.get_or_404(OpcionMenu, id_opcion_menu)
    payload = request.get_json(silent=True) or {}
    activo = payload.get("activo")
    if not isinstance(activo, bool):
        return error_response(
            "validation_error",
            "Revise los datos enviados.",
            422,
            {"activo": ["Debe enviar true o false."]},
        )
    opcion.activo = activo
    db.session.commit()
    return jsonify(serializar_opcion(opcion))


@bp.get("/arbol")
def obtener_arbol():
    opciones = db.session.scalars(
        db.select(OpcionMenu)
        .where(OpcionMenu.activo.is_(True))
        .order_by(OpcionMenu.orden, OpcionMenu.nombre)
    ).all()
    nodos = {
        item.id_opcion_menu: {**serializar_opcion(item), "hijos": []}
        for item in opciones
    }
    raices = []
    for item in opciones:
        nodo = nodos[item.id_opcion_menu]
        if item.id_padre in nodos:
            nodos[item.id_padre]["hijos"].append(nodo)
        else:
            raices.append(nodo)
    return jsonify({"items": raices})
