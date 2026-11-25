# Little Paws Net

Plataforma de protección animal que conecta a ciudadanos con organizaciones. Reúne un backend y panel web en Django, una API REST y una app Android en Flutter para adopciones, reportes y seguimiento.

## Estado de esta entrega

La integración del [Pull Request #24](https://github.com/Jce-C/Little-paws-net-backend-/pull/24) ya está incorporada en `main`, conservando los commits del equipo. Publicar código en GitHub no configura por sí solo un alojamiento.

La base técnica se verificó con **479 pruebas Django en MySQL aislado**, pruebas del cliente y aceptación real en Android Emulator y navegador. El recorrido comprobado incluye solicitud de adopción desde Android, resolución desde el panel y consulta del resultado en la app. También se comprobó conceder y revocar permisos, y renombrar un recurso con otra sesión abierta.

Es una versión de demostración e integración. Antes de ofrecerla públicamente faltan la revisión final de privacidad, licencias y seguridad, pruebas en teléfono físico, configuración del alojamiento y su presupuesto, y firma de distribución Android. Los precios son referenciales: los pedidos no realizan cobros y los aportes son compromisos, sin pasarela de pago.

## Funcionalidades principales

- Usuarios, varios roles por persona, permisos por recurso y acción, excepciones y auditoría.
- Matriz de permisos configurable y menú dinámico. El backend verifica las operaciones; ocultar un botón no sustituye esa autorización.
- Sincronización del panel entre sesiones mediante ASGI y eventos del servidor.
- Organizaciones, catálogos, mascotas, reportes y gestión de rescates.
- Solicitudes de adopción, evaluación por etapas, decisiones y seguimiento.
- Expedientes veterinarios y fotografías públicas autorizadas separadas de los documentos privados.
- Directorio, comunidad, programas de ayuda, catálogo comercial y pedidos.
- Panel en español e inglés, preferencias de accesibilidad y apariencia. Los datos introducidos por personas no se traducen automáticamente.

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `backend-panel/` | Backend vigente, API y panel de gestión. Tiene su propio Dockerfile. |
| `backend-panel/seguridad/templates/` | Plantillas del panel web. |
| `backend-panel/seguridad/static/` | Estilos, scripts, fuentes e imágenes del panel. |
| `frontend/mobile/` | Aplicación Flutter y pruebas del cliente. |
| `DIAGRAMAS/` | Diagramas UML originales del equipo, conservados. |
| `docs/` | Arquitectura, RBAC, diseño, entrega y evidencias. |
| `scripts/` | Herramientas de medición y pruebas auxiliares. |
| `backend/` y `Dockerfile` de la raíz | Implementación anterior conservada; no es el servicio del panel actual. |

Las dos implementaciones de backend tienen historias de migraciones diferentes. La versión vigente se ejecuta desde **`backend-panel/`**, usando una base propia. No aplicar sus migraciones sobre una base anterior.

## Requisitos

- Python 3.14 y Git.
- MySQL 8; la integración continua utiliza MySQL 8.4 en una instancia aislada.
- Flutter compatible con Dart 3.13 para la app, SDK de Android y un emulador o teléfono Android.
- En Linux, herramientas de compilación y bibliotecas de desarrollo MySQL para instalar `mysqlclient`.

Las dependencias concretas están en `backend-panel/requirements*.txt` y `frontend/mobile/pubspec.yaml`.

## Instalar y ejecutar el panel

Desde la raíz del repositorio, en PowerShell:

```powershell
cd backend-panel
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-railway.txt
Copy-Item .env.example .env
```

Crear un esquema MySQL vacío y una cuenta SQL exclusiva. Completar el `.env` privado con `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST` y `MYSQL_PORT`; una `DJANGO_SECRET_KEY` propia, una clave Fernet en `LPN_DATA_KEY` y hosts locales permitidos. Para desarrollo, `DJANGO_DEBUG=true`.

La [guía del backend](backend-panel/README.md) incluye la creación del esquema y del usuario SQL. No cambiar la clave de cifrado de una base que ya contiene datos cifrados: conservarla junto con su respaldo.

Después de configurar la conexión:

```powershell
.\.venv\Scripts\python.exe manage.py migrate --plan
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py check
```

Para una instalación vacía de uso real, crear el primer administrador con su correo; el comando solicita la contraseña sin mostrarla y no concede superusuario técnico:

```powershell
.\.venv\Scripts\python.exe manage.py iniciar_seguridad --email responsable@example.com --nombre "Responsable de seguridad"
```

Para una demostración, usar la carga del apartado siguiente en lugar de crear antes esa cuenta.

Iniciar el servidor local:

```powershell
.\.venv\Scripts\python.exe -m uvicorn config.asgi:application --host 127.0.0.1 --port 8000 --reload
```

Abrir [el login local](http://127.0.0.1:8000/panel/login/). Uvicorn ejecuta ASGI para la sincronización; `--reload` es exclusivamente de desarrollo.

## Preparar datos de demostración

Utilizar una **base nueva y vacía**, con nombre terminado en `_demo`, almacenamiento privado independiente y claves propias. En el entorno privado, definir `LPN_ALLOW_DEMO_SEED=1` y una `LPN_DEMO_PASSWORD` de al menos 12 caracteres. No añadir estas claves al repositorio ni al APK.

Tras aplicar las migraciones, ejecutar desde `backend-panel`, sustituyendo `mi_presentacion_demo` por el nombre exacto configurado:

```powershell
.\.venv\Scripts\python.exe manage.py preparar_presentacion --database-name mi_presentacion_demo
.\.venv\Scripts\python.exe manage.py ilustrar_presentacion --database-name mi_presentacion_demo
.\.venv\Scripts\python.exe manage.py verify_demo --presentacion
```

La carga se niega a sobrescribir una base con cuentas o datos de negocio. Crea 21 cuentas ficticias, 20 mascotas, organizaciones, reportes, solicitudes y 15 productos, además de catálogos de ciudades y razas. Separa cinco mascotas disponibles de otras cinco que ya tienen solicitudes pendientes. Publica 20 ilustraciones originales identificadas como ejemplos. El verificador revierte sus operaciones de prueba; el uso manual de la app sí conserva los cambios realizados.

| Cuenta de ejemplo | Función |
| --- | --- |
| `demo20@example.invalid` | Ciudadano |
| `demo01@example.invalid` | Responsable de la primera fundación |
| `demo04@example.invalid` | Catálogo y pedidos de la tienda |
| `demo05@example.invalid` | Veterinario dentro de su ámbito autorizado |
| `administracion@example.invalid` | Administración de seguridad |

La contraseña procede del entorno privado. Estos correos, organizaciones, animales y operaciones son ficticios. No utilizarlos para contactar personas ni realizar transferencias reales. Guion completo: [presentación y comprobaciones](docs/entrega/presentacion-y-commits.md).

## Ejecutar la app Android

Desde `frontend/mobile`, con el backend local anterior funcionando en el puerto 8000:

```powershell
flutter pub get
flutter run --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8000
```

`10.0.2.2` apunta al equipo anfitrión desde Android Emulator. Si se usa otro puerto, cambiarlo en ambos lados. Para teléfono por USB y otras opciones, consultar la [guía de la app](frontend/mobile/README.md).

La app y el panel deben utilizar el mismo backend y la misma base para compartir cambios. Sin `LPN_API_BASE_URL` la app muestra un aviso; no se conecta a Railway por omisión. Una distribución alojada necesita un origen HTTPS explícito. Las cuentas se introducen en la pantalla de acceso, no en la compilación.

## Calidad y colaboración

GitHub Actions verifica dependencias, traducciones, configuración, migraciones y la suite completa Django con MySQL aislado, además de las pruebas de herramientas. No utiliza la base de demostración ni la de producción. El estado vigente se consulta en [Actions](https://github.com/Jce-C/Little-paws-net-backend-/actions).

En el cliente, desde `frontend/mobile`:

```powershell
flutter analyze
flutter test --no-pub
```

Las pruebas de integración Android requieren un backend y datos de prueba preparados; no deben apuntar a producción. Las mediciones locales no garantizan la latencia ni el consumo del alojamiento.

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para ramas, commits, Pull Requests y pruebas; [CHANGELOG.md](CHANGELOG.md) para cambios; y [Semana 15](docs/entrega/semana-15-evolucion.md) para el trabajo de evolución del software.

## Diagramas y documentación

Los diagramas originales permanecen en `DIAGRAMAS/` y pueden abrirse con diagrams.net o una herramienta compatible con `.drawio`:

- [Diagrama de componentes](<DIAGRAMAS/Little Paws Net - Componentes UML.drawio>).
- [Diagrama de despliegue](<DIAGRAMAS/Little Paws Net - Despliegue UML.drawio>).
- [Reglas de acceso y responsabilidades](docs/rbac/01-definicion-de-accesos.md).
- [Guía de presentación integrada](docs/entrega/presentacion-y-commits.md).
- [Identidad visual](STYLE.md).

Conservar los archivos originales no significa que se hayan actualizado para cada cambio de infraestructura; revisar su contenido al decidir el alojamiento final.

## Publicación y datos privados

El contexto del contenedor vigente es `backend-panel/`. La configuración `settings_railway` es específica de Railway; antes de utilizar otro proveedor, revisar HTTPS, cabeceras del proxy, hosts, CSRF, base y volumen privado. La [guía de despliegue existente](docs/entrega/railway.md) debe adaptarse al proveedor elegido y sus límites de consumo.

Antes de desplegar, comprobar conexiones automáticas al alojamiento anterior, presupuesto, restauración de base y archivos, conservación de claves, políticas de datos y firma Android. Fusionar un PR no sustituye estas comprobaciones.

No subir `.env`, tokens, contraseñas, respaldos, archivos privados ni almacenes de firma. El archivo de entorno heredado se retiró del seguimiento en esta integración, pero sigue en el historial anterior: cualquier credencial todavía vigente debe revisarse y rotarse. Eliminarla de una versión no la revoca.
