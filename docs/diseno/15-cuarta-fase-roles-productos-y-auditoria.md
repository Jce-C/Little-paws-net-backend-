# Cuarta fase: productos, roles múltiples y controles administrativos

Actualización del 30 de octubre de 2026 sobre el panel Django existente. Sin commits ni ramas nuevas. No se eliminan ni se crean datos de negocio de demostración en producción.

## Problemas y causas

**Productos.** Existían alta, edición, disponibilidad, existencias y relación con tiendas, pedidos, imágenes y cambios históricos. No había una operación de eliminación autorizada de extremo a extremo. Retirar un producto requería distinguir la eliminación física de una baja real con historial, y filtrar los archivados también en consultas administrativas.

**Roles.** El modelo ya admitía varias filas por usuario/rol y por miembro/rol; no existía una restricción de tres relaciones. Plataforma habilitaba los tres roles globales iniciales y deshabilitaba los roles de organización por su alcance. Además, guardar validaba la delegación de roles ya asignados y sin modificar, lo que podía bloquear una edición válida. La interfaz no facilitaba suficientemente entrar al contexto correcto ni distinguía los roles de sistema sustituidos de un rol personalizado simplemente inactivo.

**Eliminación y auditoría.** La confirmación mezclaba información técnica y controles que no siempre correspondían al riesgo. Filtros y agrupación compartían una misma zona pese a cumplir propósitos distintos. Se mantiene la tabla de auditoría, sus columnas y detalles; no se reescriben registros históricos.

## Soluciones

### Eliminación de productos

Se reutiliza el servicio transaccional de bajas con el tipo `productos`, asociado al permiso real `producto.eliminar`, de alcance organización/tienda. La operación vuelve a comprobar autorización, contexto, estado, dependencias y confirmación firmada; conserva la idempotencia.

Archivar actualiza `estado_producto` a Inactivo y registra una baja lógica real. El producto deja de aparecer en listados habituales, públicos y administrativos. No puede reactivarse mediante el endpoint ordinario de edición. Las líneas de pedido, precios de referencia, imágenes y cambios históricos permanecen intactos.

El borrado físico solo se habilita sin dependencias. La revisión utiliza las relaciones y el recolector de Django y no permite eliminar en cascada otros registros. Un producto creado normalmente ya puede tener un CambioProducto: ese historial también cuenta como dependencia y se conserva. En esos casos la eliminación correcta es el archivado, no borrar el historial para liberar el producto.

La auditoría conserva nombre, tienda, precio, existencias, estado y referencias del producto antes de eliminarlo. El resultado se refleja en el catálogo mediante la navegación parcial existente, sin recargar toda la plataforma. Repetir la misma confirmación ejecutada no duplica la operación; una confirmación reutilizada para otra acción se rechaza.

### Roles múltiples

La asignación HTML y JSON comparte `seguridad/asignaciones.py`. Acepta un arreglo dinámico de identificadores, deduplica, guarda dentro de una transacción y comprueba la versión del contexto revisado. Mantiene relaciones únicas y no toca los roles de otros contextos.

La autoridad se valida sobre las concesiones y revocaciones efectivas. Un rol ya asignado que el actor no puede modificar se conserva como solo lectura; no se convierte en una concesión nueva ni puede retirarse por un actor sin autoridad. Persisten jerarquía, delegación, ámbito, organización, cuentas activas y la protección del responsable principal. Este último sigue gestionándose mediante el procedimiento de designación/transferencia.

Los roles disponibles se muestran primero, con contador del contexto, resumen de asignaciones y accesos al contexto correcto. Se sustituye el rótulo abstracto Contexto por Asignar en. Un cargo de organización requiere elegir su organización; no se transforma en un rol global. Los roles de sistema sustituidos tienen una explicación específica y no se reactivan automáticamente. Los roles personalizados nuevos aparecen desde la base sin listas fijas.

Endpoint nuevo: `GET/PUT/PATCH /api/seguridad/usuarios/<id>/asignaciones-roles/`. GET devuelve asignaciones y versión; PUT/PATCH reciben `roles`, `version`, `motivo` y opcionalmente `entidad` e `incorporar`. El arreglo expresa la selección del contexto indicado; no debe utilizarse para enviar roles de otro ámbito. Las asignaciones inactivas históricas no se revocan como efecto lateral de guardar roles activos. La incorporación a una organización sigue requiriendo confirmación y autorización explícitas.

### Confirmación e icono de regreso

La eliminación presenta título breve, nombre, advertencia, motivo y confirmación, con Cancelar/Eliminar. El nombre adicional depende del riesgo; es obligatorio para borrado físico y para registros con vínculos relevantes. Las opciones de eliminación definitiva se agrupan de forma secundaria y solo existen cuando es seguro ofrecerlas. Desactivar/restaurar conservan la confirmación sencilla de la fase anterior.

El regreso desde Excepciones utiliza un icono de flecha funcional de 36 px, tooltip, nombre accesible y foco visible. Mantiene la persona y su organización tanto en página como en la ventana de Usuarios.

### Auditoría y responsividad

Se conserva la tabla. Búsqueda, módulo y resultado quedan visibles; persona, tipo y fechas se agrupan como filtros avanzados. Aplicar y Limpiar filtros permanecen explícitos. Escribir en la búsqueda no aplica filtros automáticamente; al aplicar se reutiliza la página sin recargar la plataforma. Organizar resultados es un control independiente, con estado visible y opciones por persona/sesión. Agrupar conserva los filtros aplicados; limpiar filtros conserva la agrupación. La paginación y exportación mantienen sus parámetros.

Los grupos siguen describiendo los eventos de la página actual, con actor, cantidad y periodo, y se expanden para mostrar la misma tabla. No se cambia el significado del historial para acomodar la interfaz.

Se corrigió un desbordamiento móvil de la matriz de Excepciones, manteniendo el desplazamiento horizontal dentro de su contenedor. Los botones inferiores se acomodan sin expandir la página. Se mantienen la paleta, claro/oscuro, tipografía e iconos existentes y las traducciones de los controles nuevos.

## Archivos principales

- `seguridad/asignaciones.py`, `asignaciones_api.py`: servicio y entrada JSON de selección múltiple; `web/administracion.py` reutiliza el servicio y presenta disponibilidad/contextos.
- `seguridad/administracion_segura.py`, `web/bajas.py`, `models.py`: baja de productos, revisión de riesgo, historial e idempotencia.
- `commerce/consultas.py`, `seguridad/flujos_views.py`, `web/negocio.py`: consultas vigentes, bloqueo de edición de archivados y acción por producto.
- `politicas.py`, `presentacion.py`, `urls.py`: permiso y endpoint reconocidos por el backend.
- `templates/seguridad/web/administracion.html`, `baja.html`, `negocio.html`, `auditoria.html`: icono, controles compactos, acceso a eliminación y separación de filtros/agrupación. No se sustituye `auditoria_tabla.html`.
- `web/dashboard.py`, `static/seguridad/compacto.css`, `interacciones.js`, `navegacion.js`: preservación de parámetros, adaptación visual y confirmación según riesgo.
- Catálogos de idiomas `.po/.mo` y `tests_fase_cuatro.py`; ajuste del test previo de filtro avanzado para el nuevo reparto entre filtros visibles y avanzados.

## Base de datos

Una migración aditiva: `seguridad.0019_eliminacion_productos`. Declara el tipo productos en la baja administrativa y registra `producto.eliminar`, concedido a los roles existentes GESTOR_CATALOGO y ADMIN_SEGURIDAD. Su uso sigue requiriendo el ámbito de la tienda, salvo la precedencia técnica previamente existente. Los roles personalizados requieren su configuración explícita; no se modifica Ciudadano.

No cambia las tablas ni las restricciones de asignación múltiple, porque ya admitían varios roles. No se borran relaciones históricas ni se reactivan roles inactivos para aparentar que están disponibles.

## Pruebas

225 pruebas del backend aprobadas. Escenarios nuevos: uno, dos, tres y cinco roles; roles personalizados y de organización; dos organizaciones conservando roles globales; retirar solo uno; volver a consultar; rechazo sin autoridad; rechazo de versión antigua y destino inexistente sin error del servidor; conservar roles de superior autoridad sin poder revocarlos; producto con pedido archivado y detalle intacto; producto sin dependencias eliminado físicamente y reintento idempotente; rechazo de tienda no autorizada y de edición de producto archivado; icono con contexto y agrupación separada.

En navegador local aprobaron 12 comprobaciones: asignar cuatro roles personalizados mediante la web y recargar para comprobar persistencia; retirar uno conservando los demás; regreso accesible con persona/contexto; agrupación y limpieza conservando parámetros; modal de producto compacto; eliminación real reflejada sin recarga; activación de confirmación adicional en borrado físico y ejecución segura; móvil sin desbordamiento. Las creaciones y eliminaciones de prueba fueron exclusivamente locales.

Cuatro vistas revisadas con axe en claro/oscuro no presentaron infracciones de las reglas comprobadas. No se detectó desbordamiento de página a 390 px, y la landing conservó su ruta al cambiar de tema. Esto no sustituye revisión manual integral con lector de pantalla ni prueba de carga.

## Uso

Para cargos de equipo: Usuarios → Roles → Asignar en → organización real → seleccionar varios roles → motivo → Guardar roles. Se confirma incorporación si la persona aún no pertenece a esa organización. Para roles globales, elegir Plataforma; para un rol personalizado, comprobar primero que esté activo y definido en el ámbito correcto.

Para un producto: Catálogo → acciones de la fila → Eliminar producto → revisar consecuencia y motivo → confirmar → Eliminar. Si hay historial, se archiva y se preservan sus relaciones. El borrado definitivo se ofrece únicamente cuando no hay dependencias y pide confirmación adicional.

## Publicación y cierre

Despliegue `138fe578-f73e-4853-8dd0-9630bd9ad54f`, estado SUCCESS en Railway. Se respaldó exclusivamente `little_paws_panel_v2`: 332.350 bytes; SHA-256 `fbd8c1abdd0410bf075c414aad6f3b6b0be9b07e51a2f39a300ecbb529ce0d67`. Se aplicó correctamente `seguridad.0019_eliminacion_productos`. La base anterior se conservó.

Aprobaron 13 comprobaciones en producción sobre ese despliegue: login con una petición, contexto explícito, endpoint múltiple con versión, regreso con persona/contexto, permiso real de eliminación de productos y reconocimiento del manejador, confirmación compacta, agrupación separada, filtros aplicados sin recargar la plataforma, conservación de filtros/agrupación, tabla y detalle y móvil sin desbordamiento. No hubo errores JavaScript observados. La revisión no asignó roles ni eliminó productos reales; las operaciones destructivas y las asignaciones de prueba se ejecutaron solo en la base local aislada. La sesión temporal se cerró y su archivo se retiró.

La revisión de inglés recorrió 14 vistas y conservó controles compactos, borradores y lateral contraído. No quedan funcionalidades de esta fase sin implementar; permanecen como validaciones adicionales una revisión manual integral con lector de pantalla y pruebas de carga concurrente. Los roles fuera de contexto, sin autoridad o inactivos siguen restringidos por diseño y con explicación; esas restricciones no se sustituyen por asignaciones globales ficticias.
