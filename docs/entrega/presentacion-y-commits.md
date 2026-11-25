# Presentación local y preparación de commits

La demostración utiliza el backend real y una base nueva terminada en `_demo`.
La demo visual en memoria no sincroniza sus cambios con el panel.

## Preparación desde cero

1. Respaldar SQL, archivos privados y clave de cifrado de la instalación anterior. Mantenerlos fuera de Git y comprobar su recuperación antes de eliminar el origen.
2. Crear un esquema MySQL vacío y una cuenta SQL exclusiva con permisos únicamente sobre ese esquema. No reutilizar producción ni `config.settings_qa`: este último utiliza hashes rápidos exclusivos de pruebas.
3. Crear un archivo de entorno privado con la configuración de `.env.example`. Indicarlo mediante `LPN_ENV_FILE`. Definir una clave secreta y una clave Fernet nuevas, contraseña de demostración robusta, almacenamiento privado independiente y `LPN_ALLOW_DEMO_SEED=1`.
4. Activar el entorno Python, entrar a `backend-panel` y ejecutar (sustituir el nombre por el esquema realmente configurado):

```powershell
python manage.py migrate --noinput
python manage.py preparar_presentacion --database-name mi_presentacion_demo
python manage.py ilustrar_presentacion --database-name mi_presentacion_demo
python manage.py check
```

El comando requiere confirmar el nombre completo y se niega a actuar si encuentra usuarios, organizaciones o registros de negocio. No tiene opción de borrado ni de sobrescritura. La operación de carga es transaccional: si falla su aceptación, revierte los datos de negocio.

Para repetir las comprobaciones sin conservar operaciones de prueba:

```powershell
python manage.py verify_demo --presentacion
```

Los límites de autenticación siguen activos. Si se ejecuta repetidamente en menos de un minuto puede aparecer HTTP 429; esperar el tiempo indicado, sin desactivar la protección.

## Contenido y cuentas

- 21 personas ficticias; correos reservados `example.invalid`, sin teléfonos inventados.
- 20 mascotas: diez en rescate, cinco con solicitudes pendientes y cinco disponibles para una solicitud nueva, con presentación individualizada y custodia.
- Reportes, rescates, solicitudes, aportes simulados y pedidos relacionados; catálogo de 15 alimentos con precios referenciales en COP.
- Catálogos de ciudades DIVIPOLA, incluida Riohacha, especies y razas.
- Organizaciones claramente identificadas como demostración; no ofrecen servicios reales.

| Cuenta | Uso |
|---|---|
| `demo20@example.invalid` | Ciudadano: solicitar adopción y registrar reportes |
| `demo01@example.invalid` | Responsable de rescates, adopciones y aportes de la primera fundación |
| `demo04@example.invalid` | Responsable de catálogo y pedidos de la tienda |
| `demo05@example.invalid` | Veterinario autorizado dentro de su alcance |
| `administracion@example.invalid` | Administración de seguridad, sin superusuario técnico Django |

La contraseña se toma de `LPN_DEMO_PASSWORD`, exclusivamente del entorno privado. No se publica ni se incluye en APK/ZIP/Git. Esta contraseña compartida corresponde a una demostración aislada: para usuarios reales se necesitan claves individuales.

`ilustrar_presentacion` publica cinco ilustraciones de mascotas y quince de productos. Son dibujos procedurales originales con rótulo de ejemplo; no contienen fotos ni marcas ajenas. Se publican mediante los servicios reales, sus permisos, WebP y auditoría, y se conservan las imágenes que ya existan. No son fotografías de animales ofrecidos realmente. Para sustituirlas posteriormente, cargar imágenes autorizadas desde el panel. Las cuentas, transferencias y diagnósticos incluidos son ficticios y no deben presentarse como operaciones reales.

## App y panel sobre la misma base

Desde `backend-panel`, con ese mismo archivo de entorno:

```powershell
python -m uvicorn config.asgi:application --host 127.0.0.1 --port 8023
```

Panel: `http://127.0.0.1:8023/panel/login/`.
Desde `frontend/mobile`, para Android Emulator:

```powershell
flutter run --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8023
```

Esto es desarrollo local, no un enlace público. La versión alojada requiere HTTPS y configuración del proveedor antes de compilar la app. No debe abrirse MySQL a Internet.

Guion: iniciar ciudadano, solicitar Canela; iniciar responsable, tomar la solicitud y resolverla; consultar el resultado desde ciudadano. Después, desde administración, conceder y revocar una vista al rol ciudadano y comprobar la autorización desde otra sesión. Verificar también el cambio de nombre de un recurso y su reflejo en el menú.

## Integración Git del equipo

Al revisar el remoto el 25 de noviembre de 2026, `main` apuntaba a `016415b3a70ccf6173dd2d39cf284b6c898fa305`; la copia local avanzada parte de `795c413`. Los ZIP anteriores basados en `795c413` no sirven directamente para ese `main`. Los nuevos manifiestos deben declarar la base remota y comprobarse juntos en una copia limpia.

Orden: José (backend, carga y CI), Sally (app), Majo (diseño del panel y documentación). Usar los paquetes nuevos de presentación, no superponer ZIP históricos. Cada persona crea su propio commit. Los tres bloques se validan juntos; un bloque aislado no representa la entrega completa.

Antes de aplicar: `git fetch origin`, comprobar remoto, estado limpio y hash de base. No utilizar `reset --hard`, ni forzar un parche. Si `main` cambió, revisar y regenerar los paquetes.

El remoto conserva un `backend/.env` versionado de una etapa anterior. José debe ejecutar `git rm --cached --ignore-unmatch backend/.env`: conserva el archivo local y deja de incluirlo en versiones nuevas. No copiar su contenido a PR, capturas ni parches compartidos. Esto no borra el secreto del historial: revisar y rotar cualquier credencial todavía vigente antes de publicar el despliegue.

Mensajes propuestos:

- José: `feat: integrar backend RBAC y datos de presentacion aislados`
- Sally: `feat: integrar app movil con flujos de adopcion y reportes`
- Majo: `feat: integrar diseno del panel y documentacion de entrega`

Para esta entrega acumulada se recomienda una rama compartida `feature/presentacion-integrada`: José crea y sube el primer commit, Sally actualiza esa rama y añade el suyo, después Majo actualiza y añade el tercero. Abrir el PR a main cuando estén los tres bloques y CI apruebe el conjunto. No integrar ni desplegar un bloque aislado: las pruebas del backend también necesitan las plantillas del bloque de diseño. Los archivos de los paquetes son distintos y su aplicación conjunta fue comprobada. No modificar autorías ni crear commits a nombre de las compañeras desde otra cuenta.

## Antes de subir una versión pública

Pendientes: aceptación visual con app real y teléfono, revisión de seguridad/licencias/privacidad, configuración y presupuesto del alojamiento, firma Android y verificación remota de CI. Se comprobó la restauración SQL local y las ilustraciones no utilizan fotos de terceros; aún debe validarse el respaldo completo de archivos y claves en el alojamiento elegido. Los tests locales no certifican esos puntos. La tienda inicia pedidos sin cobrar y los aportes son compromisos; no anunciar una pasarela real.
