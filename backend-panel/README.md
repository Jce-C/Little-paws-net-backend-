# Backend Little Paws Net V2

Proyecto Django 5.2.18 + Django REST Framework 3.18.3 sobre MySQL 8. El esquema se crea con migraciones; **no se usan** `inspectdb`, SQL exportado de Lucid ni la base anterior. El modelo de negocio incluye 59 entidades y relaciones de reporte/rescate, expediente veterinario, adopción, apadrinamiento, fondo externo, tienda/pedidos, publicidad y validación.

## Instalación en Windows con PowerShell

1. Instalar Python 3.14 y MySQL Server 8.0. Workbench es opcional; sirve para inspeccionar, no para crear las tablas del proyecto.
2. Crear un esquema **nuevo y vacío** y un usuario exclusivo con permisos solo sobre ese esquema, desde una conexión administradora de MySQL:

   ```sql
   CREATE DATABASE little_paws_net_v2 CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
   CREATE USER 'lpn_app'@'127.0.0.1' IDENTIFIED BY 'REEMPLAZAR_CON_CLAVE_PRIVADA';
   GRANT ALL PRIVILEGES ON little_paws_net_v2.* TO 'lpn_app'@'127.0.0.1';
   ```

3. Dentro de `backend`, preparar el entorno e instalar dependencias:

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

4. Editar `.env` **solo en el equipo local**. Completar `MYSQL_PASSWORD`; sustituir `DJANGO_SECRET_KEY` por una clave aleatoria de al menos 32 caracteres; generar una clave Fernet para `LPN_DATA_KEY`. Estos comandos muestran claves nuevas para copiarlas manualmente, no deben guardarse en Git:

   ```powershell
   .\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   .\.venv\Scripts\python.exe -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

5. Crear la estructura y cargar datos sintéticos. `LPN_DEMO_PASSWORD` debe ser una clave **solo de demostración** de 12 o más caracteres; puede colocarse en `.env` local.

   ```powershell
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py seed_demo
   .\.venv\Scripts\python.exe manage.py verify_demo
   .\.venv\Scripts\python.exe manage.py runserver
   ```

`seed_demo` es idempotente: crea 135 registros principales (20 usuarios, 15 mascotas, 25 reportes, 10 casos, 15 solicitudes de adopción, 15 apadrinamientos, 12 compromisos de fondo, 15 productos y 8 pedidos), además de las entidades, catálogos, historiales y relaciones auxiliares. Todos son sintéticos. Los correos son `demo01@example.invalid` a `demo20@example.invalid` y usan `LPN_DEMO_PASSWORD`. El número de cuenta `000123456789` es ficticio, se almacena cifrado y **no debe utilizarse para transferir dinero**.

`verify_demo` ejecuta 28 comprobaciones HTTP/negocio y revierte sus cambios; cubre registro de usuarios, gestión de reportes anónimos, acceso no autorizado, reporte/rescate con cobertura, QR y anotación médica, adopción, pedido, fondo y apadrinamiento. Las dos pruebas unitarias sin base se ejecutan con `manage.py test accounts config`. Para una suite Django completa debe concederse a la cuenta de pruebas permiso sobre un esquema `test_little_paws_net_v2` separado; no configurar el test runner para borrar la base V2 con datos demo.

## Endpoints principales

| Ruta | Uso |
| --- | --- |
| `POST /api/auth/registro/`, `/api/auth/token/`, `/api/auth/token/refresh/`, `/api/auth/token/revoke/` | Identidad con correo y contraseña; JWT con renovación revocable |
| `POST /api/reportes/`, `POST /api/reportes/{id}/gestion-anonima/`, `POST /api/reportes/{id}/aceptar/`, `GET /api/casos/{id}/` | Reporte, edición/cierre con clave privada antes de la aceptación, rescate y seguimiento |
| `POST /api/mascotas/{id}/autorizaciones/`, `POST /api/mascotas/{id}/qr/`, `POST /api/qr/{token}/atenciones/` | Expediente; el QR no sustituye la verificación ni la autorización |
| `GET /api/adopcion/mascotas/`, `POST /api/adopcion/solicitudes/`, `POST /api/adopcion/solicitudes/{id}/resolver/` | Disponibilidad y resolución de adopción |
| `POST /api/apadrinamientos/`, `GET /api/apadrinamientos/{id}/cuenta/`, `POST /api/apadrinamientos/{id}/declaraciones/`, `POST /api/apadrinamientos/{id}/confirmaciones/` | Compromiso, cuenta privada, declaración y recepción confirmada por fundación |
| `GET /api/fondos/`, `POST /api/fondos/donaciones/`, `POST /api/fondos/{id}/distribuciones/` | Información del fondo externo; no se procesan pagos |
| `GET /api/catalogo/productos/`, `POST /api/pedidos/`, `GET /api/pedidos/{id}/` | Catálogo y pedido referencial; no hay cobro ni reserva |
| `GET /api/catalogos/`, `GET /api/publicidad/`, `GET /api/notificaciones/` | Consulta de catálogos, publicidad aprobada y bandeja interna |

Las operaciones privadas usan `Authorization: Bearer <access_token>`. Los roles de negocio están en `Rol`, `Permiso`, `UsuarioRol` y `EntidadMiembroRol`; `is_superuser` es solo para administración técnica de Django. El reporte anónimo devuelve su clave privada **una sola vez**; solo se almacena su hash. Con ella puede editar o cerrar el reporte mientras siga pendiente. Registro, autenticación y gestión anónima tienen límites de solicitudes; para varios servidores debe configurarse una caché compartida antes del despliegue. La etapa 2 incorpora carga/descarga privada de documentos, verificación y versiones/revisión de publicidad: sus rutas y límites están en el informe de cierre. Los archivos privados se almacenan fuera de rutas públicas y de Git.

## Seguridad y alcance

La revisión final añade el login animado real con los fondos originales de escritorio/móvil, edición del catálogo de permisos y acciones visibles según autorización. El formulario envía credenciales únicamente a Django mediante POST con CSRF. `frontend/panel-design/build-login-django.py` sincroniza presentación y recursos sin copiar la autenticación ficticia de la demo. La base nueva de Railway y los pasos de inicialización privada están en `docs/entrega/railway.md`; el acceso local se comprueba con `panel_railway.ps1`. La configuración de despliegue preparada es `config.settings_railway` y tiene sus dependencias en `requirements-railway.txt`; no se ha publicado esta versión todavía.

El estilo compartido del panel se documenta en [STYLE.md](../STYLE.md). `tokens.css` define colores, fuentes y radios; `sistema.css` aplica el estilo editorial cálido a las plantillas existentes sin alterar la autorización del servidor. La [vista de diseño](../demos/panel-editorial/README.md) usa datos ficticios; el [scroll de bienvenida](../demos/login-entrada/README.md) sigue como demostración aislada.

La etapa 2 añade el módulo `seguridad`: API administrativa, responsables, transferencias, asignaciones, auditoría y recorridos de negocio con aprobación y alcance privado. Consultar [Cierre de la etapa 2](../docs/rbac/06-cierre-etapa-2.md) y [Guía de archivos y tecnologías](../docs/rbac/05-guia-archivos-y-tecnologias.md). La API parte de `/api/seguridad/`; los recorridos adicionales están en `/api/seguridad/operaciones/`. La [etapa 3](../docs/rbac/07-etapa-3-acceso-web.md) ya implementa el acceso web en `/panel/login/`, captcha consumible, límites de intentos en MySQL, sesiones de 30 minutos, CSRF, navegación por permisos y panel inicial. El [boceto editable de Figma](../docs/diseno/README.md) define también los formularios operativos que se conectarán después. Los roles amplios anteriores quedan deshabilitados y `seed_demo` se niega a reactivar cuentas de demostración dadas de baja. Las cuentas receptoras utilizan preparación y aprobación separadas; la publicación directa antigua sigue bloqueada.

- `.env`, `.venv`, archivos médicos reales y claves bancarias no se publican. Antes de uso fuera de una demo local: `DJANGO_DEBUG=false`, secret y clave Fernet propios, HTTPS, almacenamiento privado de archivos, copia de seguridad y servidor/cola de notificaciones externos.
- MySQL genera `POINT` y `MULTIPOLYGON` SRID 4326 e índices espaciales; el backend no requiere GDAL en Windows. `DetallePedido` tiene FK compuestas MySQL que impiden mezclar tiendas. `CustodiaMascota` solo admite una custodia vigente por mascota.
- Las transferencias y el fondo son **externos**. Una declaración de transferencia no acredita recepción; la fundación confirma. Un pedido no cobra ni descuenta inventario.
- Esta entrega es un backend académico verificable, **no un despliegue de producción**. Las operaciones pendientes descritas arriba requieren implementación y pruebas si pasan a formar parte del alcance evaluado.
