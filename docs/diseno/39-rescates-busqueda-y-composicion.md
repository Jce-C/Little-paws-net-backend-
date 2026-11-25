# Rescates móvil: composición y búsqueda local

Referencia: [Figma, frame 8:44](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu/Untitled?node-id=8-44). Se revisaron el contexto detallado y la captura antes de implementar. Se reutiliza la misma ilustración local rescue-banner.webp; no se genera ni se añade otra imagen.

## Presentación

La búsqueda vuelve a la parte superior de la ilustración, con superficie clara y sombra cálida. El campo conserva una etiqueta semántica estable al escribir, separada del título; se verifica en el árbol Flutter. El XML de UIAutomator no expone esa etiqueta y no sustituye la comprobación manual con TalkBack. El título de 15 puntos vuelve al sector inferior izquierdo; una base crema discreta mantiene legibilidad sobre la imagen. Con texto ampliado se mueve debajo para no competir con el buscador. Se mantienen áreas táctiles amplias en lugar de copiar los 24 px de altura no accesibles del campo dibujado.

Reportar un animal aparece inmediatamente después de la ilustración. Mis reportes y Gestionar reporte anónimo se agrupan como acciones secundarias adaptables. Se eliminan el bloque de título/introducción duplicado y el segundo buscador que empujaban el listado demasiado abajo. El encabezado de los reportes usa la escala de 15 puntos del Figma.

Los registros siguen siendo los de la API, sin mascotas, fotos, estados o coordenadas ilustrativos. Se mantiene el listado vertical con acceso al detalle completo. No se incorpora el botón Ver mapa cercano del prototipo: no hay un mapa implementado ni coordenadas verificadas para representarlo. Tampoco se presentan categorías sin un destino funcional.

## Búsqueda y red

Se filtran situación, estado y descripción de los reportes cargados, ignorando mayúsculas y tildes de vocales. Limpiar búsqueda restaura el listado ya recibido. Ninguna pulsación ni limpieza genera otra petición. La tecla Buscar cierra el teclado. Actualizar y Reintentar siguen siendo acciones explícitas.

El endpoint público actual no proporciona ciudad ni caso de rescate al cliente. No se afirma que exista un filtro estructurado de ciudad ni se fabrican esos campos: una ciudad solo coincide si está escrita en la descripción pública. El seguimiento propio conserva su endpoint autenticado y datos reales. El listado público está limitado por el contrato existente a 100 registros; este cambio no implementa búsqueda global ni paginación. Esa ampliación queda pendiente.

## Comprobación

- 121 pruebas Flutter aprobadas y análisis sin incidencias; seis regresiones nuevas de geometría, acción inicial visible, búsqueda sin tildes, limpieza sin peticiones, texto 200 % a 320 × 640 y 800 × 360 y reintento de fallo.
- Se mantienen las pruebas de envío de reporte autenticado y anónimo, opciones de ciudad y seguimiento. Los POST de esas pruebas son simulados, sin escribir reportes en el QA ni producción.
- APK debug normal compilado para el backend QA local y comprobado en el emulador con navegación, buscador y texto ampliado. Capturas 30/31, logs y validacion-rescates-figma-20261119.json documentan el resultado. Se restaura la escala original del sistema.
- Backend, permisos, base de datos y contratos sin cambios en este bloque. Las pruebas Django previas son evidencia histórica, no una ejecución nueva. No se añaden paquetes de UI ni descargas externas de imágenes.

María José recibe componentes/pruebas Android; Sally documentación y capturas; José Carlos mantiene la API. Paquetes separados verificados, sin commits ni publicación. Pendiente: revisar formularios/estados web, alcance/paginación de reportes y dispositivo físico/TalkBack, firma y rendimiento autorizado. No se declara fidelidad global de todas las pantallas ni producto comercial terminado.


Actualización 20-11-2026: la búsqueda local descrita en esta revisión fue sustituida por búsqueda del servidor y páginas de 20. La composición permanece; consultar la guía 42 para contrato, solicitudes y pruebas actuales.
