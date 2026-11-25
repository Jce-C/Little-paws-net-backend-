# Asignación abierta de perfiles RBAC

Fecha: 3 de noviembre de 2026.

## Problema y cambio

El catálogo contiene perfiles globales y de organización, pero la pantalla y el motor interpretaban esa clasificación como una lista cerrada de perfiles asignables. En Plataforma únicamente se podían seleccionar tres roles activos. Esto impedía usar un gestor como perfil general y obligaba a cambiar de contexto incluso para demostrar una concesión administrativa añadida a su matriz.

La asignación determina ahora el contexto. Cualquier perfil activo sin una organización propietaria puede asignarse de forma general o dentro de una organización. `Rol.ambito` conserva su clasificación original, pero no es una barrera para esa asignación central. No se cambia automáticamente la matriz de permisos de ningún rol.

El motor consume tanto las asignaciones generales como las locales sin descartar perfiles por su clasificación. La API de permisos efectivos deriva los roles del mismo motor, evitando que la interfaz anuncie permisos que no funcionen.

## Uso

1. Usuarios → persona → Roles.
2. Elegir **Asignación general** o una organización concreta.
3. Buscar y seleccionar uno o varios perfiles del catálogo completo.
4. Indicar el motivo y guardar. Descartar conserva la selección guardada.
5. Comprobar los accesos con la cuenta afectada. La sesión abierta recibe la actualización y el backend vuelve a comprobar permisos en cada operación.

No existe un límite fijo de tres roles ni una lista de códigos autorizados por la pantalla. La matriz permite añadir una vista administrativa a un perfil ciudadano o gestor y retirarla después.

Los roles inactivos pueden seleccionarse por una cuenta autorizada a restaurarlos. La fila advierte que al guardar se activarán también para asignaciones anteriores. El formulario envía esa activación explícita; la API requiere `activar_inactivos: true`. Se audita la activación, y todos los cambios se realizan dentro de la misma transacción. Los roles históricos ya no están bloqueados por su código al editar o reactivar desde la API.

## Distinciones que se conservan

- Una asignación general aporta sus permisos de organización en las organizaciones donde la persona es miembro vigente, no en equipos ajenos. Para futuras membresías también se aplicará el perfil general; para limitarlo a un solo equipo, usar la asignación local.
- Un rol propiedad de una organización específica se asigna dentro de esa organización. No se convierte en un perfil compartido entre organizaciones.
- Los permisos globales protegen recursos de plataforma; ponerlos en un perfil de equipo no convierte esos recursos globales en locales. La autoridad para concederlos se comprueba igualmente.
- Asignar el perfil «Responsable principal» concede las capacidades de su matriz; no reemplaza el registro de titularidad ni omite la aceptación del sucesor en una transferencia real. La pantalla lo explica junto al perfil. El responsable real conserva su designación y sus garantías.
- Una denegación individual prevalece y un usuario sin autoridad de administración no puede conceder capacidades superiores a las que administra.
- Un rol archivado mediante la baja administrativa debe restaurarse por su procedimiento; no se elude esa baja al seleccionar un rol inactivo. Las reactivaciones ordinarias y las restauraciones administrativas no son la misma operación.

Estas condiciones protegen datos y transiciones reales, en lugar de imponer una lista cerrada de roles de interfaz.

## Validación

- 232 pruebas Django pasaron en MySQL local aislado. Incluyen siete nuevas pruebas de asignación de todos los perfiles, capacidades reales, revocación en la misma sesión, activación autorizada y auditada, conservación de la titularidad, catálogo sin límite de tres y prevalencia de denegaciones individuales.
- Se actualizaron pruebas que exigían los bloqueos antiguos para reflejar la nueva regla, conservando pruebas de autorización y aislamiento entre organizaciones.
- Seis comprobaciones de navegador: catálogo completo, gestores y perfil principal seleccionables en asignación general, persistencia de cuatro perfiles, selección tras recargar, móvil sin desbordamiento y restauración de la selección local anterior.
- Cinco comprobaciones con dos sesiones: sin acceso inicial, actualización automática del menú, acceso real concedido, retirada automática y rechazo real tras revocación.
- No hay cambios de esquema ni migraciones nuevas. No se asignaron, activaron ni retiraron roles de cuentas reales durante las pruebas.

Evidencia local: `output/roles-abiertos-2026-11-03/`. No se crearon commits ni ramas.

## Publicación verificada

Railway, servicio exclusivo del panel v2: despliegue `382284ee-658d-4325-9e47-c5018466fd36`, estado SUCCESS. No se modificó el servicio antiguo ni el esquema.

Siete comprobaciones de producción pasaron: etiqueta Asignación general publicada, los 16 perfiles del catálogo actual seleccionables para la administración, gestores y perfil principal disponibles, Carlitos conserva únicamente Ciudadano como asignación general, avisos de activación de los tres perfiles inactivos, móvil sin desbordamiento y API de asignaciones vigente. La verificación fue de lectura; no se guardaron cambios de roles reales. La sesión temporal de revisión se cerró al terminar.

Comprobación preventiva en la base: no existían asignaciones generales o locales activas ocultas por los filtros retirados, por lo que la publicación no amplió permisos mediante antiguas asignaciones ignoradas. Las siete pruebas específicas se repitieron sobre el código final y pasaron.
