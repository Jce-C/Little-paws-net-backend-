# Little Paws Net · guía visual compartida

Actualización: 27 de octubre de 2026. Aplica al panel web y sus adaptaciones móviles; el diseño original de la aplicación ciudadana conserva su alcance.

## Dirección

Un panel tranquilo, claro y humano. Se conserva la composición editorial del [estilo de Refero compartido](https://styles.refero.design/style/031056ff-7af1-46db-8daa-115f731c5d26), refinada con la referencia «5 Color Palettes» suministrada por el usuario: crema y beige cálido, salvia sobria y acentos arcilla. La [app móvil original](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu?node-id=3-2) aporta el perrito, la crema #FCF0D3, el marrón #423222 y las formas suaves. Los controles del panel usan variantes más oscuras para garantizar legibilidad.

Los fundamentos de [TypeUI](.agents/skills/typeui-fundamentals/SKILL.md) guían jerarquía, agrupación, campos, foco y movimiento. Su aplicación no sustituye una revisión de accesibilidad con personas usuarias.

## Colores

| Uso | Valor | Variable CSS |
| --- | --- | --- |
| Lienzo crema | #F7F2E7 | --lpn-canvas |
| Superficie beige | #F0E8D9 | --lpn-surface |
| Tarjeta marfil | #FFFDF7 | --lpn-paper |
| Separador decorativo | #DDD4C4 | --lpn-stone |
| Texto principal | #332D26 | --lpn-ink |
| Texto de apoyo | #514B40 | --lpn-body |
| Texto secundario | #696356 | --lpn-muted |
| Acción principal salvia | #4F6655 | --lpn-primary |
| Hover / pulsado principal | #405644 / #344738 | --lpn-primary-hover / --lpn-primary-active |
| Arcilla | #805D46 | --lpn-clay |
| Navegación / selección | #ECEFE3 / #E2E9DA | --lpn-sidebar / --lpn-sage-soft |
| Cabecera / texto de cabecera | #DDE5D6 / #354B3B | --lpn-table-head / --lpn-table-ink |
| Fila alterna / hover de fila | #F8F4EA / #EEF2E6 | --lpn-row-alt / --lpn-row-hover |
| Marrón de marca | #423222 | --lpn-brown |
| Crema / arena / salvia | #FCF0D3 / #DDC5AB / #B2CD99 | --lpn-cream / --lpn-sand / --lpn-sage |
| Foco / borde de campo | #705035 / #8A8879 | --lpn-focus / --lpn-input |
| Error / fondo de error | #933E32 / #FBEFEB | --lpn-danger / --lpn-danger-bg |

Los separadores tenues no sirven como único límite de un campo. Los estados llevan texto e icono además de color. No usar salvia o arena como texto pequeño sobre blanco. Comprobar el contraste después de introducir transparencias o imágenes.

## Tipografía y ritmo

- Inter local: Light 300 para titulares grandes; Regular 400 para lectura; Medium 500 para acciones y etiquetas importantes. Texto de formularios de 16 px y lectura de 1.5–1.6.
- Leckerli One local, bajo el alias CSS `LPN Script`: marca y frase expresiva de bienvenida. No usarla en tablas, formularios o instrucciones extensas.
- Titulares de página entre 32 y 48 px mediante `clamp`; secundarios entre 22 y 28 px. Texto auxiliar normalmente de 14 px; evitar comprimir instrucciones para encajarlas.
- Espaciado: 4, 8, 12, 16, 24, 32, 48 y 64 px. Relacionar etiqueta y campo; separar grupos mediante más espacio.
- Tarjetas: radio 20 px; ilustraciones destacadas: 24 px; campos: 8 px; botones y selección de navegación: píldora. Bordes suaves y sombra mínima.

## Componentes y comportamiento

El escritorio utiliza barra lateral y contenido amplio. En móvil, menú accesible y controles cómodos; las tablas pueden desplazarse dentro de su contenedor. Los iconos tienen texto o nombre accesible. Mantener foco visible y navegación mediante teclado. Evitar animar tablas y procesos de autorización.

La acción principal es salvia oscura con texto marfil; las secundarias usan borde y texto marrón. En hover, la principal se oscurece y las secundarias toman un beige suave. El estado pulsado es más profundo, el foco tiene un anillo marrón de 3 px separado del control, y el estado deshabilitado conserva un fondo visible y texto apagado. Botones principales en píldora; acciones dentro de tablas con radio de 12 px y altura mínima de 44 px.

Las tablas usan encabezados salvia claros, texto de 13 px seminegrita, celdas de 14 px, separadores de 1 px y filas marfil/crema alternadas. Nombre y título destacan en seminegrita; los campos numéricos configurados se alinean a la derecha con cifras tabulares. No añadir líneas verticales innecesarias. La fila bajo el cursor o con foco interior adopta salvia muy clara. El contenedor admite desplazamiento horizontal por teclado en móvil.

Una acción peligrosa explica su efecto y conserva su confirmación. Los diálogos tienen título, cierre accesible y contexto del registro. Una ilustración acompaña el inicio o un estado vacío; no ocupa el espacio necesario para trabajar.

La comprobación de colores renderizados dio 6.14:1 para el botón principal, 7.32:1 para encabezados de tabla y 5.34:1 para texto secundario sobre crema. Las diez combinaciones representativas verificadas superaron 4.5:1. Informe: `output/estilo-salvia/verificacion.json`. Esto verifica esas combinaciones, no certifica toda la accesibilidad de la aplicación.

[Guía editable de estados, paleta y tabla en Figma](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=104-6).

## Roles y alcance

El diseño presenta únicamente módulos autorizados, organización vigente y alcance del registro. Ocultar un botón no concede ni revoca permisos: Django vuelve a comprobarlos en cada petición. El administrador de seguridad no obtiene acceso clínico o financiero por el aspecto de la interfaz. Mantener las reglas aprobadas en `docs/rbac/` y no deducir permisos de estas imágenes.

## Recursos

El logo viene del diseño original; las ocho ilustraciones proceden del ZIP suministrado por el usuario. Las copias WebP viven en `backend/seguridad/static/seguridad/ilustraciones/`; conservar su relación de aspecto, sin ampliaciones que prometan detalle inexistente. Para ilustración decorativa usar `alt=""`; para contenido informativo escribir una alternativa útil. Fuentes y sus licencias se incluyen en `static/seguridad/fonts/`.

La bienvenida publicada usa ahora el paisaje y las seis nubes vectoriales de la composición aprobada en Figma (`C1R4sX8yAYS57FbgXPOBA7`, nodo `22:6463`). Las nubes están visibles desde la primera portada; el scroll desplaza las capas y revela propósito y formulario. El gesto permanece nativo y `prefers-reduced-motion` conserva todo el contenido sin desplazamientos animados. La demostración anterior basada en `FONDO.svg` permanece como referencia histórica aislada.

El paisaje del acceso se suaviza en contraste y saturación, con un original ampliado convencionalmente desde 768 × 1376 hasta 2304 × 4128 px; esta ampliación no añade detalle original. La web sirve variantes WebP mediante `srcset`. La marca se muestra completa en una línea como «Little Paws Net». El acceso móvil conserva la composición de tarjetas de escritorio y añade una cabecera ilustrada con el distintivo «Cuidar nos une».

La portada combina JetBrains Mono (antetítulo, primera línea y descripción) con Leckerli One (frase principal), siguiendo la referencia de vídeo. Las nubes conservan su borde plano fuera del encuadre, solo entran con el scroll y permanecen en su posición final. El fondo se encuadra con `cover` en una sección de acceso independiente para mantener su proporción. Propósito y acceso admiten una transparencia leve y desenfoque de 14 px; los campos mantienen su fondo claro. La especificación del próximo fondo está en `docs/diseno/fondo-acceso-alta-resolucion.md`.

El exterior de la bienvenida ocupa todo el ancho, sin un corte interno a 1920 px. Su tipografía se adapta al ancho y a la altura disponible. La marca decorativa y el acceso siguen el flujo normal, y las tarjetas se alinean por arriba. En el panel se escribe siempre «Little Paws Net» completo; el contenido dispone de un ancho máximo independiente y la navegación se pliega a 1024 px. La corrección se verificó en 10 tamaños y las 33 vistas del panel, con capturas en `output/responsive-panel/`.

La revisión actual sustituye el fondo de escritorio por el SVG íntegro suministrado, `fondo-escritorio.svg` (3840 × 4574), conservando las nubes. Se respeta todo el lienzo y su espacio superior, sin usar los recortes de la imagen anterior en escritorio. El nombre decorativo, los textos y las tarjetas tienen entradas suaves de nuevo; al final conservan su posición normal. El pie está separado de las tarjetas por un mínimo de 88 px en escritorio y 72 px en móvil, con espacio adicional cuando lo necesita la ilustración completa. El movimiento reducido ofrece una composición estática.

## Identidad por perfil e iconos

Los 13 perfiles tienen acentos distintos definidos en `frontend/panel-design/profiles.json`. Seguridad usa verde salvia; el responsable secundario, naranja terracota; los gestores, variantes de amarillo y ocre. Los acentos se aplican a botones, navegación, iconos y encabezados. Las superficies conservan el fondo crema y los estados de éxito/error mantienen colores semánticos independientes. El nombre del rol siempre acompaña al color.

Se instaló `lucide-static` 1.62.0, con bloqueo de versión y licencia ISC. El sprite contiene 34 SVG locales; los rombos de navegación, resumen y módulos se sustituyeron por iconos asociados a cada recurso. El sitio no necesita una CDN de iconos. Las tarjetas crema usan radio de 24 px y relieve cálido moderado, siguiendo la referencia móvil suministrada.

Las 26 combinaciones comprobadas de acento/texto de los 13 perfiles (botones y cabeceras) superan 4.5:1. Informe: `output/identidad-acceso/contraste-iconos.json`. Esto no sustituye una auditoría completa de accesibilidad.

## Archivos y alcance de la entrega

El acceso usa originales SVG independientes: escritorio 3840 × 4574 (`fondo-escritorio.svg`) y móvil 1461 × 2560 (`fondo-movil.svg`, hasta 1000 px). Ambos conservan la proporción y el lienzo completo en el fondo principal. La cabecera ilustrada móvil es una vista decorativa del mismo original vertical. Las nubes y las animaciones permanecen en capas independientes.

- `backend/seguridad/static/seguridad/tokens.css`: valores compartidos y alias de compatibilidad.
- `backend/seguridad/static/seguridad/sistema.css`: estilo aplicado a las plantillas reales de Django.
- `demos/panel-editorial/`: vistas de consulta con datos ficticios; no escribe en la API.
- `demos/login-entrada/`: demostración aislada del scroll; no autentica.
- `docs/diseno/`: inventario y enlace al Figma editable. Sus 120 vistas incluyen bocetos de formularios futuros; no equivalen a 120 formularios web implementados.
- `output/kit-capas-little-paws/`: SVG, PNG transparentes, guía y composición de referencia.

Al cambiar un componente, actualizar sus tokens, su equivalente en Figma y sus estados de escritorio/móvil. No copiar las páginas estáticas de la demo al backend: se regeneran a partir de las plantillas, con contextos ficticios.
