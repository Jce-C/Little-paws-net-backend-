# Little Paws Net — backend colaborativo

Backend Django REST Framework sobre una **base MySQL nueva**. Este repositorio se construye por funcionalidades mediante commits reales de José Carlos, María José y Sally Andrea. El repositorio anterior sirve solo como referencia; no se reutiliza su historial ni su base de datos.

## Estado

Incluye la estructura Django, configuración local segura, autenticación por correo/contraseña con JWT, catálogos, reportes, rescate, apadrinamiento y expediente médico. Los módulos de adopción, fondo externo y comercio siguen pendientes de los commits de María José y Sally Andrea.

## Desarrollo local

En `backend/`, crear un entorno virtual e instalar `requirements.txt`. Copiar `.env.example` a `.env` y asignar claves propias; `.env` está excluido de Git. Crear una base MySQL 8 vacía por integrante y ejecutar `python manage.py migrate` desde `backend/`. El usuario MySQL de desarrollo requiere permisos sobre **esa base únicamente**. No apuntar al esquema anterior `little_paws_net_v2`.

`LPN_DATA_KEY` es una clave Fernet local para cifrar datos bancarios. Generar una distinta por instalación con `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` y copiarla a `.env`. No cambiarla después de almacenar datos cifrados sin plan de rotación; no publicarla.

Verificación del backend:

```powershell
python manage.py check --database default
python manage.py migrate
python manage.py test --settings=config.test_settings
python manage.py smoke_rescue
python manage.py seed_demo_rescue
```

Las pruebas automatizadas usan SQLite temporal y no alteran MySQL. `smoke_rescue` verifica en MySQL cobertura espacial, aceptación, cupos, apadrinamiento y expediente; sus filas de prueba se revierten.
`seed_demo_rescue` carga 25 reportes ficticios y sus relaciones (más de 100 registros del proceso); se puede repetir sin duplicarlos. Solo admite el esquema local `little_paws_net_equipo` y usa correos `.invalid`, nunca datos personales reales.

## Rutas principales

- `POST /api/auth/registro/`, `POST /api/auth/token/`, `GET /api/auth/perfil/`.
- `GET /api/catalogos/`; `POST /api/reportes/`; `GET /api/reportes/{id}/`; `POST /api/reportes/{id}/aceptar/`.
- `GET /api/casos/{id}/`; `POST /api/casos/{id}/cerrar/`; `POST /api/casos/{id}/mascota/`; `POST /api/casos/{id}/custodia/`.
- `POST /api/apadrinamientos/`; `POST /api/apadrinamientos/{id}/declaraciones/`; `POST /api/apadrinamientos/{id}/confirmaciones/`.
- `POST /api/expedientes/{id}/autorizaciones/`; `POST /api/expedientes/{id}/qr/`; `POST /api/expedientes/{id}/consultar/`; `POST /api/expedientes/{id}/registros/`.

Los endpoints de escritura requieren la cuenta, el rol y la pertenencia a la entidad que correspondan. El QR nunca sustituye la verificación profesional ni la autorización vigente. Los compromisos y declaraciones no equivalen a dinero recibido: únicamente la fundación puede confirmar el aporte.

Las responsabilidades y reglas de colaboración están en [CONTRIBUTING.md](CONTRIBUTING.md).
