from app.extensions import db
from app.models import OpcionMenu


def payload(codigo, nombre, **extra):
    return {
        "codigo": codigo,
        "nombre": nombre,
        "ruta": extra.get("ruta"),
        "descripcion": extra.get("descripcion"),
        "icono": extra.get("icono"),
        "id_padre": extra.get("id_padre"),
        "orden": extra.get("orden", 1),
    }


def test_crear_raiz_y_subopcion(client):
    raiz = client.post(
        "/api/opciones-menu", json=payload("seguridad", "Seguridad")
    )
    assert raiz.status_code == 201
    id_raiz = raiz.get_json()["id_opcion_menu"]
    hija = client.post(
        "/api/opciones-menu",
        json=payload(
            "usuarios", "Usuarios", ruta="/seguridad/usuarios", id_padre=id_raiz
        ),
    )
    assert hija.status_code == 201
    assert hija.get_json()["id_padre"] == id_raiz


def test_rechazar_codigo_y_ruta_duplicados(client):
    client.post(
        "/api/opciones-menu",
        json=payload("usuarios", "Usuarios", ruta="/seguridad/usuarios"),
    )
    respuesta = client.post(
        "/api/opciones-menu",
        json=payload("usuarios", "Otro", ruta="/seguridad/usuarios"),
    )
    assert respuesta.status_code == 422
    assert "codigo" in respuesta.get_json()["details"]
    assert "ruta" in respuesta.get_json()["details"]


def test_rechazar_ciclo_al_editar(client):
    raiz = client.post(
        "/api/opciones-menu", json=payload("seguridad", "Seguridad")
    ).get_json()
    hija = client.post(
        "/api/opciones-menu",
        json=payload("usuarios", "Usuarios", id_padre=raiz["id_opcion_menu"]),
    ).get_json()
    respuesta = client.put(
        f"/api/opciones-menu/{raiz['id_opcion_menu']}",
        json=payload("seguridad", "Seguridad", id_padre=hija["id_opcion_menu"]),
    )
    assert respuesta.status_code == 422
    assert "id_padre" in respuesta.get_json()["details"]


def test_arbol_y_cambio_de_estado(client):
    raiz = client.post(
        "/api/opciones-menu", json=payload("seguridad", "Seguridad")
    ).get_json()
    client.post(
        "/api/opciones-menu",
        json=payload("perfiles", "Perfiles", id_padre=raiz["id_opcion_menu"]),
    )
    arbol = client.get("/api/opciones-menu/arbol").get_json()["items"]
    assert len(arbol) == 1
    assert len(arbol[0]["hijos"]) == 1
    respuesta = client.patch(
        f"/api/opciones-menu/{raiz['id_opcion_menu']}/estado",
        json={"activo": False},
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["activo"] is False
