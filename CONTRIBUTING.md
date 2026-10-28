# Colaborar en Little Paws Net

La rama integrada de esta entrega es `entrega-panel`. Crear ramas de funcionalidad desde su última versión, sin prefijo obligatorio. No trabajar directamente en `main`, no publicar credenciales y no mezclar funcionalidades en un commit. Cada persona debe entender y registrar su propio trabajo.

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

## Datos y despliegue

No incluir ningún `.env`, contraseña, token, respaldo SQL ni datos personales. No hay excepciones para bases de evaluación. Borrar una credencial de Git no la revoca: rotarla y comprobar servicios dependientes. No reescribir la historia ni usar force push sin coordinación explícita.

No cambiar `backend/`, sus migraciones, el Dockerfile raíz o las bases anteriores como parte de una corrección del panel. La consolidación de ambas versiones requiere un plan de migración propio.

Abrir PR hacia `entrega-panel` con alcance, validación y limitaciones. Antes de integrar, verificar CI y revisar el diff. Ver [actualización del equipo](docs/entrega/actualizar-equipo.md).
