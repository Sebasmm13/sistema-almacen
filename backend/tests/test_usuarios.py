from app.extensions import db
from app.models import Perfil, Usuario


def crear_perfiles():
    perfiles = [
        Perfil(codigo="gerente", nombre="Gerente"),
        Perfil(codigo="tecnico", nombre="Técnico"),
    ]

    db.session.add_all(perfiles)
    db.session.commit()

    return perfiles


def crear_payload(perfiles):
    return {
        "dni": "12345678",
        "nombres": "Usuario",
        "apellido_paterno": "Prueba",
        "apellido_materno": "Sistema",
        "celular": "987654321",
        "correo": "usuario@example.com",
        "password": "ClaveSegura2026",
        "perfiles": [
            perfil.id_perfil
            for perfil in perfiles
        ],
    }


def test_crear_usuario_con_varios_perfiles(client, app):
    with app.app_context():
        perfiles = crear_perfiles()
        payload = crear_payload(perfiles)

        respuesta = client.post(
            "/api/usuarios",
            json=payload,
        )

        assert respuesta.status_code == 201

        datos = respuesta.get_json()

        assert len(datos["perfiles"]) == 2
        assert "password" not in datos
        assert "password_hash" not in datos

        usuario = db.session.get(
            Usuario,
            datos["id_usuario"],
        )

        assert usuario.password_hash != "ClaveSegura2026"


def test_rechazar_usuario_duplicado(client, app):
    with app.app_context():
        perfiles = crear_perfiles()
        payload = crear_payload(perfiles)

        primera = client.post(
            "/api/usuarios",
            json=payload,
        )

        segunda = client.post(
            "/api/usuarios",
            json=payload,
        )

        assert primera.status_code == 201
        assert segunda.status_code == 422

        detalles = segunda.get_json()["details"]

        assert "dni" in detalles
        assert "correo" in detalles


def test_actualizar_usuario(client, app):
    with app.app_context():
        perfiles = crear_perfiles()
        payload = crear_payload(perfiles)

        creado = client.post(
            "/api/usuarios",
            json=payload,
        ).get_json()

        payload["nombres"] = "Usuario actualizado"
        payload["password"] = ""
        payload["perfiles"] = [
            perfiles[0].id_perfil
        ]

        respuesta = client.put(
            f"/api/usuarios/{creado['id_usuario']}",
            json=payload,
        )

        assert respuesta.status_code == 200

        datos = respuesta.get_json()

        assert datos["nombres"] == "Usuario actualizado"
        assert len(datos["perfiles"]) == 1


def test_desactivar_y_activar_usuario(client, app):
    with app.app_context():
        perfiles = crear_perfiles()
        payload = crear_payload(perfiles)

        creado = client.post(
            "/api/usuarios",
            json=payload,
        ).get_json()

        desactivado = client.patch(
            f"/api/usuarios/{creado['id_usuario']}/estado",
            json={"activo": False},
        )

        assert desactivado.status_code == 200
        assert desactivado.get_json()["activo"] is False

        activado = client.patch(
            f"/api/usuarios/{creado['id_usuario']}/estado",
            json={"activo": True},
        )

        assert activado.status_code == 200
        assert activado.get_json()["activo"] is True