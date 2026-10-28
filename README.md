# Little Paws Net

Panel de gestión y API de una red de protección y adopción de mascotas. Django 5.2, Django REST Framework y MySQL 8; interfaz web con plantillas Django, CSS y JavaScript locales.

## Qué ejecutar

| Carpeta | Responsabilidad |
| --- | --- |
| `backend-panel/` | Aplicación vigente: login, usuarios, roles, recursos, permisos y auditoría; dominio y API V2. |
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
.venv/Scripts/python.exe manage.py runserver
```

Abrir http://127.0.0.1:8000/panel/login/. `runserver` solo sirve para desarrollo. Para crear una base local nueva, ejecutar `migrate` sobre esa base vacía y después `iniciar_seguridad --email TU_CORREO`; no inicializar datos demo en la base compartida.

## Railway y acceso del equipo

La configuración privada del panel en Railway utiliza la base nueva, un usuario SQL limitado a ese esquema y almacenamiento privado persistente. Ver [despliegue](docs/entrega/railway.md). Cada persona entra con su cuenta del panel: el rol se asigna desde Django y se valida en el servidor. El color o el perfil de la demo no concede acceso.

[Actualizar las PCs del equipo](docs/entrega/actualizar-equipo.md) · [Auditoría final](docs/entrega/auditoria-final.md) · [Reglas de acceso](docs/rbac/01-definicion-de-accesos.md) · [Identidad visual](STYLE.md).

## Calidad

GitHub Actions comprueba configuración, ausencia de migraciones pendientes y pruebas en MySQL 8.4 aislado. Las pruebas no se ejecutan sobre la base de Railway. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para reproducirlas.

La suma del login se combina con límites de intentos, CSRF y sesión: no es una protección completa frente a DDoS. La administración de seguridad está implementada; algunos procesos operativos aún tienen API/listado y boceto, sin formulario web completo. Consulte la auditoría antes de prometer esas funciones.

## Idioma y accesibilidad

El panel ofrece español/inglés y preferencias de texto, contraste y movimiento desde el menú «Idioma y accesibilidad». Se conservan en el navegador y funcionan sin JavaScript. Ver [uso y mantenimiento](docs/diseno/idiomas-y-accesibilidad.md). Los nombres y datos de personas no se traducen automáticamente.
