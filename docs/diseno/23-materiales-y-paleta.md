# Materiales y paleta compartida

Revisión local del 19 de noviembre de 2026. Sin commits ni publicación.

## Decisiones de diseño

| Elemento | Aplicación |
| --- | --- |
| Bienvenida | Fondo exacto `#FCF0D3`, en web y Android. |
| Pantallas operativas | Fondo base `#FFF9EC`, en web y Android. El modo oscuro del panel conserva una base neutra. |
| Navegación | Material translúcido acotado, borde suave, selección visible y nombre accesible. |
| Lectura y edición | Tarjetas sólidas, texto opaco y campos con borde identificable; tablas sin desenfoque. |
| Tipografía | Inter para interfaz; Leckerli One para la marca y bienvenida. Fuentes locales con licencias OFL. |
| Acciones | Principal salvia, secundarias con borde, acciones menores de texto. Áreas táctiles de 44 px en web y 48 dp en Android. |
| Roles | Se conservan la selección de color existente y los permisos. Esta revisión no cambia el RBAC. |

Se usaron los fundamentos de TypeUI, [Modern Web Guidance](https://github.com/GoogleChrome/modern-web-guidance) y [Adopt Liquid Glass](https://github.com/psylch/adopt-liquid-glass-skill). La referencia móvil es el [Figma original, bienvenida 3:2](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu/Untitled?node-id=3-2). Se reutilizan logo, ilustraciones y fuentes existentes; no se generaron imágenes con IA.

Liquid Glass se adopta como separación de una capa funcional sobre el contenido. Android usa materiales Flutter y filtros acotados; la web usa CSS. No se afirma que estas implementaciones ejecuten las APIs exclusivas de SwiftUI/UIKit/AppKit. No se añaden shaders ni librerías de efectos pesadas.

## Android

- `lib/design/lpn_theme.dart`: colores, tipografía, controles, tarjetas y material común.
- `lib/design/welcome_screen.dart`: bienvenida, exploración pública, acceso y registro directos. Abrirla no consulta el catálogo.
- `lib/design/lpn_navigation.dart`: navegación flotante; con texto ampliado en pantallas estrechas se organiza en dos filas para conservar los nombres completos.
- Apariencia → Reducir transparencias aplica una superficie sólida y conserva la preferencia en el dispositivo. Contraste alto y reducción de movimiento también retiran el desenfoque. Un fallo del almacenamiento no impide usar la app.
- El login se centra cuando hay espacio y sigue desplazándose cuando lo necesita el teclado o el texto ampliado. El resto de las pantallas hereda el sistema común.
- El icono de Android se exportó del SVG original del perrito; arranque y bienvenida comparten el crema.

Los ensayos anteriores pueden usar `showWelcome: false` para concentrarse en su flujo. `lib/main.dart` y `integration_test/design_android_test.dart` prueban la entrada normal con bienvenida.

## Panel web

- `seguridad/static/seguridad/materiales.css` contiene la capa compartida, cargada después de los estilos existentes.
- `tokens.css` y `tema.css` declaran el lienzo nuevo. La clase `lpn-welcome` delimita el color de bienvenida.
- La barra superior sigue visible al desplazarse. La selección y agrupación lateral mantienen nombres, cantidades y accesos dinámicos.
- El login usa dos columnas en escritorio: relato/ilustración y formulario. En móvil presenta directamente el formulario. La ilustración conserva la configuración de posición/opacidad/velo.
- El CSS del login se integra mediante la lista de recursos públicos permitidos. No se añade una petición de hoja de estilos al acceso.
- `@supports` habilita el desenfoque como mejora progresiva; sin soporte, permanece la superficie sólida. Contraste reforzado, preferencias de contraste/transparencia y colores forzados retiran el efecto.
- Las filas alternas y las selecciones tienen variantes oscuras, sin texto claro sobre filas claras. El foco dispone de margen respecto a las barras fijas.

## Guías aplicadas

- **responsive-design**: se combinaron `rem` y unidades relativas en `clamp()` para no reducir la interfaz al ampliar texto; las imágenes reservan su espacio y las superficies evitan alturas rígidas con contenido textual.
- **form-factor-adaptation**: se mantuvieron objetivos táctiles, nombres de iconos, márgenes de foco y áreas seguras; se permite desplazamiento dentro de tablas bidimensionales sin ensanchar la página.
- [`backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter): se filtra una capa delimitada con fondo parcialmente transparente, con alternativa sólida.
- [`prefers-reduced-transparency`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency): la detección del sistema es una mejora adicional; el contraste reforzado ofrece una alternativa manual compatible.

## Evidencia y límites

`output/diseno-materiales-2026-11-19/` contiene capturas del navegador y capturas directas del APK normal en Pixel 6a. Los datos son sintéticos de MySQL QA local, sin cambios de negocio. Las mascotas sin foto pública autorizada siguen usando un marcador.

Se comprobaron 61 pruebas Flutter, análisis sin hallazgos, el recorrido nativo de bienvenida/acceso/apariencia y 63 pruebas del panel/RBAC. En navegador se revisaron 320, 390, 1366 y 2560 px, temas claro/oscuro, contraste reforzado y ausencia de peticiones adicionales al cargar el login. Axe no detectó infracciones en las cuatro pantallas representativas revisadas en ambos temas; esto no es una certificación de toda la aplicación.

Permanecen pendientes la validación con TalkBack y un dispositivo físico, mediciones de rendimiento en equipos modestos y el proceso de publicación/firma. Los nuevos materiales no autorizan ni simulan fotografías, atenciones clínicas o acciones de negocio.

## Reparto

María José: sistema visual Android, recursos, fuentes y pruebas móviles. Sally: estilos e integración de plantillas web, guía visual y evidencias. José Carlos: revisión de la integración con el backend y ejecución del conjunto de regresión; no se requiere una migración nueva.

## Corrección posterior de fidelidad

La revisión descrita arriba fue una interpretación del estilo. La revisión 28 la sustituye en tipografía y acabado: JetBrains Mono, sombras cálidas visibles y campos crema translúcidos, conforme al Figma original. Ver [fidelidad](28-fidelidad-figma.md).
