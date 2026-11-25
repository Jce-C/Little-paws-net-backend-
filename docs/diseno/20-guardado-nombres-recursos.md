# Guardado de nombres de recursos

Fecha: 2026-11-04.

Fallo reproducido: al editar un recurso en un diálogo, Guardar nombre no enviaba ninguna petición. El campo oculto `name=id` ocultaba la propiedad DOM `form.id`. Al mover las acciones al pie fijo, el atributo `form` de los botones recibía una referencia incorrecta y los controles quedaban sin formulario asociado. No era un fallo de red ni una restricción RBAC.

Corrección: leer y escribir el identificador HTML mediante getAttribute/setAttribute; utilizar esa cadena para asociar los controles del pie y buscar el botón al guardar. Mantener actualizado el indicador de cambios pendientes aunque esté fuera del formulario. La solución también cubre otros formularios de edición con un campo llamado id.

Aceptación local: 8 comprobaciones correctas, incluyendo POST confirmado, nombre en menú sin recargar, sincronización con otro usuario abierto, persistencia, Enter y edición como página completa. También pasan las 12 comprobaciones del diálogo de cambios pendientes. No se renombraron recursos en producción para probar.
