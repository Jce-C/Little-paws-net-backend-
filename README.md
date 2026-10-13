# Little Paws Net — API

Backend de Little Paws Net, una plataforma para gestionar reportes y rescates de animales, expedientes médicos, adopciones, apadrinamientos, fondos externos y el catálogo de tiendas aliadas. Está construido con Django y Django REST Framework sobre MySQL. Este repositorio contiene la API; no incluye una interfaz web o móvil.

## Funcionalidades

- Registro de usuarios y autenticación mediante JWT.
- Reportes georreferenciados, asignación de casos a fundaciones y seguimiento de estados.
- Custodia de mascotas, autorización de veterinarios y acceso controlado al expediente mediante QR.
- Solicitudes de adopción con resolución e historial.
- Compromisos de apadrinamiento y donación, y registro de distribuciones de fondos externos.
- Productos de tiendas aliadas, pedidos iniciados, espacios publicitarios y tarifas de publicación.
- Control de acceso por roles y pertenencia a entidades, con validaciones y trazabilidad en los procesos principales.
- Respuestas en español e inglés según el encabezado `Accept-Language`. Véase [IDIOMAS.md](backend/IDIOMAS.md).

Los pedidos no procesan pagos ni reservan inventario. Los compromisos y distribuciones de fondos registran información del sistema; no ejecutan transferencias bancarias.

## Requisitos

- Python y las dependencias fijadas en [requirements.txt](backend/requirements.txt).
- MySQL 8 con una base de datos vacía y una cuenta con permisos sobre esa base.
- Una clave Fernet local para proteger los datos sensibles utilizados por la aplicación.

## Inicio rápido en Windows (PowerShell)

Desde la raíz del repositorio:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar `backend/.env` con los datos de la base MySQL y claves propias. Para generar las claves sin compartirlas:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Asignar los resultados a `DJANGO_SECRET_KEY` y `LPN_DATA_KEY`, respectivamente. La segunda clave debe conservarse para poder descifrar datos ya almacenados. No subir `.env` a Git.

Una vez configurada la conexión:

```powershell
python manage.py migrate
python manage.py check --database default
python manage.py runserver
```

El servidor de desarrollo queda disponible en `http://127.0.0.1:8000/`. `runserver` es solo para desarrollo local.

## API e idiomas

Todas las rutas funcionales comienzan con `/api/`. Algunos puntos de entrada son:

| Proceso | Rutas de ejemplo |
| --- | --- |
| Acceso | `/api/auth/registro/`, `/api/auth/token/`, `/api/auth/perfil/` |
| Rescate y expediente | `/api/reportes/`, `/api/casos/{id}/`, `/api/expedientes/{id}/consultar/` |
| Adopción y fondo | `/api/adopciones/`, `/api/fondos/`, `/api/donaciones/`, `/api/distribuciones/` |
| Comercio | `/api/productos/`, `/api/pedidos/`, `/api/publicidad/`, `/api/tarifas/` |
| Referencia | `/api/catalogos/`, `/api/idiomas/`, `/api/health/` |

La mayoría de operaciones privadas requieren `Authorization: Bearer <token>`. El cliente puede solicitar inglés con `Accept-Language: en` o español con `Accept-Language: es`; los nombres de rutas y campos JSON no cambian. Las rutas completas están definidas en [config/urls.py](backend/config/urls.py) y en los archivos `urls.py` de cada módulo.

## Verificación

Desde `backend/` y con el entorno virtual activo:

```powershell
python manage.py check --database default
python manage.py makemigrations --check --dry-run
python manage.py test --settings=config.test_settings
```

La suite automatizada utiliza SQLite en memoria y no modifica MySQL. Para verificar el flujo de rescate, apadrinamiento y expediente sobre MySQL existe `python manage.py smoke_rescue`; sus registros temporales se revierten. Este comando solo admite la base local `little_paws_net_equipo`.

Se pueden cargar registros ficticios e idempotentes del proceso de rescate con `python manage.py seed_demo_rescue`. Este comando también está limitado a `little_paws_net_equipo`; no debe utilizarse en producción ni con datos personales reales.

## Seguridad y despliegue

Las credenciales y claves se configuran fuera del repositorio. Antes de desplegar se deben revisar HTTPS, hosts permitidos, cookies seguras, gestión de secretos y `python manage.py check --deploy`. La configuración incluida está orientada al desarrollo y la validación del proyecto, no a una instalación de producción lista para exponer públicamente.

Para colaborar, consultar [CONTRIBUTING.md](CONTRIBUTING.md).
