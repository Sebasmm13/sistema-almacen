# Sistema web de gestión de almacén

Starter académico para la arquitectura acordada:

- Frontend: React + TypeScript + Vite.
- Backend: Flask con application factory y blueprints.
- Base de datos: PostgreSQL.
- ORM y migraciones: Flask-SQLAlchemy + Flask-Migrate.

Este corte implementa el primer flujo vertical de **RF-01 Gestionar perfiles**:
base de datos, API REST, validaciones, pantalla React y pruebas del backend.

> Importante: durante esta primera rama los endpoints de perfiles todavía no
> tienen JWT. No se considera terminado el módulo de seguridad hasta integrar
> RF-02, RF-03, autenticación, selección de perfil y permisos en Flask.

La secuencia completa está en `GUIA_IMPLEMENTACION_DESDE_CERO.md`.

