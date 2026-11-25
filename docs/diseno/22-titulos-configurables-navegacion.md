# Títulos configurables de la navegación

Fecha: 2026-11-04.

## Uso

En el panel, abrir **Configuración** desde la barra superior. Las tres secciones desplegables nuevas son **Navegación: encabezados**, **Navegación: secciones** y **Navegación: opciones**.

- Encabezados: subtítulo bajo el logo, Mi espacio, Roles y recursos, Espacio de trabajo, Módulos autorizados, estado y mensaje del pie del lateral.
- Secciones: Seguridad, Administración, Organizaciones y equipos, Mascotas y rescates, Mi participación, Moderación, Mi organización, Operación y Atención veterinaria.
- Opciones: títulos de los módulos, tarjetas de seguridad y sus pantallas, incluidos Usuarios, Roles, Recursos, Permisos, Roles por persona, Catálogos y las áreas de negocio.

Escribir los títulos deseados, indicar el motivo y guardar. Dejar un campo de navegación en blanco restablece el nombre habitual o el nombre actual del recurso. El límite es de 80 caracteres por título. Los textos de marca personalizados se conservan literalmente al cambiar de idioma; los nombres predeterminados y la interfaz de configuración siguen usando las traducciones del sistema.

## Contrato funcional

Los cambios afectan la presentación; no cambian códigos de recursos o permisos, rutas, asignaciones, acciones implementadas, alcances de organización ni colores de los usuarios. Para opciones con un recurso, su nombre continúa siendo la fuente predeterminada. Un título personalizado explícito lo reemplaza visualmente hasta que se deja en blanco. Así se conserva el guardado y renombrado de recursos existente.

Se reutiliza ConfiguracionPanel; no hay cambios de esquema ni migraciones nuevas. Ver la configuración exige configuracion.ver y guardarla exige configuracion.editar. Las categorías conservan identificadores internos estables, independientes del nombre, el idioma y los permisos visibles de cada persona. Los contadores y la selección del menú siguen derivados de los accesos reales.

Los cambios se comunican mediante el canal de sincronización existente, sin añadir consultas periódicas. Se actualizan nombres de categorías, opciones, tarjetas, encabezados y textos del lateral. Se conservan los formularios abiertos con cambios y el estado plegado de las categorías. Cada operación sigue verificando permisos en el backend.

El formulario incluye una versión de configuración: si otra persona la modifica mientras se edita, el guardado desde una versión antigua se rechaza, conserva el borrador y pide recargar. La auditoría registra actor, motivo, título afectado y valores anteriores/nuevos, con nombres legibles. Se mantienen el pop-up de cambios pendientes y las acciones visibles del pie del formulario.

## Validación

- 250 pruebas Django correctas, incluidas ocho pruebas nuevas de configuración, herencia de nombres, autorización, sincronización del estado, auditoría, límites, concurrencia, escape HTML y agrupación en inglés.
- 13 comprobaciones de interfaz de navegación: edición real en la base local, otra cuenta abierta, ciudadano sin privilegios adicionales, borradores preservados, menú plegado, móvil, inglés y axe sin incidencias en configuración clara/oscura.
- Regresiones verificadas: renombrar recursos (8), cambios pendientes (12), concesión/revocación en otra sesión (5), confirmaciones de eliminación (6), guardar/descartar la matriz (3) y login/landing (14), incluido login con una sola petición inicial.
- Verificación final adicional de las 36 pruebas de títulos y acceso web; sin migraciones pendientes.

Las pruebas que guardan o eliminan datos se realizaron exclusivamente en la base aislada local. No se personalizaron títulos ni se alteraron permisos de producción durante la aceptación. No se crearon commits ni ramas.

Evidencias: output/navegacion-configurable-2026-11-04/, seguridad/tests_navegacion_configurable.py y .codex_tmp/pruebas-navegacion-configurable-20261104.log.
