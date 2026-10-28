# Identidad del panel Little Paws Net

Los perfiles se definen en `profiles.json`: cada uno tiene un acento oscuro y una superficie clara. Seguridad usa salvia, el responsable secundario terracota y los gestores variantes cálidas de ocre/amarillo. El color acompaña al nombre del rol; nunca sustituye su etiqueta ni concede permisos.

## Iconos

Se instaló **lucide-static 1.62.0** mediante npm, con versión exacta y licencia ISC. Se generan 34 símbolos SVG locales; no se descarga la biblioteca completa en el navegador ni se usa una CDN.

```powershell
cd frontend/panel-design
npm ci --ignore-scripts
npm run build:icons
cd ../..
python frontend/panel-design/build-demo.py
```

`build-icons.mjs` crea el sprite y copia la licencia. `build-demo.py` aplica los temas y recursos a las 33 vistas de demostración existentes. Mantiene sus datos ficticios y módulos; no cambia permisos. Los recursos de bienvenida viven en `demos/panel-editorial/static/acceso/`; las ilustraciones y seis nubes proceden del Figma suministrado por el usuario.

## Django y demo

Las plantillas Django usan el mismo sprite mediante `icono.html`. `contexto.py` calcula `perfil_visual` usando únicamente roles vigentes obtenidos por el servidor y la organización activa. En cuentas con varios roles, aplica una prioridad visual estable: seguridad, moderación, responsables, gestores y veterinario. El preparador delegado tiene un tema propio. Esta prioridad solo elige la apariencia; las comprobaciones de autorización permanecen en los servicios del backend.

La demo pública permite escoger perfiles ficticios. Su formulario de ejemplo valida localmente `demo@example.invalid`, `DemoLittlePaws` y la suma 4+3. No autentica, no almacena contraseñas, no envía correos ni modifica cuentas. Los accesos directos a los perfiles son intencionados para revisar el diseño. El login real de Django sigue usando su propio desafío, sesión y controles de acceso.

## Bienvenida y estados

Scroll nativo, nubes visibles desde el inicio y capas independientes con desplazamiento suave. El contenido permanece accesible sin animación mediante `prefers-reduced-motion`; el formulario tiene etiquetas, foco, mensajes y cambio de visibilidad de contraseña. Los estados comparten el fondo, tipografía y tarjeta: datos incorrectos, validación, acceso pendiente, bloqueo temporal, sesión vencida, permiso insuficiente, recuperación, conexión y salida. La suma del cliente es solo una interacción de demostración; no es una defensa contra DDoS.

La marca del formulario se escribe completa como **Little Paws Net**, en una línea. En móvil, la tarjeta de propósito incorpora un encuadre del paisaje y el distintivo «Cuidar nos une»; mantiene la tipografía y el relieve del escritorio.

Los PNG y WebP del paisaje anterior y su ampliador se retiraron en la auditoría final: el acceso actual usa únicamente los dos fondos vectoriales originales. No se mantienen duplicados de exportación que el navegador ya no carga.

La portada adopta la jerarquía de la referencia de vídeo: antetítulo, titular monoespaciado, frase principal manuscrita, descripción y botón. Se incluye JetBrains Mono localmente con su licencia OFL. Las nubes 1, 5 y 6 tienen borde plano derecho; las 2, 3 y 4 se anclan al lado izquierdo. Entran desde ese lado con el scroll y conservan su posición al completar la entrada. El progreso se acumula: no hay tramo de salida ni retroceso al subir la página. La altura se recalcula al redimensionar y se respeta la preferencia de movimiento reducido.

El fondo conserva su proporción con `object-fit: cover`, sin `fill`. Las tarjetas de escritorio usan opacidades 0.86 (propósito) y 0.90 (acceso), con desenfoque de 14 px; móvil usa 0.92 para conservar legibilidad. El soporte de reducción de transparencia devuelve superficies opacas. Medidas y preparación del nuevo original: `docs/diseno/fondo-acceso-alta-resolucion.md`.

La fuente única del acceso es `frontend/panel-design/acceso.css`, copiada por `build-demo.py`; la página ya no carga `refinamientos.css`. El contenedor exterior ocupa todo el ancho incluso en 2K, y el contenido tiene límites independientes. El encabezado, la bienvenida, la marca decorativa, el acceso y el pie participan en el flujo normal. La altura del hero deriva del viewport y su contenido; no se fija a 900–1200 px. Las tarjetas comparten el borde superior y la izquierda se estira hasta el alto del formulario. Por debajo de 1000 px se apilan. Los controles para cambiar el perfil de demostración están en un desplegable nativo. La navegación del panel colapsa por debajo de 1024 px; la barra de la demo tiene una altura explícita de 56 o 104 px para no tapar el encabezado. La marca completa aparece también en las plantillas Django y en las 33 vistas estáticas.

### Fondo vectorial nuevo y entradas

En escritorio se usa **`fondo-escritorio.svg`**, copia íntegra del archivo `image 6 [Vectorized].svg` suministrado por el usuario: 3840 × 4574, 2531 trazados, sin bitmaps incrustados. Esta copia no pasa por el generador de recortes ni de WebP. Su ancho es fluido, la altura mantiene la proporción original y el contenedor reserva como mínimo el alto del lienzo completo. Se ancla por abajo para que, si el contenido requiere más altura, el espacio adicional quede arriba. Se respeta la zona superior libre del original. La variante móvil se documenta a continuación.

El pie queda después del contenedor ilustrado; las tarjetas disponen de al menos 88 px de separación inferior en escritorio y 72 px en móvil. La superficie visible puede ser mayor para mostrar completo el dibujo. Las nubes no se modifican en esta revisión.

Las entradas se coordinan con la carga de fuentes y página, con un límite de espera de 2 s. El antetítulo, las líneas del título, descripción y botón entran escalonados. La marca decorativa tiene una entrada propia de 1 s (opacidad, subida de 18 px y escala 0.985 → 1). Las tarjetas recuperan desplazamientos de 22–28 px, opacidad y desenfoque suaves; el nombre y los campos del login acompañan la entrada. Una vez terminadas, las transformaciones de las tarjetas vuelven a su posición normal. `prefers-reduced-motion` mantiene todo visible y estático.

El fondo completo también existe como recurso vectorial reutilizable en Figma (`157:24`). Las vistas de escritorio y los estados de acceso lo usan por instancia; los textos y controles siguen editables. Comprobación del SVG, proporción, margen inferior, fases de animación y recorrido de demo: `output/login-svg/revision.json`.

La revisión móvil incorpora `fondo-movil.svg`, copia íntegra del original `image 6 [Vectorized] (1).svg`: 1461 × 2560, 2531 trazados. Hasta 1000 px de ancho, el fondo principal conserva el lienzo completo y su proporción, anclado abajo sin recortes. La cabecera de la tarjeta de propósito muestra una vista decorativa del mismo recurso. En Figma se reutiliza el componente `162:24` en L04. Se mantienen las nubes y todas las entradas animadas. Verificación en seis tamaños, sin desbordamientos ni imágenes rotas, con recorrido de demo y animación comprobados: `output/fondo-movil/revision.json`.

## Verificación

La presentación de acceso también se conecta al formulario real de Django mediante `python frontend/panel-design/build-login-django.py`. Genera el HTML de acceso, copia únicamente los SVG/fuentes necesarios y reutiliza las entradas de las nubes. No copia datos de ejemplo ni valida contraseñas en el navegador: Django conserva la suma, CSRF, sesión y autorización. Ejecutarlo tras modificar la presentación de la bienvenida. La web pública de diseño sigue siendo una demo independiente.

Los informes y capturas de esta revisión se guardan en `output/identidad-acceso/`. Las 13 combinaciones de texto/acento para botones y encabezados comprobadas superan 4.5:1. Los estados semánticos de éxito/error conservan su paleta y no adoptan los colores de perfil. Las tarjetas de resumen y módulos usan crema, radio de 24 px, borde claro y sombra cálida; el relieve no reemplaza el foco ni la legibilidad.

La corrección de adaptación se revisó en 10 tamaños (320 × 640 a 2560 × 1350), incluyendo 1280 × 640 y 1366 × 650. Se comprobaron las 33 vistas en móvil, portátil y 2K, además del recorrido del formulario y la entrada unidireccional de las nubes: 121 comprobaciones sin errores detectados. Capturas e informe: `output/responsive-panel/`.
