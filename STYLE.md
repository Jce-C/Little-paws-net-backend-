# Little Paws Net · guía visual compartida

Actualización: 19 de noviembre de 2026. Aplica al panel web real y a la aplicación Android en Flutter.

## Dirección

Un panel tranquilo, claro y humano. Se conserva la composición editorial del [estilo de Refero compartido](https://styles.refero.design/style/031056ff-7af1-46db-8daa-115f731c5d26), refinada con la referencia «5 Color Palettes» suministrada por el usuario: crema y beige cálido, salvia sobria y acentos arcilla. La [app móvil original](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu?node-id=3-2) aporta el perrito, la crema #FCF0D3, el marrón #423222 y las formas suaves. Los controles del panel usan variantes más oscuras para garantizar legibilidad.

Los fundamentos de [TypeUI](.agents/skills/typeui-fundamentals/SKILL.md) guían jerarquía, agrupación, campos, foco y movimiento. Su aplicación no sustituye una revisión de accesibilidad con personas usuarias.

## Colores

| Uso | Valor | Variable CSS |
| --- | --- | --- |
| Bienvenida | #FCF0D3 | --lpn-cream / LpnColors.welcome |
| Resto de pantallas | #FFF9EC | --lpn-canvas / LpnColors.canvas |
| Superficie beige | #F7F0E1 | --lpn-surface |
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

- Inter local: Regular 400 para lectura; Medium 500 para etiquetas; Semibold 600–650 para jerarquía y acciones importantes. Texto de formularios de 16 px y lectura de 1.5–1.6.
- Leckerli One local, bajo el alias CSS `LPN Script`: marca y frase expresiva de bienvenida. No usarla en tablas, formularios o instrucciones extensas.
- Titulares operativos entre 24 y 32 px mediante `clamp`; secundarios entre 18 y 24 px. Los titulares expresivos de bienvenida admiten una escala mayor. Texto auxiliar normalmente de 14 px; evitar comprimir instrucciones para encajarlas.
- Espaciado: 4, 8, 12, 16, 24, 32, 48 y 64 px. Relacionar etiqueta y campo; separar grupos mediante más espacio.
- Tarjetas: radio 20 px; ilustraciones destacadas: 24 px; campos: 12–16 px; acciones: 16–18 px; filtros y pequeñas selecciones: píldora. Bordes suaves y sombra mínima.

## Componentes y comportamiento

El escritorio utiliza barra lateral y contenido amplio. En móvil, menú accesible y controles cómodos; las tablas pueden desplazarse dentro de su contenedor. Los iconos tienen texto o nombre accesible. Mantener foco visible y navegación mediante teclado. Evitar animar tablas y procesos de autorización.

La acción principal es salvia oscura con texto marfil; las secundarias usan borde y texto marrón. En hover, la principal se oscurece y las secundarias toman un beige suave. El estado pulsado es más profundo, el foco tiene un anillo marrón de 3 px separado del control, y el estado deshabilitado conserva un fondo visible y texto apagado. Botones principales con esquinas suaves; acciones dentro de tablas con radio de 12 px y altura mínima de 44 px.

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


## Actualización del panel real - 30 de octubre de 2026

La referencia Duna se adapta a una interfaz administrativa compacta: superficies cálidas, bordes sutiles, Inter y marca Leckerli One; se conserva la paleta LPN. No aplicar titulares de marketing ni huecos de 80-120 px a las tablas y formularios. Los formularios puntuales usan modales accesibles; las matrices y los listados permanecen en sus secciones. Los permisos binarios usan únicamente switches. Las excepciones conservan Heredar/Permitir/Denegar. No reintroducir el selector manual de color en accesibilidad. Más detalle en [panel compacto y modales](docs/diseno/10-panel-compacto-y-modales.md).


## Materiales y adaptación actual

La implementación nueva está en `backend-panel/seguridad/static/seguridad/materiales.css` y `frontend/mobile/lib/design/`. Se adopta Liquid Glass como principio de separación entre navegación y contenido, no como una simulación de las APIs nativas de Apple en Android o en CSS. Se limita el desenfoque a capas acotadas de navegación y acceso. Las tablas, expedientes, notas y formularios conservan superficies legibles. No se añaden filtros a cada tarjeta ni animaciones de desenfoque.

En web se usa `@supports` para habilitar `backdrop-filter`, con superficie sólida como alternativa. El contraste reforzado y las preferencias de transparencia/contraste del sistema retiran el efecto. En Android se respeta contraste alto/reducción de movimiento y se ofrece Apariencia → Reducir transparencias; esta preferencia se conserva localmente. No cambia roles, sesión ni permisos.

La bienvenida y el acceso están separados: en Android la bienvenida no consulta el catálogo hasta Explorar; se puede entrar o registrarse directamente. En web el login integra CSS, iconos e ilustración en su documento para conservar una sola petición inicial. La ilustración queda en un panel lateral de escritorio y se oculta en pantallas pequeñas. La jerarquía no depende de que el navegador soporte vidrio.

Guías consultadas: [Modern Web Guidance](https://github.com/GoogleChrome/modern-web-guidance), `responsive-design` y `form-factor-adaptation`; [Adopt Liquid Glass](https://github.com/psylch/adopt-liquid-glass-skill), fundamentos de TypeUI y el Figma móvil original. Ver [criterios y evidencia de esta revisión](docs/diseno/23-materiales-y-paleta.md).

## Fidelidad al móvil · 19 noviembre

La revisión vigente usa Inter para la interfaz Android y Leckerli One para el saludo. Conserva bienvenida #FCF0D3 y operación #FFF9EC, ilustraciones y marca originales. La revisión de controles del 20 de noviembre conserva tarjetas de lectura de radio 24 y barras de acciones de 28; campos/botones usan radio 15,5, crema/beige y sombras cálidas. La navegación principal vuelve a ser una franja de ancho completo, de radio 0, con selección discreta. Ver guía 44; estos valores sustituyen los radios 14/18 y la navegación flotante de la guía 41. La petición posterior autoriza esta evolución de fuente y jerarquía sobre el calco anterior. Vidrio solo en navegación/acciones y alternativa sólida. Ver docs/diseno/41-formularios-legibles-y-glass.md; la guía 28 describe una revisión anterior.


### Distinción de tipografía por superficie

El panel de gestión usa Inter, como los frames web 9:124 y 9:129; su saludo mide 2 rem y las cifras 2 rem con peso ligero. Android usa Inter desde la revisión de formularios legibles; el acceso web conserva su identidad tipográfica anterior. El resumen web usa cuadrícula sin carrusel, tarjetas crema opacas y paneles de lectura claros, respetando colores por perfil. Ver docs/diseno/37-dashboard-web-figma.md.


## Referencia móvil vigente · Stitch · 20 noviembre 2026

La nueva referencia y el documento integral del usuario reemplazan los radios 15,5 y la barra rectangular de la guía 44. Flutter usa controles 28, tarjetas orgánicas 32, titulares 30–38, cuerpo 16 y apoyo 14. Acentos mantequilla #F7D76B, rosa #EAD1CF y salvia, con navegación/CTA carbón #252525. Se conservan bienvenida #FCF0D3 y contenido #FFF9EC. No aplicar esta sustitución global al panel administrativo web. Menú de inicio con seis tarjetas, barra inferior de cuatro destinos y medallón completo del perro. Decoración fuera de las fotos y del área de lectura; movimiento reducido y alternativa sólida al vidrio. Ver guía 48, que distingue funcionalidad real y simulación de la demo.


## Ajuste de referencia vigente · barra y acceso

La guía49 reemplaza únicamente el acceso y el medallón de navegación de la guía48: login/registro vuelven al tema anterior aislado (radio15,5, crema y relieve). La navegación conserva cápsula oscura, pero ahora tiene hueco central real y botón blanco elevado de56. El perro lleva a Inicio; en Solicitudes cambia a más y abre selección de mascota. No volver a encerrar el medallón en el interior de la cápsula ni usar un círculo decorativo sin acción. Los demás componentes conservan Stitch.


## Ajuste vigente · bienvenida y barra · 21 noviembre

La guía52 sustituye la restauración del acceso de49: login y registro conservan Stitch (controles28 y CTA oscuro). La bienvenida usa entrada breve820ms, sombra ligera y acciones visibles sin scroll en tamaños ordinarios. Se conserva la cápsula con hueco y botón elevado; el contenido se extiende detrás de su silueta con espacio final de seguridad, sin corte rectangular. Las etiquetas tienen margen interior12; no reducir tipografía accesible para forzar encaje. Ver docs/diseno/52-bienvenida-y-barra-flotante.md y sus pruebas.


## Referencia móvil vigente · PDF y replicador · 21 noviembre

La guía56 sustituye radios, composición y acceso de48–52: campos14, botones18, tarjetas20–24, titulares28, cuerpo16 y apoyo14. Bienvenida #FCF0D3 y páginas #FFF9EC. Cabecera orgánica salvia en login/registro, ilustraciones limpias sin controles superpuestos, metadatos fuera de las fotos y temas sugeridos en formularios. La cápsula cóncava y el medallón funcional permanecen; iconos inferiores20 y etiquetas12, con objetivo táctil mínimo48. Vidrio limitado a navegación, alternativa sólida, movimiento reducido y entrada finita280ms. No modifica el diseño del panel administrativo web ni sobrescribe Figma. Ver docs/diseno/56-redisenio-referencias-visuales.md.


## Actualización58 · superficies y acceso

Acceso con onda Bézier a ancho completo, papel/salvia y campos agrupados. Inicio de fondo continuo y lectura fuera de la ilustración; tarjetas de capas con entrada escalonada460ms, anulada al reducir movimiento. FormCard agrupa identidad/redacción y montos. Metadatos del catálogo alineados al inicio. Perfil prioriza mascotas sobre roles. Contraste secundario corregido a655B4E. La guía58 actualiza56 y resuelve parte de57; no sustituye los contratos de datos pendientes ni cambia la estética del panel administrativo.


### Fotografías comerciales · guía59

En tarjeta y ficha de producto, usar la foto pública autorizada con ajuste contain, radios del sistema y nombre/precio fuera de la imagen. Mantener marcador explícito y reintento cuando corresponda. No sustituir productos reales por fotos genéricas. Formulario web nativo con confirmación, publicar/retirar y cancelar, sin publicación automática al seleccionar un archivo.


### Revisión60 · círculos y perfiles públicos

Las flechas de FeatureDeck se centran como hijas del círculo, nunca se alinean mediante otra fila. La ficha pública agrupa textos y contactos autorizados; la publicación requiere confirmación y envío explícito. Ver guía60.


### Revisión61 · cierre de identidad, marca, bienvenida e Inicio

Perro completo con hocico orgánico activo en assets/brand-organic.svg; original conservado. Fondo HomeBackdrop independiente de la lista, lectura con degradado protector y controles fuera del arte. Diálogos marfil, switches salvia y materiales sólidos sin sombra. Ver guía61 y registro porcentual de los14 puntos.


### Revisión62 · presentación de mascotas

Descripción, requisitos y cuidados fuera de la fotografía; atributos sobre etiqueta salvia suave, altura medida y texto ampliado. La solicitud repite cuidados públicos y conserva acciones fijas. Vacío explícito, nunca afirmar que no requiere cuidados si faltan datos. Ver guía62.


## Tarjetas: jerarquía de decisión

La guía63 fija imagen independiente, título dominante, datos secundarios por proximidad y una acción contextual. Adopción y productos reutilizan DecisionCard/DecisionAction; listas comparten ListTileTheme. Los formularios y publicaciones conservan su estructura propia. Ver [criterios y recorrido](docs/diseno/63-tarjetas-y-programas-ayuda.md). No uniformar alturas a costa de cortar texto o controles.


## Identidad de organizaciones

Logo64px con contain y espacio reservado; nombre20/700, tipo/ciudad secundarios y resumen breve. En320px o texto ampliado, logo sobre nombre completo. Contactos y servicios completos en pantalla propia; iconos de copia con etiqueta accesible. Sin marca publicada se usa un icono del tipo de organización. [Guía64](docs/diseno/64-directorio-logos-publicos.md).


## Comunidad y decisiones compactas

Priorizar autor/fecha, título, estado y una acción. Rescates usa dos columnas con altura natural y pasa a una con texto ampliado. Círculos de acción de al menos48px y etiquetas breves; contactos completos viven en la ficha de organización. Tienda alinea imagen112px a la izquierda, datos a la derecha; apila con texto ampliado. No usar separadores de punto medio para reunir título, estado y ciudad. [Guía65](docs/diseno/65-comunidad-fotos-y-rescates.md).


## Cierre tienda y referencias visuales ·22-11-2026

Tienda con fotos autorizadas, importe decimal exacto y comprobante del servidor; bienvenida/login según los SVG del usuario; accesos circulares de Inicio, reporte por etapas y retrato opcional en expediente protegido. Ver docs/diseno/66-tienda-fotos-y-pedido-trazable.md y docs/diseno/67-referencias-acceso-expediente-y-reporte.md. Implementación local; el punto14 conserva la aceptación en dispositivo y entorno real pendiente.

### Revisión 68
El vidrio se concentra en navegación. Contenido y pies de formulario conservan superficies tranquilas; sin cápsula decorativa adicional alrededor de acciones. Los puntos medios se sustituyen por puntuación natural. Movimiento/transparencia reducidos tienen variantes funcionales.

## Actualización móvil · 23 de noviembre

La app móvil adopta azul, amarillo, naranja y fondo cálido de la referencia nueva, suavizados y centralizados en `frontend/mobile/lib/design/lpn_theme.dart`. Esta paleta sustituye la salvia anterior en la app. El panel web conserva su tema existente. Revisar la guía 71 para composición, superficies y límites de aceptación.
