# Northflank: configuración del panel

Usar `backend-panel/Dockerfile`, contexto `backend-panel`, una instancia y un proceso Uvicorn. Conservar los recursos incluidos en Sandbox; no crear planes de pago.

Configurar `DJANGO_SETTINGS_MODULE=config.settings_northflank` en **runtime**, `LPN_PRIVATE_ROOT=/data/private` sobre volumen persistente, `DJANGO_ALLOWED_HOSTS=HOSTNAME,127.0.0.1,localhost` con el hostname público exacto y las direcciones de las sondas internas, `DJANGO_CSRF_TRUSTED_ORIGINS=https://HOSTNAME`, `DJANGO_SECRET_KEY` y `LPN_DATA_KEY` propios, y `MYSQL_HOST/PORT/DATABASE/USER/PASSWORD` mediante secretos internos. No introducir secretos de runtime como argumentos de build. Para MySQL con TLS, configurar `MYSQL_SSL_MODE=REQUIRED` y verificar la conexión real antes de migrar.

Se reutiliza la configuración HTTPS/cookies/WhiteNoise de producción, desactivando la confianza en Railway y su hostname de salud. Los límites de autenticación usan `X-Envoy-External-Address`, que Northflank reemplaza en su ingress **público**, validando una sola dirección IP. No se confía en valores de `X-Forwarded-For` suministrados por el cliente. Si la cabecera falta o es inválida, se usa la dirección del socket.

Esta configuración exige un servicio detrás del ingress público de Northflank. No utilizarla en un origen público directo ni confiar en peticiones internas/VPC no controladas: la garantía de sustitución de esa cabecera no se aplica a esas rutas. No añadir otro CDN delante durante esta demostración.

Fuente: [Networking on Northflank](https://northflank.com/docs/v1/application/network/networking-on-northflank).

Puerto de aplicación 8000, health check HTTP `/api/health/`. Este endpoint no comprueba disponibilidad de la base. Verificar además login, archivos y una operación de negocio.

Crear tablas únicamente sobre el esquema nuevo `little_paws_demo`, con `migrate --plan` y `migrate --noinput`. Cargar mediante `preparar_presentacion --database-name little_paws_demo` e `ilustrar_presentacion` con confirmación del mismo nombre. Mantener `LPN_ALLOW_DEMO_SEED=1` solo durante esa carga. No pegar datos de conexión ni claves en issues, chats o el repositorio.

## Demostración alojada, 25 de noviembre de 2026

[Acceso al panel](https://p01--little-paws-panel--mbdslkhqlqj9.code.run/panel/login/). Instalación académica con datos ficticios; no introducir datos reales ni realizar pagos.

Servicio `little-paws-panel`: una instancia `nf-compute-20`, 0.2 vCPU y 512 MB, puerto HTTP interno 8000 y HTTPS público. CI automático desactivado: construir manualmente solo un commit validado. Base `little-paws-db` con TLS y red privada; sus cinco variables se enlazan mediante el grupo `little-paws-database`, restringido a este servicio y al runtime. Volumen `little-paws-files`, 6 GB, montado en `/data/private` y etiquetado Free. No abrir MySQL a Internet.

Se comprobó la conexión TLS, el montaje real, la aplicación con UID 10001, el reinicio conservando 21 cuentas ficticias, 20 mascotas y 15 productos, y la descarga de las 20 ilustraciones WebP después de reiniciar. El catálogo público contiene cinco mascotas disponibles. Las pruebas externas comprobaron login por API, perfil, accesos efectivos y autorización: administración puede listar usuarios y ciudadanía recibe 403. Las variables de carga y su contraseña se retiran del servicio al terminar; los accesos se entregan por separado, nunca en el repositorio.

La cuenta y los recursos permanecen en Sandbox/Free; el panel de facturación mostraba US$0.00 al verificar. Esto describe una comprobación puntual, no garantiza consumo ilimitado. La tarifa genérica de almacenamiento que aparece en formularios no equivale por sí sola al coste facturado de un recurso Free. No actualizar a Pay as you go ni ampliar recursos sin revisar el presupuesto. El umbral de factura de US$50 no es un límite que detenga el consumo. Sandbox es para demostración, sin compromiso de disponibilidad para producción.

Antes de aceptar datos reales: revisión de privacidad, licencias y seguridad, copias externas con prueba de restauración, monitorización y presupuesto de producción. La APK de prueba usa este origen HTTPS, sin contraseñas incluidas; requiere una firma privada de distribución y validación en teléfono físico antes de publicarse en una tienda.
