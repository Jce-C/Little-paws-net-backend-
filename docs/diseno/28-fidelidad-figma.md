# Fidelidad al Figma móvil · revisión local

19 de noviembre de 2026. Sin commits, publicación ni cambios en Railway.

## Referencia comprobada

Se leyó el archivo original `sR48elLBOFINiQXIfwJsNu` mediante contexto de diseño y capturas, no solo la miniatura general:

- `3:2`: bienvenida, logo negro de 128 × 142,726, marca monoespaciada, saludo Leckerli One y controles crema con sombra.
- `5:7`: login, símbolo marrón de 92 × 104, tipografía JetBrains Mono, campos redondeados con sombra cálida.
- `108:376`: catálogo, imágenes de 107 × 114, texto separado debajo, título centrado e ilustración existente.
- `156:1796` y `156:1924`: perfil, tarjetas crema, acentos beige, contornos claros y paneles elevados.
- El archivo del panel `Kv2Na4SBOxyGoQ4tC8CMxR` mantiene su organización administrativa; se extiende el acabado del móvil a sus componentes existentes.

La versión anterior interpretó la identidad con Inter, botones salvia y superficies casi planas. Esta revisión devuelve JetBrains Mono y sombras cálidas visibles. Las capturas de referencia se guardan únicamente como evidencia; no se utilizan como fondos de la aplicación.

## Implementación

Android: tema común para tarjetas, botones, campos, menús de apariencia y diálogos. Los formularios de acceso, registro, perfil, reportes y solicitudes usan la misma superficie de entrada. La bienvenida vuelve a la composición original; la exploración pública sigue accesible mediante un enlace secundario. El catálogo separa fotografía y metadatos. Las imágenes de mascotas siguen dependiendo de la API y del permiso de publicación; no se sustituyen registros reales por los animales del mockup.

Web: tokens comunes para tipografía, sombra y transparencia. Se actualizan navegación, indicadores, formularios, paneles y ajustes existentes. El login integra la fuente local en el documento para conservar una única petición inicial. Las tablas conservan una base sólida, los colores de usuario, el menú dinámico y el comportamiento RBAC.

La transparencia afecta a la superficie y no al texto. Contraste reforzado o reducción de transparencias mantienen fondos sólidos. Los controles conservan objetivos táctiles de 48 dp en Android y sus estados de foco. El diseño se adapta al texto ampliado, teclado y tamaños pequeños mediante desplazamiento de contenido.

## Alcance visual

Se reproduce el lenguaje visual del archivo y las composiciones consultadas. No se declara que todas las pantallas tengan una coincidencia píxel a píxel: hay pantallas funcionales sin equivalente en Figma, controles de accesibilidad, datos dinámicos y navegación ciudadana ya implementada. Tampoco se simulan opciones sin backend. El desafío de acceso del panel permanece en el panel; esta revisión no inventa un CAPTCHA móvil.

## Verificación

Evidencia: `output/fidelidad-figma-2026-11-19/` en el espacio de trabajo, con capturas directas de Android, navegador y referencias exportadas. Pruebas automatizadas de flujos móviles y texto al 200 %, regresión del panel/preferencias, revisión de desbordamientos a 320, 390, 1366 y 2560 px y Axe en claro/oscuro sobre el dashboard revisado. El resultado automatizado no certifica accesibilidad de toda la aplicación.

Se añadió espera de renderizado tras el desplazamiento en dos pruebas de navegación; evita pulsar coordenadas antiguas al cambiar el tamaño del contenido. No se eliminan comprobaciones de comportamiento.

## Guía web utilizada

Modern Web Guidance `css`: se reutilizan las variables CSS del sistema y se delimitan los selectores a las superficies del producto, sin reset global. Regla aplicada: “Use CSS custom properties on :root to define core design variables”.

## Reparto

María José: Flutter, recursos originales, fuentes/licencias y pruebas móviles. Sally: estilos/plantilla web y documentación visual. José Carlos: revisión de integración y regresión; no hay migraciones ni cambios de permisos.
