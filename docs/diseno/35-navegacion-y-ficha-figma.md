# Navegación y ficha pública Android: revisión contra Figma

Referencias originales:

- [Catálogo y navegación, frame 108:376](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu/Untitled?node-id=108-376).
- [Ficha e historia, frame 128:502](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu/Untitled?node-id=128-502).

Se consultaron el contexto detallado y las capturas de ambos frames antes de implementar. Esta revisión continúa la guía 34: no certifica todavía una reproducción de todas las pantallas.

## Navegación común

La barra inferior ocupa el ancho disponible, usa fondo crema y una línea superior como en el original. Se elimina el contenedor flotante que ocupaba demasiado espacio. Conserva los cuatro destinos reales: Rescates, Adoptar, Solicitudes y Mi cuenta. No se incorpora una tienda sin funcionalidad para imitar el prototipo.

Se descargaron los vectores originales de cabecera (29 × 20) y navegación (38 × 31); se conservan sus dimensiones y la transformación del frame. La marca central es decorativa, no un quinto destino ficticio. La selección se reconoce por subrayado, peso tipográfico y semántica, sin depender del color. Los objetivos táctiles tienen al menos 48 × 48 puntos lógicos. En teléfonos con texto ampliado se usan dos filas; las etiquetas no se reducen para forzarlas en una fila.

## Ficha pública

La foto dinámica conserva 248 × 226 puntos, muestra la imagen completa y recibe la tarjeta con borde claro y sombra cálida. Edad y tamaño se agrupan con las cápsulas verdes e iconos originales. Los valores largos se envuelven; los desconocidos se presentan como Sin registrar. No se inventa una edad o una raza.

SU HISTORIA recupera el panel crema, los marcadores y la línea vertical de Figma. Muestra únicamente datos ya autorizados por el contrato público: organización bajo cuyo cuidado está, fecha de custodia, ciudad y disponibilidad actual. No se afirman rescate, vacunas o esterilización porque esa información no forma parte de esta respuesta. Tampoco se añade al público el botón de expediente/QR del prototipo. El expediente y QR existentes siguen sujetos al flujo de mascotas propias y permisos del backend.

La opacidad del crema se resuelve sobre el lienzo antes de dibujar la sombra para evitar que esta oscurezca todo el interior. Reducir transparencias/contraste alto conserva una superficie sólida y elimina la sombra de la historia. La acción verde de adopción permanece fuera del scroll, con al menos 48 puntos de altura. Los textos auxiliares usan 12 puntos y la historia 11 para datos dinámicos legibles.

Los tres PNG de iconos/marcador proceden de los recursos originales. history-dot.svg conserva la fuente; su variante PNG de 112 × 108 reproduce a escala 4× los filtros SVG que flutter_svg no soporta. No se redibujó el símbolo ni se empleó generación de imágenes. Ninguna URL temporal de Figma se utiliza en ejecución.

## Validación y evidencia

- 108 pruebas Flutter aprobadas; análisis sin incidencias y APK debug QA compilado.
- Cuatro regresiones nuevas comprueban navegación, selección, áreas táctiles, zona segura y texto 200 % en 320 × 640 y 800 × 360.
- Dos regresiones de ficha comprueban datos verificados, ausencia de eventos médicos inventados, organización larga, valores desconocidos y acción siempre visible con texto ampliado.
- Cuatro destinos comprobados en el emulador con lectura de selección accesible. Capturas 14 y 15 de navegación; 16–18 de ficha/historia y texto ampliado. Se restaura la escala original 1.0.
- Logs y JSON en output/adopcion-movil. No se escriben registros de negocio ni se utilizan cuentas o imágenes reales.

## Repartición y límites

María José incorpora componentes, recursos y pruebas Android; Sally revisa las comparaciones y documentación. José Carlos no necesita modificar contratos ni permisos en este bloque. Los ZIP se regeneran y validan sin commits, ramas ni publicación.

Siguen pendientes las comparaciones específicas de perfil, rescates, formularios y estados, y la revisión equivalente del panel web. El encabezado material de la pantalla principal conserva por ahora su tratamiento anterior. La navegación de la ficha es una ruta secundaria con volver/actualizar, no una copia de los controles de marca del prototipo. TalkBack en dispositivo físico, firma y evaluación de rendimiento en un entorno autorizado continúan pendientes. La app sigue siendo un piloto local.
