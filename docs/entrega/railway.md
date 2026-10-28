# Railway · conexión y plan de actualización

## Destinos comprobados

Proyecto: `little-paws-net-demo`, ID `fd2429ee-8ee5-454d-9bdc-91c595d80547`.

- MySQL: `d929907f-99e2-433f-80c1-640ebbae9930`.
- API: `580ffc4f-afaa-441c-a0c8-d90ddd15a81f`; `https://little-paws-api-production.up.railway.app/`.
- La interfaz de Railway mostraba ambos servicios Online y un despliegue anterior de la API desde GitHub.
- Conexión SQL verificada **solo a `little_paws_net_eval`**, usando la configuración existente de la copia local cloud, sin copiar ni publicar sus claves. Se consultaron metadatos en una transacción de solo lectura. No se afirma haber inspeccionado todos los datos de la base de producción.

El `backend-panel/.env` de este repositorio sigue apuntando a MySQL local. No se sustituyó silenciosamente por la base de Railway.

## Por qué no ejecutar migrate directamente

La comparación de esquemas figura en `output/auditoria-entrega/comparacion-esquemas.json`. Faltan 25 tablas y 22 columnas respecto a la versión local; entre ellas `Recurso`, auditoría, asignaciones, responsabilidad principal, transferencias, captcha y límites. `Rol` necesita `activo`, `delegable` y `sistema`; `Permiso` necesita relación al recurso, acción, alcance y estado; las membresías necesitan revocación. También hay diferencias anteriores al módulo de seguridad, por ejemplo claves de detalle de pedido y campos de fondos. El nombre de la aplicación de adopciones y el historial de migraciones difieren.

Una migración de seguridad no resuelve automáticamente todas esas diferencias. Tampoco es correcto marcar migraciones como aplicadas para evitar errores de tablas existentes.

## Alternativa aprobada para la entrega

Preparar un esquema nuevo y separado para **esta versión completa** dentro del destino de Railway acordado, conservando la demo anterior. Usar un usuario SQL exclusivo de ese esquema y variables privadas del servicio; después aplicar su historial de migraciones desde cero. No recrear cuentas activas a partir de contraseñas demo ni sobrescribir la clave de cifrado de datos existentes.

El propietario aprobó preparar la base nueva y conservar la anterior, y autorizó Railway CLI. El destino preparado es `little_paws_panel_v2`, con un usuario exclusivo `lpn_panel_v2` limitado a ese esquema, en el servicio MySQL existente. La creación y migración se verifican en `output/auditoria-entrega/railway-nueva-base.json`; solo `migrated: true` confirma el proceso completo. No se crean servicios de cómputo adicionales ni se despliega el backend antiguo sobre el esquema nuevo.

**Resultado verificado:** creación y migraciones completas, 91 tablas, 13 roles activos, 20 recursos, 51 permisos y cero usuarios. `panel_railway.ps1 -Accion check` terminó sin incidencias. Las bases `little_paws_net_demo` y `little_paws_net_eval` conservaron sus 66 tablas cada una. No se cambió el servicio de la API anterior. El alta del propietario permanece pendiente de su contraseña privada.

La configuración privada queda en `backend-panel/.env.railway`, excluida de Git y de los paquetes; su ACL local limita lectura al propietario y SYSTEM. `MYSQL_SSL_MODE=REQUIRED` exige transporte cifrado en el acceso externo comprobado. Esto no configura por sí solo verificación de identidad con una CA propia. `LPN_ENV_FILE` selecciona explícitamente este archivo; el `.env` habitual sigue apuntando al MySQL local.

Desde la raíz del repositorio, para comprobar la conexión:

```powershell
.\backend\panel_railway.ps1 -Accion check
```

Para crear tu administrador con una contraseña solicitada de forma oculta:

```powershell
.\backend\panel_railway.ps1 -Accion iniciar_seguridad -Email TU_CORREO -Nombre "Tu nombre"
```

Para probar el panel real en tu computador usando la base nueva:

```powershell
.\backend\panel_railway.ps1 -Accion runserver
```

Abrir `http://127.0.0.1:8000/panel/login/`. El servidor escucha solo en loopback; no equivale a un despliegue público. Cada integrante necesita su configuración privada autorizada: no distribuir el archivo con contraseña en los ZIP.

Tras preparar el destino:

1. Guardar el esquema, host, puerto, usuario y contraseña en Secrets/variables de entorno, nunca en Git. Esta copia espera `MYSQL_DATABASE`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER` y `MYSQL_PASSWORD`. Mapear explícitamente los nombres de Railway (`MYSQLDATABASE`, `MYSQLHOST`, etc.) a los que consume Django.
2. Usar red privada entre servicios de Railway. Para herramientas locales, usar el acceso externo/túnel permitido por el proyecto; no confundir el host interno con el proxy TCP.
3. Para un futuro servicio nuevo de panel, seleccionar `backend-panel/` como directorio raíz y su Dockerfile; usar `DJANGO_SETTINGS_MODULE=config.settings_railway`. Instalar `requirements-railway.txt`; configurar `DJANGO_SECRET_KEY`, `LPN_DATA_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` y un volumen privado con `LPN_PRIVATE_ROOT` apuntando a él. Gunicorn y WhiteNoise sirven la aplicación y los recursos; el Dockerfile no ejecuta migraciones ni crea cuentas automáticamente. `collectstatic` se verificó localmente; la imagen necesita verificación Linux antes de desplegar. Los secretos nuevos no se reutilizan en el servicio anterior.
4. Revisar `showmigrations --plan`, aplicar `migrate` en el esquema nuevo y comprobar los conteos del catálogo. No usar una importación SQL como sustituto de las migraciones.
5. Inicializar al propietario con `python manage.py iniciar_seguridad --email TU_CORREO --nombre "Tu nombre"`; la contraseña se solicita oculta.
6. Probar login y RBAC real desde el dominio publicado antes de cambiar el enlace de entrega.

## Alternativa para conservar el backend cloud como fuente oficial

Crear una rama local de integración sobre esa copia, portar `seguridad` y adaptar imports/modelos (`adoptions`, no `adoption`). Generar migraciones **nuevas a partir de su historial**, ensayarlas sobre una copia restaurable y conservar PK/FK, titulares, responsables, asignaciones y datos cifrados. Verificar traducciones y API existentes. Solo después programar el cambio sobre la base elegida. Los parches de esta entrega no son directamente aplicables a esa copia distinta.

Referencias oficiales: [MySQL en Railway](https://docs.railway.com/databases/mysql), [proxy TCP](https://docs.railway.com/networking/tcp-proxy), [Django en Railway](https://docs.railway.com/guides/django). Las instrucciones de PostgreSQL del tutorial de Django no cambian el motor MySQL requerido por este proyecto.
