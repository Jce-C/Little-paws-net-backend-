# Etapa 2 — Implementación Django, bloque 1

Fecha: 2026-10-26. Referencia funcional: `01-definicion-de-accesos.md` y `02-matriz-resumen.md`.

**Documento histórico del primer bloque.** Los pendientes indicados al final fueron abordados en la ampliación posterior; consultar [cierre funcional de la etapa 2](06-cierre-etapa-2.md) para el estado actual y [guía de archivos](05-guia-archivos-y-tecnologias.md) para la explicación técnica.

## 1. Qué está implementado

El backend dispone de una API de administración y un motor de autorización. Todavía no es el panel visual ni el login web con captcha: corresponden a los bloques posteriores.

1. **Catálogo y roles.** `Recurso` identifica el módulo; `Permiso` identifica una acción y un alcance; `RolPermiso` relaciona roles y permisos. Las asignaciones globales y de entidad conservan su historial de revocación. Se cargan 13 roles del sistema y 18 recursos. Los códigos de operación reconocidos proceden de `seguridad/politicas.py`; crear un nombre en la base no crea una función ejecutable.
2. **Administración.** Usuarios, roles, recursos y permisos admiten consulta paginada, creación y actualización parcial. Las bajas son lógicas. No se permite borrar estos registros por la API, cambiar los indicadores técnicos del usuario ni retirar al último Administrador de seguridad activo. Los roles estructurales conservan sus permisos esenciales.
3. **Ámbitos.** Cada petición comprueba cuenta activa, rol vigente, recurso, permiso y contexto. Una membresía de una entidad no concede acceso a otra. Un JWT todavía válido no conserva un rol revocado. `is_staff` e `is_superuser` no sustituyen un rol de negocio.
4. **Responsables.** Una fila única identifica al principal de cada entidad. Los responsables secundarios administran miembros y cargos delegables. El principal no se otorga como un cargo ordinario ni se elimina mediante una baja de miembro o usuario. La primera designación y la recuperación administrativa son operaciones específicas; la recuperación exige motivo y cancela transferencias pendientes.
5. **Transferencia.** La inicia el principal hacia otro responsable vigente de la misma entidad. El saliente conserva el cargo hasta la aceptación del sucesor. `mantener_secundario` vale `false` por defecto. Al aceptar se respeta esa opción y se conservan los otros cargos operativos del saliente. Los participantes pueden cancelar una transferencia pendiente.
6. **Asignaciones.** Las solicitudes de adopción, aportes, pedidos y verificaciones pueden tomarse desde colas mínimas. La entidad se deriva del registro real, no del cuerpo enviado por el cliente. La toma es exclusiva y transaccional; la devolución requiere motivo y retira el acceso. Las colas solo entregan identificadores. No se permite tomar la propia solicitud de adopción o verificación. Los fondos permiten varios gestores, designados por responsables de su entidad.
7. **Trazabilidad.** `EventoSeguridad` registra operaciones administrativas, cambios de responsabilidad y asignaciones. Guarda metadatos explícitos, sin copiar contraseñas, datos bancarios ni el cuerpo completo de las peticiones. Su API es de consulta autorizada.

### Roles cargados

| Ámbito | Roles |
| --- | --- |
| Global | Administrador de seguridad, Moderador, Ciudadano |
| Entidad | Responsable principal, Responsable secundario |
| Operación en una entidad | Gestor de rescates, adopciones, aportes, catálogo, pedidos, fondo y publicidad; Veterinario |

El registro público asigna solamente Ciudadano. Ninguna migración convierte automáticamente una cuenta en administradora. Los roles amplios antiguos `ADMIN_PLATAFORMA`, `GESTOR_FUNDACION` y `GESTOR_TIENDA` quedan deshabilitados; se conservan sus asignaciones históricas. Las plantillas no sustituyen las condiciones de cada objeto y algunas operaciones declaradas aún requieren sus endpoints de negocio.

## 2. Dónde está y cómo funciona

| Archivo o módulo | Responsabilidad |
| --- | --- |
| `backend-panel/core/models.py` | Recurso y ampliación de roles, permisos y revocaciones |
| `backend-panel/seguridad/politicas.py` | Catálogo de operaciones y plantillas de roles |
| `backend-panel/seguridad/autorizacion.py` | `puede`, `tiene_base` y `exigir`; evaluación actual contra la base |
| `backend-panel/seguridad/objetos.py` | Resolución del objeto, su entidad y sus condiciones para asignación |
| `backend-panel/seguridad/models.py` | Responsables, transferencias, asignaciones y auditoría |
| `backend-panel/seguridad/servicios.py` | Transacciones, delegación, revocación y bloqueos |
| `backend-panel/seguridad/serializers.py` | Campos admitidos; rechazo de campos ajenos y cambios de alcance |
| `backend-panel/seguridad/views.py`, `urls.py` | API que consumirá el panel |
| `backend-panel/seguridad/tests.py` | Pruebas de autorización, API, negocio y concurrencia |

Ejemplo: para resolver una adopción no basta con tener Gestor de adopciones. Se exige membresía y rol vigentes en la entidad custodiante, asignación individual a la solicitud y cumplimiento de las reglas del servicio de adopción. El responsable principal tampoco hereda automáticamente los cargos operativos.

### Integraciones con el negocio existente

- Aceptación y detalle de rescates: permisos del gestor en su fundación; el reportante conserva la consulta de su caso.
- Resolución de adopciones y confirmación de aportes: permiso y asignación individual.
- Registro de distribuciones: permiso y asignación al fondo concreto.
- Escritura veterinaria: profesional verificado, rol vigente y autorización específica y no vencida para la mascota.
- La ruta antigua de publicación directa de cuentas receptoras devuelve `409`: se cerró esa vía hasta implementar propuesta y aprobación por personas diferentes.
- `seed_demo` utiliza los roles separados y las asignaciones necesarias. Se niega a reactivar cuentas demo previamente deshabilitadas. No ejecutarlo para recuperar acceso al panel.

## 3. Contrato de API del bloque

Prefijo: `/api/seguridad/`. Autenticación actual: `Authorization: Bearer <access_token>` obtenido en `/api/auth/token/`. Todas las operaciones privadas comprueban además sus permisos; el token por sí solo no autoriza.

| Método y ruta relativa | Uso |
| --- | --- |
| `GET/POST usuarios/`, `GET/PATCH usuarios/{id}/` | Administración de cuentas |
| `GET/POST roles/`, `GET/PATCH roles/{id}/` | Roles y baja lógica |
| `GET/POST recursos/`, `GET/PATCH recursos/{id}/` | Catálogo de recursos |
| `GET/POST permisos/`, `GET/PATCH permisos/{id}/` | Acciones reconocidas; metadatos de alcance protegidos |
| `GET/POST roles/{id}/permisos/` | Consulta o reemplazo validado de la matriz del rol |
| `GET mis-accesos/` | Roles y permisos potenciales separados por ámbito |
| `POST comprobar/` | Evalúa un permiso del usuario autenticado para un contexto |
| `POST usuarios/{id}/roles-globales/` | Asignación o revocación global |
| `GET entidades/` | Consulta para administración de seguridad |
| `GET/POST entidades/{id}/miembros/` | Equipo y altas/bajas de miembros |
| `POST entidades/{id}/roles/` | Asignación o revocación de cargos delegables |
| `POST entidades/{id}/principal/` | Primera designación o recuperación con motivo |
| `GET/POST entidades/{id}/transferencias/` | Consulta de participantes e inicio |
| `POST transferencias/{id}/resolver/` | Aceptación o cancelación |
| `GET colas/{recurso}/?entidad_id={id}` | Trabajo disponible sin datos privados; verificación no necesita entidad |
| `POST asignaciones/{recurso}/{id}/tomar/` | Toma por la persona autenticada; cuerpo vacío |
| `POST asignaciones/{recurso}/{id}/devolver/` | Devolución con motivo |
| `POST fondos/{id}/asignar/` | Asignar o revocar un gestor del fondo |
| `GET auditoria/` | Historial paginado para seguridad |

Ejemplos de cuerpos, con identificadores ficticios:

```json
{"permiso": "adopcion.resolver", "objeto_id": 42}
```

```json
{"sucesor_id": 8, "mantener_secundario": false}
```

`sucesor_id` es el identificador de **EntidadMiembro**, no el de Usuario. La aceptación se envía al identificador de la transferencia:

```json
{"aceptar": true}
```

Asignación de un cargo de entidad:

```json
{"miembro_id": 8, "rol_id": 12, "revocar": false}
```

Los permisos devueltos por `mis-accesos/` sirven para preparar la navegación; `ASIGNADO` y `AUTORIZADO` requieren comprobar el objeto concreto. `comprobar/` no reemplaza la validación final del servicio ni modifica accesos.

## 4. Migraciones y primer acceso

Desde `backend`, en PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py iniciar_seguridad --email TU_CORREO --nombre "Tu nombre"
```

El último comando es una inicialización explícita para el propietario del entorno. Pide una contraseña oculta si la cuenta no existe, valida su fortaleza y no la imprime ni la recibe como argumento. Se niega a reactivar cuentas deshabilitadas y a añadir otro administrador si ya hay uno activo. Las altas administrativas posteriores se hacen mediante la API autorizada.

Migraciones nuevas: `core.0007` y `seguridad.0001` a `0003`. La migración de catálogo conserva una copia fija de las políticas en `_catalogo_v1.py`, para que migraciones futuras no dependan de cambios en el código de ejecución.

En este equipo se aplicaron las cuatro migraciones. Antes y después se verificaron 20 usuarios y **0 activos**. No se ejecutó la inicialización de una cuenta administradora ni se asignó el cargo a una cuenta demo.

## 5. Validación ejecutada

- `manage.py check`: sin incidencias.
- `manage.py makemigrations --check --dry-run`: sin cambios pendientes de modelo.
- **56 pruebas aprobadas** de `seguridad`, `accounts.tests` y `config.tests`, con las migraciones completas, en una instancia local independiente de MySQL 8.0.46.
- Incluyen aislamiento entre entidades; revocación con JWT vigente; campos de escalamiento; último administrador; transferencia con ambas opciones; devolución y limpieza de asignaciones; varios gestores por fondo; autorización del servicio real de adopción; y dos hilos compitiendo por la misma verificación.
- Una prueba ejecuta `seed_demo` dos veces y luego `verify_demo` sobre datos sintéticos de esa instancia independiente. No se cargaron esos usuarios ni se ejecutó esa verificación mutante sobre la base habitual.

Para reproducir la suite, preparar una **instancia MySQL independiente** en otro puerto local y establecer `LPN_TEST_MYSQL_HOST=127.0.0.1`, `LPN_TEST_MYSQL_PORT`, `LPN_TEST_MYSQL_USER` y `LPN_TEST_MYSQL_PASSWORD` en el entorno. La cuenta de pruebas necesita crear y borrar su esquema de pruebas. Después:

```powershell
.\.venv\Scripts\python.exe manage.py test seguridad accounts.tests config.tests --settings=config.settings_test_mysql --noinput
```

La configuración exige otro puerto y usa los esquemas `lpn_rbac_sandbox` y `test_lpn_rbac_sandbox`. No usar la cuenta ni la base habitual de la aplicación como entorno de pruebas.

## 6. Qué sigue pendiente de la etapa 2

Este bloque establece la estructura administrativa y protege los servicios mencionados. **No completa toda la etapa 2 ni constituye una auditoría integral de seguridad.** Faltan, siguiendo las decisiones aprobadas:

1. Propuesta y aprobación separadas para cuentas receptoras, con historial y prohibición de autoaprobación.
2. Acceso excepcional a registros concretos, solo lectura, con autoridad aprobadora, expiración de máximo 24 horas y revocación.
3. Subida y descarga privada de documentos y soportes; detalle y resolución de verificaciones y reclamaciones de mascotas con los límites acordados.
4. Enmiendas clínicas que conserven el original y el resto de transiciones clínicas aprobadas.
5. Versiones y revisión de publicidad, estados y transiciones restantes de pedidos, catálogo, rescates y solicitudes. Tener un código en la matriz no significa que estos endpoints existan.
6. Completar pruebas de esos flujos y sus interacciones concurrentes antes de declarar terminada la etapa.

Después se conectará el login web de la etapa 3, con protección CSRF si utiliza sesiones. El captcha de suma es una comprobación básica de automatización y necesita límites de intentos; no protege por sí solo contra DDoS. En la etapa 4 se diseñará el panel propio en Figma. Django Admin puede conservarse como herramienta técnica independiente; el panel de negocio consumirá esta API y sus permisos.
