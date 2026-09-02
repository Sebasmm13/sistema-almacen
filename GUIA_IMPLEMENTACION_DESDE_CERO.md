# Guía de implementación desde cero

## Resultado que deben buscar primero

El primer hito no es “tener toda la base de datos”. El hito correcto es poder
abrir React, crear un perfil, enviarlo a Flask, guardarlo en PostgreSQL y verlo
de nuevo en la lista. Ese corte de extremo a extremo cierra RF-01 y comprueba
que la arquitectura funciona.

No empiecen todavía con productos, entradas o salidas. El orden es:

1. Preparación de Trello y GitHub.
2. Entorno local y estructura del repositorio.
3. Esquema de seguridad y migraciones.
4. RF-01 Perfiles de extremo a extremo.
5. RF-02 Usuarios y asignación de varios perfiles.
6. RF-03 Opciones de menú jerárquicas.
7. Login, selección de perfil, JWT, permisos y menú dinámico.
8. Recién después, núcleo de inventario.

## 1. Preparar Trello antes de programar

Cree un tablero llamado `Sistema de Almacén - Programación III` y compártalo
con todos los integrantes y con el docente. Use estas listas, en este orden:

1. `00 Información`
2. `Product Backlog`
3. `Sprint / Por hacer`
4. `En proceso`
5. `Bloqueado`
6. `Revisión y pruebas`
7. `Terminado`

Cree inmediatamente estas tarjetas:

| ID | Tarjeta | Lista inicial | Prioridad |
|---|---|---|---|
| ORG-01 | Configurar repositorio, ramas y reglas | Sprint / Por hacer | Alta |
| DB-01 | Corregir y migrar el esquema de seguridad | Sprint / Por hacer | Alta |
| RF-01 | Gestionar perfiles | Sprint / Por hacer | Alta |
| RF-02 | Gestionar usuarios y asignar perfiles | Product Backlog | Alta |
| RF-03 | Gestionar opciones de menú jerárquicas | Product Backlog | Alta |
| RF-04 | Asignar menús y permisos a perfiles | Product Backlog | Alta |
| RF-05 | Implementar login y selección de perfil | Product Backlog | Alta |
| RF-06 | Construir menú dinámico y rutas protegidas | Product Backlog | Alta |
| QA-01 | Probar seguridad desde React hasta PostgreSQL | Product Backlog | Alta |

Cada tarjeta debe contener objetivo, responsable, dependencias, criterios de
aceptación, checklist BD/backend/frontend/pruebas y enlace a la rama o pull
request. Solo se mueve a Terminado cuando está integrada, probada y demostrable.

## 2. Crear GitHub y las ramas

En PowerShell, ubíquese en la carpeta donde guardará el proyecto:

```powershell
mkdir sistema-almacen
cd sistema-almacen
git init -b main
git add .
git commit -m "chore: crear estructura inicial del proyecto"
git branch develop
git switch develop
```

Luego cree el repositorio vacío en GitHub y conecte el remoto:

```powershell
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
git push -u origin develop
```

Regla de trabajo:

```text
main       = versión estable demostrable
develop    = integración de la iteración
feature/*  = una tarjeta o funcionalidad
```

Para RF-01:

```powershell
git switch develop
git pull
git switch -c feature/RF-01-perfiles
```

No trabajen directamente en `main`.

## 3. Instalar y comprobar herramientas

Necesitan Git, Python, Node.js, PostgreSQL y pgAdmin. Como el respaldo recibido
fue creado por PostgreSQL 18.4, usar PostgreSQL 18 evita incompatibilidades al
restaurarlo. Sin embargo, para este proyecto conviene crear una base nueva y no
seguir usando el respaldo anterior porque contiene contraseñas visibles, tres
perfiles y permisos incorrectos.

Compruebe en PowerShell:

```powershell
git --version
python --version
node --version
npm --version
psql --version
```

Si `psql` no aparece, agregue la carpeta `bin` de PostgreSQL al PATH o ejecute
los scripts desde Query Tool de pgAdmin.

## 4. Crear la base de datos

En pgAdmin:

1. Abra `Servers > PostgreSQL`.
2. Clic derecho en `Databases > Create > Database`.
3. Nombre: `gestion_almacen_dev`.
4. Owner: su usuario local de PostgreSQL.
5. Guarde.

Hay dos caminos. El recomendado para el curso es que los modelos de SQLAlchemy
y Flask-Migrate sean la fuente versionada. Los archivos SQL corregidos sirven
para comparar el resultado o levantar una base de referencia.

### Camino recomendado: migraciones

Copie el starter, abra PowerShell en `backend` y ejecute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

Edite `backend/.env` y cambie usuario, contraseña y nombre de la base en
`DATABASE_URL`. No suba `.env` a GitHub.

Después:

```powershell
$env:FLASK_APP="run.py"
flask db init
flask db migrate -m "crear modulo de seguridad"
flask db upgrade
```

Revise la migración antes de confirmarla. Debe incluir las nueve tablas de
seguridad. Compare sus nombres, claves y tipos con
`Diccionario_datos_corregido.xlsx` y con `001_esquema_seguridad_postgresql.sql`.

La prevención de ciclos de `opcion_menu` debe validarse en el servicio Flask;
como defensa adicional puede copiar la función y el trigger del SQL corregido a
la migración generada.

### Camino de referencia: scripts SQL

En Query Tool de pgAdmin ejecute, en este orden:

1. `001_esquema_seguridad_postgresql.sql`
2. `002_datos_base_seguridad.sql`

No ejecute a la vez el script de creación y una migración que cree las mismas
tablas, porque obtendrá errores “relation already exists”. El equipo debe elegir
una sola fuente de creación y documentarla.

## 5. Levantar Flask

Con el entorno virtual activo:

```powershell
cd backend
$env:FLASK_APP="run.py"
flask run --debug
```

Compruebe en el navegador:

```text
http://localhost:5000/api/health
```

Debe responder:

```json
{"status":"ok"}
```

Pruebe el CRUD con los tests:

```powershell
pytest -q
```

No avance si fallan las pruebas o si Flask no conecta con PostgreSQL.

## 6. Levantar React

Abra otra ventana de PowerShell:

```powershell
cd frontend
npm install
Copy-Item ..\.env.example .env
npm run dev
```

Abra:

```text
http://localhost:5173
```

Pruebe crear, editar, desactivar y reactivar un perfil. Luego confirme en pgAdmin:

```sql
SELECT id_perfil, codigo, nombre, activo
FROM perfil
ORDER BY id_perfil;
```

Si React muestra “No se pudo conectar con Flask”, compruebe `VITE_API_URL`, el
puerto 5000 y `FRONTEND_URL` en el backend.

## 7. Criterios de aceptación de RF-01

RF-01 solo pasa a Revisión y pruebas cuando:

- Lista perfiles activos e inactivos.
- Crea un perfil con código y nombre obligatorios.
- Rechaza códigos repetidos.
- Edita nombre y descripción.
- Desactiva lógicamente; no elimina la fila.
- Muestra errores del backend dentro de React.
- Los tests cubren creación, duplicado, validación, edición y desactivación.
- La evidencia muestra React, respuesta de Flask y fila PostgreSQL.

Antes de Terminado, cree el pull request de `feature/RF-01-perfiles` a `develop`,
asigne un revisor y adjunte el resultado de `pytest -q`.

## 8. RF-02: usuarios y varios perfiles

Implemente después de cerrar RF-01:

1. Modelo y endpoints de `usuario` y `usuario_perfil`.
2. DNI y celular como texto para conservar ceros iniciales.
3. Correo normalizado en minúsculas.
4. Contraseña procesada por Argon2 o bcrypt antes de guardar.
5. Formulario React con selección múltiple de perfiles.
6. Regla: un usuario activo no puede quedar sin perfil activo.
7. Asigne `administrador` y `gerente` al usuario gerente de prueba.

Nunca envíe `password_hash` en respuestas JSON.

## 9. RF-03: opciones de menú jerárquicas

Implemente:

1. CRUD de `opcion_menu`.
2. Selector de opción padre.
3. `id_padre = NULL` para opciones raíz.
4. `ruta = NULL` para agrupadores como Seguridad o Inventario.
5. Rutas React solo para pantallas, por ejemplo `/seguridad/perfiles`.
6. No cree opciones “Editar perfil” o “Agregar producto”; son botones dentro de
   una pantalla y se controlan mediante permisos.
7. Antes de guardar, recorra los ancestros y rechace cualquier ciclo.

## 10. Autenticación, perfil activo y autorización

Cuando RF-01, RF-02 y RF-03 funcionen:

1. `POST /api/auth/login` valida correo, contraseña y estado.
2. Devuelve únicamente los perfiles activos del usuario.
3. Si existe un perfil, lo selecciona; si existen varios, React muestra la
   pantalla de selección.
4. `POST /api/auth/select-profile` verifica nuevamente la relación activa.
5. Flask crea una sesión y emite JWT con `id_usuario`, `id_perfil`, `jti` e
   identificador de sesión.
6. `GET /api/auth/menu` arma el árbol desde `perfil_opcion_menu`.
7. Cada endpoint usa un decorador de permiso; ocultar botones en React no es
   autorización.
8. Al cambiar de perfil, revoque la sesión anterior y emita nuevos tokens.
9. Logout revoca la sesión.

Ejemplo conceptual del decorador:

```python
@jwt_required()
@permission_required("perfil.editar")
def actualizar_perfil(id_perfil):
    ...
```

El menú visible y el permiso de acción son controles distintos.

## 11. Orden del módulo de almacén

Solo después de demostrar la seguridad completa:

1. Categorías, unidades, productos, almacenes y ubicaciones.
2. Movimientos y detalle de movimientos.
3. Entradas y salidas dentro de transacciones.
4. Stock calculado o actualizado únicamente por movimientos.
5. Kardex por producto.
6. Solicitudes, conteos físicos y ajustes autorizados.
7. Reportes de stock bajo y movimientos.

Nunca agregue un formulario “Editar stock”. Una diferencia se corrige mediante
un ajuste justificado y autorizado; un movimiento confirmado no se edita ni se
elimina, se revierte con otro movimiento.

## 12. Qué debe cambiar en el informe actual

El informe está bien planteado como arquitectura objetivo, pero debe aclarar:

- El respaldo adjunto ya es PostgreSQL 18.4; no es un script SQL Server.
- El respaldo todavía usa tablas y columnas CamelCase entre comillas.
- El respaldo solo tiene cinco tablas y no incluye permisos, sesiones,
  auditoría ni tablas del almacén.
- Los datos anteriores tenían tres perfiles, contraseñas visibles y todas las
  opciones asignadas al técnico.
- La base corregida y el software deben utilizar los nombres snake_case del
  diccionario actualizado.
- Debe indicarse la empresa o escenario real y validarse cómo ocurren entradas,
  salidas y solicitudes; el texto actual aún describe un almacén genérico.

## 13. Definición de Terminado

Una tarjeta está terminada solo si:

- Cumple sus criterios de aceptación.
- Funciona integrada desde React hasta PostgreSQL.
- Tiene validaciones en frontend y backend.
- Respeta eliminación lógica y permisos.
- Incluye pruebas del camino correcto y de errores.
- No contiene secretos ni datos personales reales.
- Fue revisada mediante pull request.
- Cuenta con captura o video y resultado de pruebas en Trello.

