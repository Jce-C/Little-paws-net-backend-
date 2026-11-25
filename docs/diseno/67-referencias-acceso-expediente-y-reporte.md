# 67 · Referencias visuales del PDF y SVG

22 de noviembre de 2026. Fuentes: Referencias visuales.pdf (4 páginas), Login.svg y Myavoo - Onboarding Welcome Screen.svg aportados por el usuario. Se renderizaron y revisaron todos los documentos; no se ejecuta código de los adjuntos.

## Alcance solicitado

1. Inicio: cuatro accesos circulares reales sobre la cuadrícula; tarjetas con figuras de fondo, jerarquía más clara y controles de tamaño táctil. Se mantiene la flecha centrada en su círculo.
2. Expediente: retrato, nombre e indicador de atenciones agrupados; datos clínicos seleccionables y correcciones junto al original. La foto es opcional, no se inventa una imagen si falta autorización.
3. Reporte: tres etapas —Situación, Ubicación y Revisión/contacto— con Continuar/Anterior fijos, validación local por etapa y conservación de datos al retroceder. Solo Enviar reporte crea el registro. La búsqueda de ciudades mantiene su debounce. Salir con borrador pide confirmación; un resultado incierto bloquea el reenvío accidental.
4. Bienvenida/login: composición de las referencias en español, fotos integradas con transparencia, ondas procedurales, barras redondeadas, botón oscuro y nombre completo. Se conserva la paleta exacta de acceso; el resto de la app mantiene su paleta actual para el futuro cambio indicado por el usuario.

## Recursos de acceso

Las fotografías se extraen de los SVG del usuario y se optimizan a WebP con alpha; no se carga el SVG completo de2,7MB como pantalla. La foto de bienvenida conserva su marca de Dreamstime por petición expresa del usuario. No se elimina esa marca. El logo blanco conserva los huecos interiores; no se aplica un filtro que lo vuelva una silueta sólida.

Welcome: #F5B738/#FAD574/#FCE39E; panel #FFFDF9; acción #2E2738. Login: base #FCD78A, onda superior #F9CB57, onda inferior #EFAB28, campos #795701, texto cálido claro y botón #2E2738. Estos colores están limitados a las pantallas de acceso, no se reemplaza globalmente el sistema de temas.

Con texto ampliado se incrementa el espacio real del título y se permite desplazamiento; no se superponen foto, texto o acciones. En tamaños habituales la bienvenida mantiene sus accesos visibles. Los controles conservan foco, etiquetas accesibles, autofill y reducción de movimiento.

## Acceso y privacidad

Recordarme permite optar por almacenar la sesión en el almacenamiento seguro nativo. El navegador conserva la política de sesión solo en memoria; allí se explica y deshabilita esa opción. El botón de ayuda de contraseña describe el procedimiento asistido actual. No se simula un envío de correo: la recuperación automática por correo sigue pendiente.

La miniatura del expediente se incorpora dentro de la respuesta médica ya autorizada: WebP160px y32KB como máximo, sin URL pública nueva, sin otra petición de imagen y con Cache-Control:no-store. Solo se reutiliza la fotografía autorizada del custodio vigente/último; un nuevo custodio no hereda la foto del anterior. La retirada impide volver a mostrarla. Los cambios de cuenta descartan la vista privada mediante la protección existente de sesión.

## Evidencia

Los PNG *implementado* y los renders de superficies proceden de widgets Flutter reales mediante pruebas; no son capturas del emulador. CUA y Node reportaron Transport closed, por lo que no se afirma una inspección manual del navegador ni una prueba física de TalkBack. Las comprobaciones HTTP locales, pruebas de permisos y validaciones de tamaño/texto se registran en sus logs.

La validación integral del punto14 permanece parcial hasta comprobar dispositivo físico/emulador, TalkBack, aceptación visual humana y el backend real integrado. El progreso de la tabla es13/14=92,86%, aunque las correcciones visuales de este documento se implementen.
