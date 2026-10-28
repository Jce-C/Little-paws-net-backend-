# Etapa 3 · Acceso web y panel inicial

Implementado el 26 de octubre de 2026. La etapa 2 aportó autorización y API; esta etapa permite usarlas desde un navegador con sesión de Django. El boceto completo posterior se entrega en [Figma y su inventario](../diseno/README.md).

## Qué se implementó

- Login con correo, contraseña, botón para mostrarla y desafío de suma.
- Captcha válido cinco minutos, ligado a una sesión y consumido una sola vez. Una respuesta errónea obliga a emitir otra suma; otra sesión no puede consumirlo. El servidor guarda hashes del resultado y de la sesión.
- Límites compartidos en MySQL: 25 envíos de login por IP, ocho por correo normalizado y 60 emisiones de captcha por IP en ventanas fijas de 15 minutos. Los intentos que exceden devuelven HTTP 429 y Retry-After. No se confía en X-Forwarded-For recibido del navegador.
- Sesión de duración máxima absoluta de 30 minutos, rotación al entrar y cierre por POST. El middleware comprueba también la expiración antes de las solicitudes a la API.
- Cookies HttpOnly y SameSite=Lax; Secure por defecto cuando DEBUG es falso. CSRF protege el login, el cierre de sesión y las mutaciones de la API autenticadas mediante sesión.
- La API conserva autenticación JWT para clientes móviles y añade SessionAuthentication para el panel. El navegador no guarda JWT en localStorage.
- Inicio y menú derivados de permisos actuales; selector limitado a organizaciones propias y recalculado al cambiar de entidad. Revocar un rol o desactivar la cuenta corta el acceso efectivo. El administrador técnico de Django no obtiene un rol de negocio automáticamente.
- Pantallas adaptables a móvil, diálogos nativos y mensajes de carga, vacío y error. Estilos CSS y fuente Manrope alojados en el propio proyecto.

El captcha aritmético sirve como barrera básica de automatización y requisito académico; **no evita un ataque DDoS**. Los límites anteriores protegen este login y no equivalen al control de tráfico de toda una infraestructura.

## Rutas

| Ruta | Comportamiento |
| --- | --- |
| GET/POST `/panel/login/` | Formulario, validación y creación de sesión |
| GET `/panel/` | Inicio con accesos autorizados |
| GET `/panel/modulos/<codigo>/` | Módulo con comprobación de acceso en servidor |
| POST `/panel/organizacion/` | Cambiar entre organizaciones autorizadas |
| POST `/panel/logout/` | Cerrar sesión |

Las tablas utilizan las API de `/api/seguridad/` y `/api/seguridad/operaciones/`. El backend vuelve a comprobar permisos y alcance en cada operación; ocultar una opción del menú no sustituye esa validación.

## Alcance funcional de la interfaz actual

El panel permite consultar los módulos autorizados y sus registros. Incluye crear/editar usuarios, roles y recursos; asignar o revocar roles globales con motivo; consultar y guardar la matriz de permisos de un rol; consultar auditoría; tomar solicitudes de las colas y abrir registros asignados. Las API conservan las restricciones de roles del sistema y los límites sobre el último administrador.

Los otros módulos ofrecen tablas y detalles iniciales según el permiso disponible. Los formularios completos de transferencia de principal, preparación/aprobación de cuentas, verificación documental, resolución de reclamaciones, anotaciones clínicas y operación se representan en el boceto de Figma para conectarlos en la siguiente implementación visual. **No se presentan como formularios web ya terminados por existir su API.**

## Archivos y tecnologías, paso a paso

1. `config/urls.py` conecta `/panel/` con `seguridad/web/urls.py`. Django selecciona la vista de la ruta solicitada.
2. `web/forms.py` valida los campos del login. `web/acceso.py` emite/consume desafíos, cuenta intentos y controla la duración absoluta de la sesión.
3. `web/views.py` autentica, aplica CSRF, comprueba permisos, selecciona la organización y renderiza HTML. Los destinos de retorno se restringen al panel del mismo sitio.
4. `web/contexto.py` construye navegación y ámbito actuales a partir de la autorización de etapa 2. La responsabilidad principal se obtiene del registro único de responsable de entidad; asignar un rol puente no basta.
5. `templates/seguridad/web/` contiene acceso, estructura, inicio, módulo y estados. Django Templates escapa los datos al renderizarlos.
6. `static/seguridad/panel.css` define identidad, campos, tablas, diálogos y adaptación móvil. `fonts/` guarda Manrope y su licencia OFL. No se necesita un servidor de Node para servir esta interfaz.
7. `static/seguridad/panel.js` consume las API con fetch y sesión del mismo origen; envía el token CSRF al guardar. Construye el contenido con nodos y textContent para evitar interpretar los datos como HTML.
8. `seguridad/models.py` y `migrations/0007_acceso_web.py` añaden DesafioWeb y LimiteWeb. MySQL coordina su consumo y actualización mediante transacciones y bloqueo de filas, también entre procesos.
9. `config/settings.py` registra la sesión de DRF, el middleware y las cookies. `tests_web.py` verifica el comportamiento nuevo.

La interfaz y el backend permanecen en el mismo repositorio. `web/`, `templates/` y `static/` distinguen la capa de presentación; servicios, autorización, modelos y API conservan la lógica y los datos. Django Admin permanece disponible como herramienta técnica; el equipo de negocio entra por `/panel/`.

## Cómo abrirlo en local

El servidor de vista previa de esta entrega escucha en `http://127.0.0.1:8000/panel/login/`. Para iniciarlo de nuevo, desde `backend` y con el entorno local configurado:

```powershell
$env:DJANGO_DEBUG = "true"
$env:DJANGO_COOKIE_SECURE = "false"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Esas dos variables habilitan el desarrollo por HTTP local; el servidor público debe usar su configuración de despliegue y HTTPS.

La base local conserva 20 cuentas de demostración inactivas y ningún administrador activo. No se reactivaron para enseñar la interfaz. El propietario inicializa su cuenta desde su terminal, sin compartir contraseñas:

```powershell
.\.venv\Scripts\python.exe manage.py iniciar_seguridad --email TU_CORREO --nombre "Tu nombre"
```

El comando solicita y confirma la contraseña de forma oculta. No reactiva cuentas desactivadas ni permite inicializar un segundo administrador si ya hay uno activo. Después se entra por el login del panel con la cuenta creada.

## Validación

- **107 pruebas aprobadas** en MySQL aislado: 84 anteriores y 23 nuevas de acceso web.
- Incluyen CSRF en login/cierre/API, captcha incorrecto/expirado/repetido/de otra sesión, límites, cookies y rotación, expiración absoluta, datos escapados, usuario sin rol, cuenta desactivada, permisos revocados y cambio entre dos organizaciones.
- Dos pruebas concurrentes nuevas comprueban consumo único del desafío y conteo compartido de intentos.
- `manage.py check`, comprobación de migraciones y sintaxis de JavaScript sin incidencias.
- Migración `seguridad.0007_acceso_web` aplicada en la base local. No se publicaron credenciales ni se activaron cuentas demo.

El servidor MySQL usado para las pruebas es independiente del esquema habitual. El informe de etapa 2 y la configuración `settings_test_mysql.py` explican la separación de las pruebas.
