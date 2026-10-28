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

El archivo `backend/.env` de esta demostración académica ya apunta a una **copia de evaluación en Railway** con una cuenta SQL que permite trabajar desde Django Admin. No hay que instalar ni crear MySQL en el computador. El equipo entrega la contraseña de Django Admin por separado.

```powershell
python manage.py check --database default
python manage.py runserver
```

Abra [Django Admin local](http://127.0.0.1:8000/admin/) e inicie sesión con la cuenta temporal de evaluación. Podrá consultar, añadir y editar los recursos que el Admin permite, con las restricciones de cada proceso. Los datos iniciales proceden de Railway. `runserver` sirve solo para la demostración en el computador; no reemplaza el despliegue de Railway. No ejecute `migrate` ni `seed_demo_rescue` al abrir la copia: la base ya tiene tablas y más de 100 registros ficticios.

## Demostración publicada

- [Entrada de la API](https://little-paws-api-production.up.railway.app/)
- [Estado del servicio](https://little-paws-api-production.up.railway.app/api/health/)
- [Conteos de datos ficticios](https://little-paws-api-production.up.railway.app/api/demo/resumen/)
- [Catálogos](https://little-paws-api-production.up.railway.app/api/catalogos/)
- [Django Admin publicado](https://little-paws-api-production.up.railway.app/admin/)

## Idiomas

La API responde en español por defecto. En la mayoría de las rutas, el cliente cambia al inglés enviando `Accept-Language: en`; para volver al español, `Accept-Language: es`. Los mensajes cambian, pero las rutas y nombres de campos JSON permanecen estables. Para verlo rápidamente desde un navegador, abra [español](https://little-paws-api-production.up.railway.app/api/idiomas/?lang=es) e [inglés](https://little-paws-api-production.up.railway.app/api/idiomas/?lang=en). El propio Django Admin adapta sus textos estándar al idioma preferido del navegador; los nombres propios del modelo permanecen en español. Véase [IDIOMAS.md](backend/IDIOMAS.md).

## Estructura

`backend/config/` contiene configuración y rutas generales. Las aplicaciones `accounts`, `core`, `rescue`, `animals`, `adoptions`, `funds` y `commerce` separan modelos, serializadores, servicios, vistas, URLs, migraciones y pruebas. El Admin sirve para consulta, carga supervisada de catálogos, usuarios y reportes; las transiciones delicadas siguen pasando por las APIs y servicios. Véase [ADMIN.md](backend/ADMIN.md).

## Comprobación automatizada

```powershell
python manage.py makemigrations --check --dry-run
python manage.py test --settings=config.test_settings
```

Las pruebas utilizan una base SQLite temporal y no modifican el MySQL de Railway. Las rutas completas se encuentran en [config/urls.py](backend/config/urls.py) y los `urls.py` de cada módulo.

## Despliegue

Railway construye la API con el `Dockerfile`: instala Python y dependencias, reúne los archivos estáticos del Admin y ejecuta Gunicorn. El profesor **no necesita Docker** para usar `runserver`. Las variables privadas de Railway configuran la instancia publicada sobre `little_paws_net_demo`. El `.env` público conecta la copia descargada a `little_paws_net_eval`, una base separada con los mismos datos iniciales; los cambios del profesor no aparecerán en la API publicada. `.dockerignore` evita incorporar ese `.env` a la imagen desplegada.

Los registros son ficticios. Un acceso SQL publicado permite conexiones de terceros y no debe reutilizarse para datos reales. Tras la evaluación deben revocarse sus credenciales. Para colaboración y cambios, consulte [CONTRIBUTING.md](CONTRIBUTING.md).


## Panel web y backend V2 en este repositorio

El repositorio oficial es https://github.com/Jce-C/Little-paws-net-backend- (con guion final).
La versión nueva se incorpora temporalmente en `backend-panel/`, con su propio historial
de migraciones y el esquema Railway `little_paws_panel_v2`. `backend/` y el Dockerfile
de la demostración anterior permanecen intactos. Son dos servicios durante la transición;
no comparten autorización ni se deben conectar al mismo esquema. Consolidar el backend
queda para una migración posterior explícita, no para una copia de archivos entre ambos.

La rama de integración prevista es `entrega-panel`. Seguir
[el reparto y las instrucciones](docs/entrega/reparto-y-commits.md).
El panel nuevo requiere Python 3.14, sus dependencias y variables privadas propias.
La apariencia de bienvenida ya usa el formulario auténtico de Django, no el acceso
ficticio de la demo. `demos/panel-editorial/` conserva la referencia visual aislada.

Las credenciales de evaluación publicadas por la versión anterior no se reutilizan
para el panel nuevo. Que permanezcan en el historial anterior no las convierte en
seguras; su revocación es un trabajo independiente pendiente.
