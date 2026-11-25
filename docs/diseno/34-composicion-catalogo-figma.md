# Catálogo Android: composición del Figma original

Referencia: https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu/Untitled?node-id=108-376

Se revisó el contexto detallado y la captura del frame 108:376 antes de ajustar la composición. El encabezado ADOPTAR queda centrado; la cantidad de resultados se apila cuando no cabe. La ilustración existente mantiene su versión WebP local de 102 376 bytes. Los filtros se sitúan sobre el borde inferior del banner con áreas táctiles amplias. Seleccionar el filtro activo no vuelve a consultar el catálogo.

La cuadrícula conserva imágenes de 107 × 114 puntos lógicos y reduce el espacio entre filas. La altura se calcula con los nombres, resúmenes y escala de texto efectivos. Con texto ampliado se usa una columna; no se reduce la preferencia del sistema para forzar la composición.

## Verificación local

- 102 pruebas Flutter aprobadas; análisis sin incidencias.
- APK debug construido e instalado en el emulador ya abierto.
- Capturas reales 12-catalogo-composicion-figma.png y 13-catalogo-texto-200.png en output/fidelidad-figma-2026-11-19; escala original 1.0 restaurada.
- Los registros de QA carecen de fotografías públicas: se muestra el estado sin imagen. No se sustituyen por las mascotas ilustrativas del Figma.
- Backend, permisos y datos de producción sin cambios en este bloque.

## Diferencias pendientes

Esta revisión no certifica fidelidad de todas las pantallas. La revisión posterior de navegación y ficha se documenta en la guía 35. El material de cabecera y las composiciones de perfil y formularios todavía deben compararse individualmente con sus frames originales. Se conservan las cuatro funciones actualmente implementadas; no se añade una tienda ficticia para imitar el menú del prototipo.

El alcance confirmado por el usuario es toda la app y el panel web, no únicamente Apariencia. Figma define la composición y los materiales; los efectos de plugins deben adaptarse a esa referencia. Las capturas y medidas de este documento corresponden solo al catálogo Android.

## Repartición sin commits

María José: componentes y pruebas Android. Sally: comparación y evidencia visual/documentación. José Carlos: no hay cambios de API en este bloque. Todo sigue en local; no se publica ni se crean commits.
