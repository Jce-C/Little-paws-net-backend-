# Bienvenida y continuidad de la barra flotante · 21 noviembre 2026

## Petición y prioridad visual

La petición directa de esta revisión sustituye la restauración del acceso de la guía49: se conserva el acceso Stitch (controles28 y CTA oscuro), no el tema previo de crema/relieve. Login y registro permanecen separados de la bienvenida. Los cambios de sesión de las guías50/51 se conservan en el cliente canónico.

## Recorte reproducido y corrección

El Scaffold reservaba un rectángulo completo por encima del menú flotante; el borde de ese viewport cortaba fotos/tarjetas en línea recta, antes de llegar a la silueta de la cápsula. Ahora extendBody permite continuar el contenido detrás de la barra. Inicio, catálogo, solicitudes y cuenta agregan el espacio de navegación al final del desplazamiento, de manera que la última acción pueda quedar completamente encima del menú. El catálogo añade un sliver final; no se modifica su paginación o transporte.

También se da un margen interior horizontal de12 a las etiquetas de la cápsula; a anchuras muy pequeñas o texto ampliado, los destinos se distribuyen por columnas. Se mantiene la concavidad real, el botón elevado56 y su comportamiento: perro→Inicio; más desde Solicitudes→selección de mascota, sin envío automático. Teclado y zona segura siguen respetándose.

## Bienvenida

Jerarquía breve, marca completa, superficie orgánica mantequilla32, sombra cálida ligera, sello de huella y detalle de cuidado. Un CTA principal y dos acciones secundarias permanecen visibles en tamaños ordinarios; texto200% puede desplazarse y no se reduce para forzar el encaje. Entrada finita de820ms con tres intervalos: marca, tarjeta, acciones. Solo opacidad y traslación, sin alterar la geometría del flujo, red, dependencia adicional ni espera para habilitar controles. Con disableAnimations se muestra directamente el estado final; no hay bucles ni movimiento persistente.

## Web y fuentes consultadas

La demo recibe un host fijo acotado a100dvh, con fallback100%, y el indicador de carga queda fuera del flujo. Se configura hostElement tanto en loader.load como initializeEngine siguiendo Flutter: https://docs.flutter.dev/platform-integration/web/embedding-flutter-web y https://docs.flutter.dev/platform-integration/web/initialization. No se atribuye el recorte observado a este ajuste de host; la causa nativa comprobada es la reserva rectangular del Scaffold.

TypeUI fundamentos: jerarquía, agrupación de acciones, objetivos táctiles y alternativa al movimiento. Modern Web Guidance, guía motion: «Keep the final state» y preferencia de animar opacity/transform. Se adapta a los widgets equivalentes de Flutter, sin introducir una animación CSS que Flutter no utiliza.

## Pruebas y límites

174 pruebas canónicas y análisis sin incidencias; tres regresiones nuevas sobre viewport320×560/390×740, última acción alcanzable, etiquetas dentro del path, texto200% y movimiento reducido. La demo independiente supera28 pruebas focalizadas que incluyen los banners abierto/cerrado en320×640,460×540 y1000×700, acceso redondeado, paginación y contratos ficticios. Builds web release, Android visual y QA compilados. La prueba antigua de geometría se actualiza porque el cuerpo ahora se extiende detrás del menú; la prueba de paginación desplaza al final y comprueba que Cargar más queda encima del botón central antes de pulsarlo.

Se instala únicamente el paquete .visualdemo y se capturan pantallas nuevas del emulador: output/bienvenida-2026-11-21/pantallas. El APK QA real se compila aparte con API local; no se instala ni se presenta como probado contra Railway. La demo web usa el mock previo y no incluye los cambios privados50/51 del cliente real. Fotografías identificadas como ejemplos, nunca asignadas a animales reales.

Publicación: solo Sites demo v4, commit77eb14061b5d937142fb2c5f462673548762a93a, deployment appgdep_6b01b9473e1c8191b2f73b5e4411950f, resultado succeeded. https://little-paws-mobile-demo.e-rios48.chatgpt.site/. La inspección visual del navegador sigue pendiente: la herramienta de Computer Use se detuvo previamente al no identificar la URL; no se sortea esa limitación con otro automatizador. La comprobación de hosting procede de Sites y la visual de Android.

## Reparto

Majo: widgets y regresiones; Sally: guía/evidencia/criterios de diseño; José Carlos: backend intacto. No se modifica Railway ni se hacen commits, ramas o publicaciones en el repositorio oficial. El helper de Sites sí guarda la fuente del repositorio independiente de la demo para poder publicar su versión coherente.
