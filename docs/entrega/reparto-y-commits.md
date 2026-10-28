# Entrega del panel · repositorio oficial y ramas

Repositorio: https://github.com/Jce-C/Little-paws-net-backend- (el guion final forma parte del nombre).
Base verificada: `016415b3a70ccf6173dd2d39cf284b6c898fa305`, rama `main` consultada el 27 de octubre de 2026.
Estos paquetes sustituyen a los ZIP anteriores, que tenían una base incompatible.
No se hicieron commits, pushes ni cambios en GitHub durante su preparación.

## Estructura de la integración

- `backend/`, `Dockerfile` y `DIAGRAMAS/`: aplicación anterior; se conservan.
- `backend-panel/`: versión nueva de Django, sus API, RBAC y panel, para la base `little_paws_panel_v2` ya creada.
- `frontend/panel-design/`: fuentes y generadores de la presentación.
- `demos/panel-editorial/`: recorrido ficticio de diseño, separado de la autenticación real.
- `docs/`: decisiones, auditoría e instrucciones.

Es una transición con dos servicios, no dos autorizaciones sobre la misma base.
No mezclar modelos/migraciones ni apuntar `backend-panel/` a las bases anteriores.
No sustituir el Dockerfile raíz de la API publicada. El futuro servicio del panel
utilizará `backend-panel/` como raíz y su propio Dockerfile. Consolidar los servicios
requiere una migración posterior explícita.

## Orden obligatorio

Rama de integración: **`entrega-panel`**. Las ramas remotas aún no se han publicado.

| Orden | Persona | Rama personal | Parche | Commit sugerido |
| --- | --- | --- | --- | --- |
| 01 | Tú, con revisión del asistente | `dominio-rbac` | `01-dominio-rbac.patch` | `feat(seguridad): incorporar roles permisos y flujos con alcance` |
| 02 | Sally | `sally-panel-web` | `02-panel-web.patch` | `feat(panel): agregar acceso web y administracion por permisos` |
| 03 | Majo | `majo-identidad` | `03-identidad-visual.patch` | `feat(diseno): incorporar identidad visual y temas por perfil` |
| 04 | Tú, con revisión del asistente | `integracion-api` | `04-integracion-api.patch` | `feat(api): incorporar backend del panel y configuracion independiente` |
| 05 | Sally | `sally-demo` | `05-demo-animada.patch` | `feat(demo): agregar recorrido visual del panel y acceso animado` |
| 06 | Majo | `majo-documentacion` | `06-documentacion.patch` | `docs(entrega): documentar alcance validacion y despliegue pendiente` |

Integrar un bloque antes de comenzar el siguiente. Las cuatro primeras piezas
forman juntas el servicio nuevo: no desplegar ni ejecutar migraciones a mitad.
Cada persona revisa y entiende su implementación antes de registrar su commit.

## Preparación en GitHub

Cada integrante usa su propia cuenta. El propietario invita a Sally y Majo desde
Settings → Collaborators → Add people del repositorio correcto. Ellas aceptan.
No compartir contraseñas, tokens o claves SQL. Tener acceso a GitHub no otorga
un rol dentro de Little Paws Net.

## Primer bloque: propietario

El asistente preparará el bloque 01 en la copia de integración cuando el propietario
autorice expresamente empezar a crear commits. No se aplican los parches en la
carpeta de trabajo que ya contiene todos los cambios.

En una copia limpia del repositorio correcto, se parte de la base verificada:

```powershell
git clone -c core.autocrlf=false https://github.com/Jce-C/Little-paws-net-backend-.git Little-paws-net-entrega
cd Little-paws-net-entrega
git switch -c entrega-panel 016415b3a70ccf6173dd2d39cf284b6c898fa305
git switch -c dominio-rbac
```

Se revisa y registra el bloque 01 en `dominio-rbac`, se integra en `entrega-panel`
y se publica esa rama. Solo entonces puede comenzar Sally. No cambiar la rama
principal ni configurar publicación automática de una integración incompleta.

## Ejemplo completo: Sally, bloque 02

Ejecutar solamente después de que el bloque 01 esté integrado y la rama remota
`entrega-panel` exista. Extraer el ZIP nuevo de Sally fuera del repositorio.
La carpeta `archivos/` es una referencia; el parche es el mecanismo de aplicación.

```powershell
git clone -c core.autocrlf=false https://github.com/Jce-C/Little-paws-net-backend-.git Little-paws-net-entrega
cd Little-paws-net-entrega
git fetch origin
git switch -c sally-panel-web origin/entrega-panel
git config user.name "Nombre de Sally"
git config user.email "CORREO_DE_SALLY_EN_GITHUB"
$parche = "C:/RUTA/PAQUETE_SALLY/02-panel-web.patch"
git apply --check --index "$parche"
git apply --index "$parche"
git diff --cached --stat
git diff --cached
```

Si `apply --check` falla, detenerse y compartir el error. No forzar la aplicación,
no eliminar cambios propios y no copiar todo el ZIP encima de otra versión.
Si el diff es el esperado y Sally ha revisado su aporte:

```powershell
git commit -m "feat(panel): agregar acceso web y administracion por permisos"
git push -u origin sally-panel-web
```

En GitHub abrir Pull Request: **base `entrega-panel`, compare `sally-panel-web`**.
El propietario comparte aquí el enlace y espera la revisión antes de integrarlo.
Si hay correcciones, Sally las incorpora en su rama y vuelve a hacer push al mismo PR.

## Majo y las siguientes rondas

Majo repite el procedimiento con su propio nombre/correo, rama `majo-identidad`,
parche 03 y título de commit de la tabla. Después siguen 04, 05 y 06.
En las rondas siguientes no hace falta clonar otra vez: con el trabajo anterior
ya guardado y la carpeta limpia, cada persona obtiene la integración actualizada
y crea una rama nueva. Ejemplo de Sally para el bloque 05:

```powershell
git fetch origin
git switch -c sally-demo origin/entrega-panel
```

Aplicar solo el parche que corresponda. No crear la ronda siguiente a partir de
una rama personal vieja. Todos los PR se dirigen a `entrega-panel`.

## Validación y usuarios de la aplicación

El panel nuevo está en `backend-panel/`. Sus pruebas deben usar MySQL aislado,
no la base de Railway de uso compartido. La revisión de esta copia ejecuta
`check`, comprobación de migraciones y las 110 pruebas actuales.
La imagen de producción necesita validación Linux y configuración de volumen/secretos
antes del despliegue. No publicar como producto completamente terminado por tener
los formularios administrativos; varios formularios operativos siguen pendientes.

El propietario configura `backend-panel/.env.railway` de forma privada; no está
incluido en los ZIP. En su equipo instala Python 3.14 y prepara el entorno:

```powershell
py -3.14 -m venv backend-panel/.venv
backend-panel/.venv/Scripts/python.exe -m pip install -r backend-panel/requirements.txt
```

Una vez configurado el archivo privado, comprueba conexión e inicializa su cuenta:

```powershell
./backend-panel/panel_railway.ps1 -Accion check
./backend-panel/panel_railway.ps1 -Accion iniciar_seguridad -Email TU_CORREO -Nombre "Tu nombre"
./backend-panel/panel_railway.ps1 -Accion runserver
```

El comando inicializa solo al primer administrador y pide la contraseña oculta.
Si ese administrador ya se creó usando esta base desde la copia de trabajo anterior,
no repetir el alta: usar la misma cuenta. No se crean administradores diferentes
por cambiar de carpeta o repositorio.

En http://127.0.0.1:8000/panel/login/ entrar con esa cuenta. Abrir Usuarios → Nuevo
usuario, completar nombre/correo/contraseña inicial y Cuenta activa; repetir para
Sally y Majo. Después asignarles un rol desde el botón Roles de su fila.
No necesitan usuarios SQL ni acceso de administración a Railway para hacer commits.

Para consulta del diseño, crear un rol `CONSULTA_DISENO`, nombre Consulta de diseño,
ámbito GLOBAL, Delegable desmarcado y Activo marcado. Asignar `roles.ver`,
`recursos.ver` y `permisos.ver`. Luego asignar ese rol a ambas cuentas. No darles
Administrador de seguridad solo por participar en el frontend. Otros perfiles de
prueba se asignan según el alcance acordado y se revocan cuando dejan de ser necesarios.

Los ZIP incluyen inventarios y parches, sin credenciales nuevas ni entornos locales.
La validación reconstruye la base oficial y aplica los seis parches sin commits,
comprobando hashes y que `backend/`, `Dockerfile` y `DIAGRAMAS/` no se modifican.
El `.env` de evaluación ya publicado en la historia anterior no se reenvía en
los paquetes; debe revocarse por separado, no reutilizarse en este panel.
