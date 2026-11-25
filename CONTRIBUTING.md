# Colaborar en Little Paws Net

La base del panel está en `entrega-panel`. Para la próxima entrega, el equipo revisará esa base en un PR hacia `main`. Después, crear ramas `feature/<tema>` para mejoras y `fix/<tema>` para correcciones desde la base acordada. Cada integrante revisa y registra su propio trabajo.

Usar mensajes como `feat(movil): consultar el estado de adopción`, `fix(panel): manejar un recurso inexistente` o `docs: actualizar las instrucciones de instalación`. Un PR debe enlazar su issue, explicar el resultado y dejar instrucciones de prueba. Revisar los cambios y las pruebas antes de integrar. Tras la integración, actualizar el registro de cambios y crear el tag sobre el commit que corresponde a la versión.

## Cambios del panel

Trabajar en `backend-panel/`. Mantener modelos, migraciones, servicios de dominio, permisos y API coherentes. Ocultar botones no sustituye la autorización del servidor. Las reglas de seguridad requieren pruebas de operación permitida y denegada.

Las pruebas usan MySQL **aislado**, nunca Railway. Configurar `LPN_TEST_MYSQL_HOST=127.0.0.1`, un puerto distinto de `MYSQL_PORT`, usuario y contraseña en variables locales `LPN_TEST_MYSQL_PORT`, `LPN_TEST_MYSQL_USER`, `LPN_TEST_MYSQL_PASSWORD`; además una `DJANGO_SECRET_KEY` local de prueba. El usuario de pruebas debe poder crear y destruir la base sintética. Después, desde `backend-panel`:

```powershell
python manage.py check --settings=config.settings_test_mysql
python manage.py makemigrations --check --dry-run --settings=config.settings_test_mysql
python manage.py test seguridad accounts.tests config.tests --settings=config.settings_test_mysql --noinput
```

El workflow `.github/workflows/panel.yml` reproduce estas comprobaciones en Linux con MySQL 8.4. No usa secretos de producción.

## Diseño

Las fuentes visuales viven en `frontend/panel-design`; el resultado real se sirve desde `backend-panel/seguridad/static`. La demo de `demos/` es independiente y ficticia. Mantener ambos al corregir estilos compartidos; no cargar archivos de la demo como autenticación real. Conservar licencias de fuentes e iconos.

## App móvil

Trabajar en `frontend/mobile/`. Ejecutar `flutter analyze` y `flutter test test/widget_test.dart`. Los ensayos que crean o resuelven solicitudes deben usar la base de pruebas local indicada en la [guía de la app](frontend/mobile/README.md).

## Datos y despliegue

No incluir ningún `.env`, contraseña, token, respaldo SQL ni datos personales. No hay excepciones para bases de evaluación. Borrar una credencial de Git no la revoca: rotarla y comprobar servicios dependientes. No reescribir la historia ni usar force push sin coordinación explícita.

No cambiar `backend/`, sus migraciones, el Dockerfile raíz o las bases anteriores como parte de una corrección del panel. La consolidación de ambas versiones requiere un plan de migración propio.

Ver [actualización del equipo](docs/entrega/actualizar-equipo.md) y [trazabilidad de Semana 15](docs/entrega/semana-15-evolucion.md).
