# Colaborar en Little Paws Net

La integración actual se revisa en el PR #24, desde `feature/presentacion-integrada` hacia `main`. Después de integrarla, crear ramas `feature/<tema>` para mejoras y `fix/<tema>` para correcciones desde `main` actualizado. Cada integrante revisa y registra su propio trabajo. Conservar los commits individuales al integrar esta entrega.

Usar mensajes como `feat(movil): consultar el estado de adopción`, `fix(panel): manejar un recurso inexistente` o `docs: actualizar las instrucciones de instalación`. Un PR debe enlazar su issue, explicar el resultado y dejar instrucciones de prueba. Revisar los cambios y las pruebas antes de integrar. Tras la integración, actualizar el registro de cambios y crear el tag sobre el commit que corresponde a la versión.

## Cambios del panel

Trabajar en `backend-panel/`. Mantener modelos, migraciones, servicios de dominio, permisos y API coherentes. Ocultar botones no sustituye la autorización del servidor. Las reglas de seguridad requieren pruebas de operación permitida y denegada.

Las pruebas usan MySQL **aislado**, nunca Railway. Configurar `LPN_TEST_MYSQL_HOST=127.0.0.1`, un puerto distinto de `MYSQL_PORT`, usuario y contraseña en variables locales `LPN_TEST_MYSQL_PORT`, `LPN_TEST_MYSQL_USER`, `LPN_TEST_MYSQL_PASSWORD`; además una `DJANGO_SECRET_KEY` local de prueba. El usuario de pruebas debe poder crear y destruir la base sintética. Después, desde `backend-panel`:

```powershell
python manage.py check --settings=config.settings_test_mysql
python manage.py makemigrations --check --dry-run --settings=config.settings_test_mysql
python manage.py test --settings=config.settings_test_mysql --noinput
```

El workflow `.github/workflows/panel.yml` reproduce estas comprobaciones en Linux con MySQL 8.4. No usa secretos de producción.

## Diseño

El panel utiliza `backend-panel/seguridad/templates` y `backend-panel/seguridad/static`; la app tiene sus componentes y recursos en `frontend/mobile`. Revisar la interfaz realmente conectada al backend, no una demo visual en memoria. Conservar las licencias de fuentes e iconos y los diagramas originales de `DIAGRAMAS/`.

## App móvil

Trabajar en `frontend/mobile/`. Ejecutar `flutter analyze` y `flutter test --no-pub`. Los ensayos que crean o resuelven solicitudes deben usar la base de pruebas local indicada en la [guía de la app](frontend/mobile/README.md).

## Datos y despliegue

No incluir ningún `.env`, contraseña, token, respaldo SQL ni datos personales. No hay excepciones para bases de evaluación. Borrar una credencial de Git no la revoca: rotarla y comprobar servicios dependientes. No reescribir la historia ni usar force push sin coordinación explícita.

No cambiar `backend/`, sus migraciones, el Dockerfile raíz o las bases anteriores como parte de una corrección del panel. La consolidación de ambas versiones requiere un plan de migración propio.

Ver [actualización del equipo](docs/entrega/actualizar-equipo.md) y [trazabilidad de Semana 15](docs/entrega/semana-15-evolucion.md).
