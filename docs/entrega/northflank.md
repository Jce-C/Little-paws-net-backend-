# Northflank: configuración del panel

Usar `backend-panel/Dockerfile`, contexto `backend-panel`, una instancia y un proceso Uvicorn. Conservar los recursos incluidos en Sandbox; no crear planes de pago.

Configurar `DJANGO_SETTINGS_MODULE=config.settings_northflank` en **runtime**, `LPN_PRIVATE_ROOT=/data/private` sobre volumen persistente, `DJANGO_ALLOWED_HOSTS` con el hostname público exacto, `DJANGO_CSRF_TRUSTED_ORIGINS=https://HOSTNAME`, `DJANGO_SECRET_KEY` y `LPN_DATA_KEY` propios, y `MYSQL_HOST/PORT/DATABASE/USER/PASSWORD` mediante secretos internos. No introducir secretos de runtime como argumentos de build. Para MySQL con TLS, configurar `MYSQL_SSL_MODE=REQUIRED` y verificar la conexión real antes de migrar.

Se reutiliza la configuración HTTPS/cookies/WhiteNoise de producción, desactivando la confianza en Railway y su hostname de salud. Los límites de autenticación usan `X-Envoy-External-Address`, que Northflank reemplaza en su ingress **público**, validando una sola dirección IP. No se confía en valores de `X-Forwarded-For` suministrados por el cliente. Si la cabecera falta o es inválida, se usa la dirección del socket.

Esta configuración exige un servicio detrás del ingress público de Northflank. No utilizarla en un origen público directo ni confiar en peticiones internas/VPC no controladas: la garantía de sustitución de esa cabecera no se aplica a esas rutas. No añadir otro CDN delante durante esta demostración.

Fuente: [Networking on Northflank](https://northflank.com/docs/v1/application/network/networking-on-northflank).

Puerto de aplicación 8000, health check HTTP `/api/health/`. Este endpoint no comprueba disponibilidad de la base. Verificar además login, archivos y una operación de negocio.

Crear tablas únicamente sobre el esquema nuevo `little_paws_demo`, con `migrate --plan` y `migrate --noinput`. Cargar mediante `preparar_presentacion --database-name little_paws_demo` e `ilustrar_presentacion` con confirmación del mismo nombre. Mantener `LPN_ALLOW_DEMO_SEED=1` solo durante esa carga. No pegar datos de conexión ni claves en issues, chats o el repositorio.
