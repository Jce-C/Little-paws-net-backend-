# Panel publicado en Railway

## Servicio vigente

- Entrada: https://little-paws-panel-production.up.railway.app/panel/login/
- Estado de proceso: https://little-paws-panel-production.up.railway.app/api/health/
- Proyecto: `fd2429ee-8ee5-454d-9bdc-91c595d80547`.
- Servicio panel: `830362dc-fcb3-40c6-9850-c9dac01941e5`.
- MySQL existente: `d929907f-99e2-433f-80c1-640ebbae9930`.
- Esquema exclusivo del panel: `little_paws_panel_v2`.
- Volumen privado del panel: `/data`; `LPN_PRIVATE_ROOT=/data/private`.

El backend antiguo conserva su servicio, sus bases y su Dockerfile raíz. El nuevo no aplica sus migraciones sobre los esquemas anteriores. El endpoint health es de liveness: comprueba que el proceso responde, no es monitoreo completo de MySQL.

## Configuración privada

El servicio consume `DJANGO_SETTINGS_MODULE=config.settings_railway`, `DJANGO_SECRET_KEY`, `LPN_DATA_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_SSL_MODE=REQUIRED`, `LPN_PRIVATE_ROOT` y `PORT`. Las variables están en Railway; no en el repositorio. MySQL usa la red privada y el usuario limitado al esquema nuevo. Las herramientas locales autorizadas usan un endpoint externo con TLS; no distribuir esas claves al equipo para simplemente entrar a la web.

Conservar la clave Fernet de bases existentes. Cambiarla sin migrar los datos impide descifrar documentos/referencias protegidos. Las contraseñas de personas se almacenan como hashes de Django y no son credenciales SQL.

Railway termina HTTPS en el edge. Solo `settings_railway` confía en `X-Real-IP`, documentado por Railway, para los límites por cliente; el desarrollo ignora cabeceras enviadas por el navegador. No ejecutar esa configuración detrás de otro proxy sin revisar qué cabeceras sobrescribe. El host `healthcheck.railway.app` y la excepción HTTP de `/api/health/` permiten la sonda interna; el resto fuerza HTTPS y cookies seguras.

## Construcción y despliegue

Directorio raíz del panel: `backend-panel/`. Dockerfile de dos etapas, compilación de wheels separada y runtime sin compilador. El entrypoint prepara únicamente el directorio privado del volumen y baja al usuario `app` antes de Gunicorn. WhiteNoise sirve los recursos públicos con nombres versionados. `railway.toml` configura healthcheck y reinicios limitados.

La publicación inicial auditada se hizo mediante CLI desde el directorio del panel. No asumir autodeploy desde GitHub hasta conectar explícitamente el servicio nuevo, rama y raíz correctos. El servicio antiguo sigue con su configuración anterior.

Para un despliegue manual autorizado, desde `backend-panel`:

```powershell
railway up . --path-as-root --project fd2429ee-8ee5-454d-9bdc-91c595d80547 --service 830362dc-fcb3-40c6-9850-c9dac01941e5 --environment production --detach
```

`--detach` inicia el despliegue: comprobar después estado SUCCESS, logs y login. No imprimir variables privadas ni incluir .env en archivos de construcción.

Las migraciones no se ejecutan automáticamente en el Dockerfile. Antes de una nueva versión, revisar el plan y aplicar únicamente a la base nueva, con respaldo cuando cambie datos. La auditoría aplicó `accounts.0002_usuario_debe_cambiar_clave`; los seis bloques iniciales ya estaban migrados. No usar `--fake` para ocultar diferencias ni ejecutar seeds de demo en producción.

## Acceso del equipo

José, Sally y Majo tienen cuentas individuales con rol `ADMIN_SEGURIDAD`, por decisión del propietario. No son superusuarios técnicos de Django. Las cuentas nuevas de Sally y Majo requieren cambiar su clave temporal antes de entrar al panel o usar la API. La contraseña previa de José se conserva. Credenciales entregadas por separado, nunca en Git ni en documentación. Desde el panel se puede cambiar la contraseña y revocar roles o desactivar usuarios conservando auditoría.

## Antes de una explotación real

Configurar y ensayar respaldos/restauración de MySQL y del volumen privado; definir retención, alertas y mantenimiento de sesiones/límites. Configurar correo transaccional y recuperación verificada; evaluar MFA para administradores. Completar los formularios operativos pendientes y probar accesibilidad/carga con objetivos acordados. El captcha aritmético y el límite de intentos no sustituyen medidas contra DDoS.

Referencias: [Django en Railway](https://docs.railway.com/guides/django), [healthchecks](https://docs.railway.com/deployments/healthchecks), [cabeceras del edge](https://docs.railway.com/networking/public-networking/specs-and-limits), [volúmenes](https://docs.railway.com/cli/volume).
