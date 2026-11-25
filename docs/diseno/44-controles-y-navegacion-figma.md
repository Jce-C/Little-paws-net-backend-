# Bordes, superficies y navegación Android según Figma

Revisión local del 20 de noviembre de 2026, a petición del usuario. Referencia móvil `sR48elLBOFINiQXIfwJsNu`: bienvenida `3:2`, acceso `5:7` y navegación de Adoptar `108:376`. Se consultaron contexto de diseño y captura de cada frame; se conservan los recursos vectoriales originales ya disponibles.

## Diferencias corregidas

La revisión anterior había convertido las acciones principales en superficies salvia planas y la navegación en una cápsula flotante. Esas diferencias eran decisiones de implementación; no eran necesarias para Android ni para conservar los permisos.

- Botones comunes: radio de 15,5, crema/beige con texto marrón y sombras cálidas. La acción principal conserva mayor peso/elevación que los secundarios. No se aplica transparencia al texto.
- Campos: mismo radio de 15,5, fondo crema y borde cálido. Al enfocar, el borde marrón se refuerza; los errores conservan texto y borde propios.
- Los campos elevados de acceso/perfil/gestión anónima y buscador pintan su sombra sobre los límites reales del control mediante `RaisedInputBorder`. El mensaje de error/ayuda queda fuera de esa sombra. No se calcula una altura fija que recorte el texto ampliado o los errores.
- Navegación principal: franja de ancho completo, sin márgenes de cápsula, con línea superior y vidrio de tonos crema. La pestaña actual usa peso y una marca pequeña, además de semántica de selección. Se conserva el logo central y los cuatro destinos reales.
- La página reserva espacio encima de la franja. La zona de gesto de Android queda protegida por SafeArea. Si el teclado ocupa espacio inferior (`viewInsets.bottom > 0`), la barra se oculta y vuelve con la misma selección al cerrarlo.

Tarjetas de lectura y grupos conservan radio 24; barras de acciones de formulario, radio 28. No se cambia la tipografía Inter aprobada en la revisión anterior, ni la marca/saludo originales. La bienvenida sigue en `#FCF0D3` y el resto en `#FFF9EC`. Los acentos de estados/iconos no se convierten todos al color del botón.

## Adaptaciones explícitas

El prototipo de acceso dibuja campos de 33 de alto. La app conserva controles operables y espacio para texto/iconos, con objetivos táctiles de al menos 48. El radio, color y sombra siguen la referencia; no se declara una copia de todas las coordenadas/tamaños del frame.

Con texto al 200 %, la navegación puede organizar sus destinos en dos filas para conservar etiquetas completas y áreas táctiles. No se reducen las letras para forzarlas dentro de una única fila. El contraste alto retira el efecto de campo elevado; Reducir transparencias mantiene las superficies de vidrio sólidas. Contrastes calculados: texto sobre botón crema 9,68:1 y borde de campo sobre su fondo 3,23:1. Esto no certifica accesibilidad global ni TalkBack físico.

La suma y recuperación de contraseña que aparecen en el frame no se simulan: siguen pendientes de contrato real. Esta revisión modifica presentación y comportamiento de navegación ante teclado; no cambia autenticación, permisos, peticiones o backend.

## Verificación

Pasan 139 pruebas Flutter y el análisis está limpio. Una regresión nueva verifica en Home real que la franja cubre el ancho, no se superpone al área del catálogo, desaparece con un inset de teclado y recupera la selección sin otra consulta. Las pruebas existentes cubren cuatro objetivos de 48, zona segura, texto al 200 %, acceso/registro, errores, sesión y adopción.

En Android se valida el formulario vacío sin enviar credenciales, la navegación y las cuatro pestañas al 200 %, restaurando escala 1,0. El teclado nativo de este emulador estaba en modo flotante y declaró inset inferior cero: en ese caso la franja permanece, porque ese teclado no ocupa el borde inferior. El caso de teclado inferior con inset positivo se comprueba en la prueba de widget; no se presenta el teclado flotante como evidencia de ese caso distinto.

Logs `flutter-controles-figma-20261120.log`, `analyze-controles-figma-20261120.log`, `build-controles-figma-20261120.log`. Capturas y hash del APK en `output/controles-figma-2026-11-20/`. El recorrido general del mosaico se actualiza con el APK vigente; `version.json` identifica su compilación y alcance. No se retocan las capturas ni se usan imágenes generadas.

## Reparto

María José recibe tema, borde reutilizable, navegación, ajuste de Home y prueba. Sally recibe guía, sistema visual y evidencias. José Carlos conserva la API sin cambios. Sin commits, ramas, despliegues o cambios en Railway. El emulador visible muestra el APK local; esto no publica una versión comercial.
