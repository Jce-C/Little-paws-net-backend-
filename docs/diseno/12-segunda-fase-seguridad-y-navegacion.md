# Segunda fase: navegación, auditoría y administración segura

Actualización del 30 de octubre de 2026. Panel Django existente; no se sustituyeron autenticación, motor RBAC ni servicios de adopción, custodia, aportes o pedidos. No se crearon commits ni ramas en el repositorio oficial.

## Navegación y presentación

Seguridad contiene Usuarios, Roles y recursos y Auditoría, filtrados por acceso efectivo. Roles y recursos reúne cuatro tarjetas horizontales: Roles, Recursos, Permisos y Roles por persona. Las excepciones individuales permanecen dentro de la asignación de personas. Las categorías del lateral son desplegables, con sangría, contadores y una barra de iconos al contraerse.

El contador superior suma entradas autorizadas del lateral: excluye Mi espacio y Configuración, situada en la cabecera. Roles y recursos cuenta como una entrada; su insignia secundaria cuenta las pantallas internas autorizadas. No se fuerza una cantidad por el nombre del rol: una cuenta con un módulo autorizado muestra uno.

La navegación interna obtiene las vistas Django y reutiliza el lateral cuando su estructura no cambió. Conserva su scroll, los grupos y el estado contraído. Incluye historial del navegador, cancelación de solicitudes de navegación obsoletas y protección de formularios pendientes. Los cambios ordinarios por sincronización actualizan fragmentos. Una revocación puede recargar deliberadamente después de retirar contenido protegido.

El acceso de vuelta a la bienvenida tiene una superficie contrastada e icono. Los modales usan crema suave en claro y base neutra en oscuro. Las tarjetas de indicadores conservan controles, puntos, desplazamiento táctil y barra discreta; se retiró la franja de acento fuerte. La comparación de mascotas disponibles y adoptadas consulta estados reales y solo aparece con acceso global de mascotas. No representa una serie temporal.

## Auditoría

El backend registra identidad del actor, nombre y roles vigentes al registrar, resultado, ruta de operación sin valores secretos, referencia aleatoria de solicitud y de sesión web cuando existe, recurso e identificador. Los nombres del elemento y del rol se conservan cuando el servicio dispone de ellos. Los permisos se acumulan: no se inventa un único rol ejecutor; se muestra el conjunto vigente y la capacidad identificada cuando está disponible.

Las consultas indican recurso e identificador. Los cambios de permisos y asignaciones incluyen el rol específico. Se registran rechazos autenticados y fallos controlados, y los intentos de login no validados se atribuyen a acceso sin autenticar, sin fingir una identidad. No se guarda la contraseña, captcha, token, cookie, correo intentado, payload completo ni dirección IP en el evento. Se mantienen los límites de login existentes.

Se filtran claves sensibles y se limita profundidad y tamaño de metadatos. Llamadas idénticas de auditoría dentro de una petición se deduplican. El panel no agrega un evento genérico cuando el servicio ya registró la operación real. Dos operaciones distintas siguen siendo dos eventos.

Los eventos anteriores no se reescribieron. Los campos históricos que no fueron registrados se muestran como no registrados. La vista permite filtrar por persona, categoría, fechas, módulo y resultado, paginar y agrupar visualmente los eventos de la página por persona o referencia de sesión. La agrupación no elimina ni sustituye registros individuales.

Se añadieron índices de fecha, actor/fecha y recurso/fecha. La exportación CSV aplica los mismos filtros, captura un límite de identificador, limita 10.000 eventos, neutraliza fórmulas y excluye el JSON bruto. Requiere `auditoria.exportar` y registra la exportación.

`python manage.py archivar_auditoria --dias 365` evalúa filas y tamaño aproximado de JSON mediante una muestra. `--escribir` genera una copia JSONL comprimida y un manifiesto SHA-256 bajo `LPN_PRIVATE_ROOT/auditoria`. Puede indicarse `--antes` con fecha ISO y zona horaria. Nunca borra registros ni publica archivos. La conservación sigue siendo indefinida; la antigüedad de copia es configurable por la ejecución y no existe tarea automática de purga. La estimación no incluye índices, páginas ni sobrecarga de MySQL. El hash verifica la copia, no certifica inmutabilidad del servidor.

## Roles y capacidades

El catálogo y la asignación consultan roles de la base, incluidos roles personalizados y de organización. Los roles inactivos se conservan en el catálogo para trazabilidad y no conceden acceso. Un rol de plataforma se asigna a la cuenta; un rol de organización requiere membresía vigente y puede ser plantilla reutilizable o estar vinculado a una organización concreta mediante el nuevo FK opcional. El cargo principal conserva su procedimiento específico de designación y transferencia.

El formulario crea o edita nombre, descripción obligatoria, organización cuando corresponda, estado y permisos en una transacción. La edición del panel utiliza una versión del rol para impedir sobrescrituras concurrentes. La API devuelve `version` y admite `If-Match` en PATCH para clientes que implementen concurrencia optimista; clientes anteriores siguen siendo compatibles. El servidor conserva códigos y ámbitos estables y valida todos los permisos.

La administración de seguridad y el superusuario pueden administrar las capacidades reconocidas. Un gestor limitado no puede conceder capacidades superiores a su autorización. Los responsables mantienen su delegación legítima de cargos de organización, sin poder conceder capacidades globales superiores ni asignar roles ligados a otra organización. La misma comprobación se aplica a excepciones que permitan capacidades. Las operaciones revalidan autorización bajo los bloqueos administrativos.

La matriz incorpora Eliminar y conserva acciones específicas implementadas como resolver, asignar, gestionar y autorizar. Se agregaron acciones reales de eliminación, desactivación y restauración para usuarios, roles y entidades, y exportación de auditoría. Se asignaron al Administrador de seguridad existente mediante migración; no se ampliaron roles ciudadanos automáticamente.

Administrar acciones permite mantener descripción y estado de operaciones del registro cerrado del servidor. No crea endpoints a partir de un nombre. Una acción completamente nueva requiere implementar y probar primero su handler y política. Aprobación y rechazo conservan los contratos de resolución existentes cuando comparten una operación; no se añadieron switches ficticios.

## Bajas y restauraciones

Cada operación consulta dependencias, identifica el registro y exige motivo, confirmación explícita y escritura exacta del nombre o correo. El botón permanece deshabilitado hasta completar la confirmación. El backend revalida todo: permisos, firma temporal, identidad del administrador, versión de dependencias y restricciones del elemento. Una confirmación caduca a los diez minutos.

Las operaciones se serializan y utilizan un identificador único persistente: repetir la misma confirmación devuelve el resultado sin ejecutar una segunda baja ni duplicar su evento. Las relaciones protegidas y dependencias impiden el borrado físico. El colector de Django vuelve a comprobar que no se borren o modifiquen otros registros.

- Desactivar bloquea temporalmente el acceso o la operación.
- Eliminar lógicamente conserva el registro, sus relaciones y el historial, marcando su baja.
- Restaurar es una operación autorizada y confirmada; no reactiva asignaciones revocadas.
- Borrar físicamente solo está disponible sin dependencias. Las cuentas normales suelen tener historial o asignaciones, por lo que corresponde la alternativa lógica.
- No se ejecuta anonimización automática. Requiere un procedimiento específico de tratamiento y conservación de datos.

No se permite la baja de la propia cuenta ni de cuentas técnicas esenciales desde este flujo. Se conserva la protección del último administrador y de responsables principales que deben transferirse o recuperarse antes. Los roles estructurales no se eliminan ni desactivan; sus permisos siguen siendo administrables conforme a la autorización, manteniendo el objetivo pedagógico de configurar Ciudadano y los demás roles.

La baja de entidades mantiene miembros, mascotas, adopciones, reportes y demás relaciones. Muestra dependencias directas y cantidades históricas relacionadas. El motor retira el contexto inactivo y bloquea operaciones vinculadas; las consultas administrativas históricas siguen disponibles. Los catálogos públicos excluyen organizaciones inactivas. Restaurar conserva revocaciones previas.

## Base de datos y endpoints

Migraciones aditivas: `core.0008_fase_dos_administracion` y `seguridad.0014` a `0016`. Añaden el FK opcional `Rol.entidad`, las tablas `BajaAdministrativa` y `OperacionAdministrativa`, tres índices de auditoría y diez capacidades reales. El contenido histórico se conserva.

- `GET/POST /api/seguridad/administracion/<tipo>/<id>/baja/`: previa autorizada y ejecución confirmada; tipos `usuarios`, `roles`, `entidades`.
- `GET/POST /panel/bajas/<tipo>/<id>/`: mismo servicio en modal y respaldo SSR.
- `GET/POST /panel/acciones/`: catálogo de operaciones implementadas, con permiso administrativo.
- `POST/PATCH /api/seguridad/roles/`: admite permisos integrados y organización; PATCH sobre el identificador admite If-Match.
- `GET /panel/auditoria/?exportar=csv`: exportación filtrada, con permiso específico.
- Las rutas anteriores de listas, matrices, asignaciones y negocio siguen vigentes.

## Organización del código

`web/navegacion.py` agrupa módulos; `static/seguridad/navegacion.js` conserva navegación y confirmaciones; `interacciones.js` y `sincronizacion.js` reutilizan fragmentos. `administracion_segura.py`, `roles_admin.py`, `bajas_api.py`, `web/bajas.py` y `web/acciones.py` concentran validaciones. `auditoria_contexto.py` y `servicios.auditar` registran y acotan metadatos. `web/dashboard.py`, `web/exportar_auditoria.py` y el comando de archivado presentan y exportan los eventos. Las plantillas, estilos y catálogos de idioma se actualizaron sin sustituir el sistema de diseño.

## Verificación y límites

Pruebas de permisos, límites administrativos, ámbito de organización, concurrencia, idempotencia, bajas lógicas, borrado físico sin dependencias, conservación del historial, agrupación, exportación y archivado privado. Las pruebas de creación/baja/restauración usan únicamente datos sintéticos locales. En producción se realiza verificación de lectura, sin borrar cuentas o entidades para demostrar el funcionamiento.

La validación automática no sustituye una prueba de carga, revisión manual integral de accesibilidad ni auditoría externa de seguridad. No se afirma almacenamiento WORM ni cumplimiento de una política legal de retención. La búsqueda libre por contenido puede necesitar un índice especializado a mayor volumen; los filtros estructurados e índices existentes son la vía eficiente. Los clientes API que quieran impedir sobrescrituras deben enviar la versión/If-Match. Mantener una vía técnica de recuperación es importante porque la configuración de permisos de roles continúa siendo una responsabilidad administrativa.

## Cierre de verificación

La suite general descubrió y aprobó 192 pruebas en 24,678 segundos. Se verificaron en navegador la creación de roles con permisos, baja lógica y restauración, bloqueo del botón sin confirmación, navegación sin desmontar el lateral, columna Eliminar real, agrupación y detalle contextual de auditoría. También aprobaron las revisiones de cinco vistas en claro/oscuro y 15 combinaciones de resolución con texto ampliado. La concesión y revocación entre dos sesiones funcionó sin iniciar sesión nuevamente; la revocación local de esa prueba se reflejó en 869 ms, una medición puntual.

El administrador técnico valida las bajas antes de guardar y revalida dentro del bloqueo transaccional. No permite retirar el último superusuario técnico activo ni desactivar una cuenta técnica protegida; las condiciones se muestran como errores del formulario. El reintento concurrente que perdió autorización se rechaza sin guardar. Los controles del panel siguen siendo independientes de los privilegios técnicos de Django Admin.

El respaldo previo de la base del panel tiene 239.762 bytes y SHA-256 `bab16b2fea0d91abafc71244f6b5d05aee1f7eb757d3258cfb91d8e006316697`. Se aplicaron correctamente las cuatro migraciones; no se tocó el servicio ni la base anterior. En la medición previa al cierre había 255 eventos históricos; la muestra de los 100 recientes promedió 58 bytes de JSON, que no predice el tamaño de los nuevos eventos con contexto. Los tres índices se verificaron en MySQL. No se ejecutaron bajas ni operaciones administrativas de demostración en producción.

Los permisos completamente arbitrarios sin implementación del servidor, la purga histórica automática y la anonimización automática no se simulan: quedan expresamente fuera de esta entrega. Las bajas usan alternativas seguras reales y mantienen los registros vinculados. Para una siguiente validación operativa conviene medir carga concurrente y revisar manualmente con lectores de pantalla.

La confirmación de baja incluye la identidad, estado, ámbito, vínculo de organización y datos de revisión además de las dependencias y asignaciones. Cambiar, por ejemplo, la descripción de un rol después de abrir la confirmación obliga a revisar de nuevo antes de eliminarlo. En producción aprobaron once comprobaciones de lectura, incluyendo conservación de grupos e historial interno, formulario integrado y protección del rol estructural; no hubo errores JavaScript observados. Las rutas de reclamación ciudadana se conservan aun ante una organización inactiva, sin reabrir su operación ordinaria.

La auditoría de fallos rechaza identificadores fuera del rango de almacenamiento sin convertir una respuesta 404 en error del servidor; solo conserva una referencia numérica acotada. Los rechazos de validaciones administrativas controladas también se registran cuando se intentó una operación real del backend, sin guardar el contenido sensible enviado.

Las entradas de Organizaciones, Equipo y Cuentas que comparten pantalla se consolidan en una sola entrada y un solo módulo contado. Una cuenta autorizada únicamente para cuentas puede abrir su pantalla sin recibir acceso a los miembros del equipo. La identificación visible del usuario incluye los roles de su organización seleccionada, además de los globales.

Publicación final: Railway `c37a6229-57a8-4004-af4d-4e74ea280063`, estado SUCCESS. Las once comprobaciones de producción aprobaron sobre esta publicación, sin errores JavaScript observados. El login realizó únicamente la petición del documento `/panel/login/` durante la carga medida. Se comprobó la navegación, el contador autorizado, la conservación de grupos e historial, el formulario integrado, la protección de baja del rol estructural, las versiones para concurrencia y la agrupación y detalle de auditoría. La sesión temporal de revisión se cerró al terminar.
