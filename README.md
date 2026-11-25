# Little Paws Net

Little Paws Net conecta a ciudadanos y organizaciones de protección animal. Incluye un panel web con Django, Django REST Framework y MySQL, y un cliente Android en Flutter para consultar mascotas y gestionar solicitudes de adopción.

**Base local para integrar:** [estado, paquetes y orden de entrega](docs/entrega/base-solida-local.md). Incluye tienda paginada y comprobaciones completas. Los commits, la versión y el despliegue se preparan después de revisar esta base; no se anuncia como publicación comercial.

## Qué ejecutar

| Carpeta | Responsabilidad |
| --- | --- |
| `backend-panel/` | Aplicación vigente: login, usuarios, roles, recursos, permisos y auditoría; dominio y API V2. |
| `frontend/mobile/` | Aplicación ciudadana Android. Incluye catálogo, acceso, solicitud y seguimiento de adopción. |
| `frontend/panel-design/` | Fuentes visuales y generadores de iconos/plantillas. No es otro servidor frontend. |
| `demos/panel-editorial/` | Demostración estática con datos ficticios. No autentica ni conecta a Railway. |
| `docs/` y `DIAGRAMAS/` | Reglas, arquitectura, diagramas y guías. |
| `backend/` y `Dockerfile` raíz | API anterior conservada por compatibilidad. Usa otras migraciones y otra base. |

El servicio nuevo se despliega desde **backend-panel**, con su Dockerfile. La base autorizada es `little_paws_panel_v2`; no aplicar estas migraciones a las bases anteriores. El Dockerfile raíz sigue perteneciendo al servicio antiguo.

## Desarrollo local

Requisitos: Python 3.14, Git y una instancia MySQL autorizada. Desde la raíz:

```powershell
cd backend-panel
py -3.14 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-railway.txt
Copy-Item .env.example .env
```

Completar `.env` con claves y una base local propia, o recibir configuración privada del propietario. No hay credenciales en el repositorio y no se distribuyen en ZIP. Las claves de cifrado de bases existentes se conservan; no generar una diferente para datos ya cifrados.

```powershell
.venv/Scripts/python.exe manage.py check --database default
.venv/Scripts/python.exe -m uvicorn config.asgi:application --host 127.0.0.1 --port 8000 --reload
```

Abrir http://127.0.0.1:8000/panel/login/. Uvicorn ejecuta ASGI para sincronizar las sesiones; `--reload` solo se usa en desarrollo. Para crear una base local nueva, ejecutar `migrate` sobre esa base vacía y después `iniciar_seguridad --email TU_CORREO`; no inicializar datos demo en la base compartida.

## Railway y acceso del equipo

Para ejecutar Android en un emulador o celular, sigue la [guía de ejecución de la app](frontend/mobile/README.md). La [entrega de Semana 15](docs/entrega/semana-15-evolucion.md) registra deudas, responsables y trazabilidad.

La configuración privada del panel en Railway utiliza la base nueva, un usuario SQL limitado a ese esquema y almacenamiento privado persistente. Ver [despliegue](docs/entrega/railway.md). Cada persona entra con su cuenta del panel: el rol se asigna desde Django y se valida en el servidor. El color o el perfil de la demo no concede acceso.

[Actualizar las PCs del equipo](docs/entrega/actualizar-equipo.md) · [Auditoría final](docs/entrega/auditoria-final.md) · [Reglas de acceso](docs/rbac/01-definicion-de-accesos.md) · [Identidad visual](STYLE.md).

## Calidad

GitHub Actions comprueba configuración, ausencia de migraciones pendientes y pruebas en MySQL 8.4 aislado. Las pruebas no se ejecutan sobre la base de Railway. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para reproducirlas.

La suma del login se combina con límites de intentos, CSRF y sesión: no es una protección completa frente a DDoS. La administración de seguridad está implementada; algunos procesos operativos aún tienen API/listado y boceto, sin formulario web completo. Consulte la auditoría antes de prometer esas funciones.

## Idioma y accesibilidad

El panel ofrece español/inglés y preferencias de texto, contraste y movimiento desde el menú «Idioma y accesibilidad». Se conservan en el navegador y funcionan sin JavaScript. Ver [uso y mantenimiento](docs/diseno/idiomas-y-accesibilidad.md). Los nombres y datos de personas no se traducen automáticamente.


La revisión móvil más reciente sigue la referencia Stitch y conserva Flutter/Django. Incluye galería autorizada, red verificada, comunidad y ayudas por organización; no procesa pagos. Consulte [implementación y límites](docs/diseno/48-redisenio-integral-stitch.md). Los cambios permanecen locales hasta que el equipo revise e integre sus bloques.
