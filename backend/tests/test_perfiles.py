def test_crear_y_listar_perfil(client):
    response = client.post(
        "/api/perfiles",
        json={
            "codigo": "administrador",
            "nombre": "Administrador",
            "descripcion": "Administra la seguridad",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["activo"] is True

    response = client.get("/api/perfiles")
    assert response.status_code == 200
    assert response.get_json()["total"] == 1


def test_rechaza_codigo_duplicado(client):
    payload = {"codigo": "gerente", "nombre": "Gerente"}
    assert client.post("/api/perfiles", json=payload).status_code == 201

    response = client.post("/api/perfiles", json=payload)
    assert response.status_code == 409
    assert response.get_json()["error"] == "conflict"


def test_valida_datos(client):
    response = client.post(
        "/api/perfiles", json={"codigo": "Código Inválido", "nombre": ""}
    )
    assert response.status_code == 422
    assert "codigo" in response.get_json()["details"]
    assert "nombre" in response.get_json()["details"]


def test_actualiza_y_desactiva(client):
    created = client.post(
        "/api/perfiles", json={"codigo": "tecnico", "nombre": "Técnico"}
    ).get_json()
    profile_id = created["id_perfil"]

    response = client.put(
        f"/api/perfiles/{profile_id}",
        json={
            "codigo": "tecnico",
            "nombre": "Técnico de almacén",
            "descripcion": "Registra movimientos",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["nombre"] == "Técnico de almacén"

    response = client.patch(
        f"/api/perfiles/{profile_id}/estado", json={"activo": False}
    )
    assert response.status_code == 200
    assert response.get_json()["activo"] is False
    assert client.get("/api/perfiles").get_json()["total"] == 0

