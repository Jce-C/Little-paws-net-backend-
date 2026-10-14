# Little Paws Net — backend

API de Little Paws Net desarrollada con Django 5.2, Django REST Framework y MySQL 8. La base de datos de demostración y el servidor público están alojados en Railway. Este repositorio no contiene un frontend.

## Abrir la copia en otro computador

Requisitos: Python 3.12, Git y acceso a Internet. En PowerShell, desde la carpeta clonada:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

El archivo `backend/.env` de esta demostración académica ya apunta a Railway con una cuenta SQL de lectura. No hay que instalar ni crear MySQL en el computador. El equipo entrega la contraseña de Django Admin por separado.

```powershell
python manage.py check --database default
python manage.py runserver
```

Abra [Django Admin local](http://127.0.0.1:8000/admin/) e inicie sesión con la cuenta temporal de evaluación. Los datos que aparecen proceden de Railway. `runserver` sirve solo para la demostración en el computador; no reemplaza el despliegue de Railway. No ejecute `migrate` ni `seed_demo_rescue` en esa copia: la base ya tiene tablas y más de 100 registros ficticios.

## Demostración publicada

- [Entrada de la API](https://little-paws-api-production.up.railway.app/)
- [Estado del servicio](https://little-paws-api-production.up.railway.app/api/health/)
- [Conteos de datos ficticios](https://little-paws-api-production.up.railway.app/api/demo/resumen/)
- [Catálogos](https://little-paws-api-production.up.railway.app/api/catalogos/)
- [Django Admin publicado](https://little-paws-api-production.up.railway.app/admin/)

## Idiomas

La API responde en español por defecto. En la mayoría de las rutas, el cliente cambia al inglés enviando `Accept-Language: en`; para volver al español, `Accept-Language: es`. Los mensajes cambian, pero las rutas y nombres de campos JSON permanecen estables. Para verlo rápidamente desde un navegador, abra [español](https://little-paws-api-production.up.railway.app/api/idiomas/?lang=es) e [inglés](https://little-paws-api-production.up.railway.app/api/idiomas/?lang=en). Véase [IDIOMAS.md](backend/IDIOMAS.md).

## Estructura

`backend/config/` contiene configuración y rutas generales. Las aplicaciones `accounts`, `core`, `rescue`, `animals`, `adoptions`, `funds` y `commerce` separan modelos, serializadores, servicios, vistas, URLs, migraciones y pruebas. El Admin sirve para consulta, carga supervisada de catálogos, usuarios y reportes; las transiciones delicadas siguen pasando por las APIs y servicios. Véase [ADMIN.md](backend/ADMIN.md).

## Comprobación automatizada

```powershell
python manage.py makemigrations --check --dry-run
python manage.py test --settings=config.test_settings
```

Las pruebas utilizan una base SQLite temporal y no modifican el MySQL de Railway. Las rutas completas se encuentran en [config/urls.py](backend/config/urls.py) y los `urls.py` de cada módulo.

## Despliegue

Railway construye la API con el `Dockerfile`: instala Python y dependencias, reúne los archivos estáticos del Admin y ejecuta Gunicorn. El profesor **no necesita Docker** para usar `runserver`. Las variables privadas de Railway configuran la instancia publicada, que ejecuta las migraciones antes de cada despliegue. La cuenta SQL pública de demostración se usa únicamente para la copia local de evaluación; `.dockerignore` evita incorporarla a la imagen desplegada.

Los registros son ficticios. Un acceso SQL publicado permite conexiones de terceros y no debe reutilizarse para datos reales. Tras la evaluación deben revocarse sus credenciales. Para colaboración y cambios, consulte [CONTRIBUTING.md](CONTRIBUTING.md).
