# 87. Teclado, foco y validación adaptativa

Bloque local del 25 de noviembre de 2026. Continúa Q01/Q02 de la guía 75. Estado global: **49/57 (86,0 %)**. No se cierran estos dos criterios completos con una prueba parcial.

## Problema y cambio

Los pies colocados en `Scaffold.bottomNavigationBar` no se desplazan automáticamente sobre el teclado como el cuerpo del formulario. Eso podía ocultar guardar, enviar o cancelar. Se centralizó el tratamiento de `viewInsets.bottom` en `LpnKeyboardSafeArea` y se añadió `avoidKeyboard` a `LpnActionBar`.

Se aplicó en diez pies: publicaciones/interés, convocatoria de voluntariado, gestión de ayudas de organización, producto, pedido, compromiso de aporte, avatar, mascota personal, apadrinamiento y detalle de reporte. Los pies dentro del cuerpo conservan el comportamiento anterior; añadirles otro inset dejaría un hueco doble.

En horizontal, un teclado nativo muy alto puede dejar menos de 180 píxeles lógicos para la aplicación. En ese caso se reserva el espacio para editar y se oculta temporalmente el pie; cerrar el teclado restaura las acciones sin perder el borrador. Esta excepción surgió en el emulador y tiene prueba de regresión propia.

No se modificaron permisos, endpoints, persistencia, textos legales ni la paleta. La implementación compartida y su nueva prueba coinciden en el cliente oficial y las dos demos.

## Verificación

- Suite completa final del cliente: **317 aprobadas y nueve optativas omitidas**.
- Nueve casos nuevos: mascota y publicación en 320×640 con texto al 200 %, horizontal 800×360 y tablet 800×1280; teclado simulado de 120–320 px; pie dentro del cuerpo sin doble desplazamiento; Tab contenido en la confirmación y Escape conservando el borrador; teclado horizontal alto y recuperación al cerrarlo. Ninguno envía una operación de negocio.
- Cada demo: **28 pruebas focales aprobadas**. Análisis estático limpio en las tres copias.
- Android: APK de demo compilado e instalado en AVD Pixel_6a_2 de solo lectura, aislado del dispositivo de trabajo. Wi-Fi y datos deshabilitados; backend ficticio en memoria. Se observó el IME nativo y el botón Enviar sobre él, conservando el texto escrito. Esto no prueba una escritura en el backend real.
- La demo web se compila desde `sites/little-paws-mobile-demo`. La copia `demos/mobile-visual` es el destino Android y no contiene plataforma web; no se le genera una plataforma nueva solo para esta validación.
- Backend sin cambios en este bloque; se conserva la evidencia anterior de 468 pruebas. No se repite una suite ajena a la modificación.

Comando focal: `flutter test test/keyboard_accessibility_test.dart --no-pub --reporter expanded`.

Evidencia local: `output/correcciones-app-2026-11-25/teclado-foco/`. Las capturas que comienzan con `emulador-` provienen del Android real emulado y muestran la banda de demo. Las dimensiones de las pruebas automatizadas están expresadas en píxeles lógicos.

## Criterios que permanecen abiertos

Q01 requiere aceptación integral en dispositivos, orientación y apariencia; este bloque comprueba una selección de formularios y no todas las pantallas. Q02 conserva TalkBack, recorrido completo con teclado y aceptación en teléfono físico. No se declara conformidad WCAG por pasar pruebas de widgets.

Continúan S04, S05, S08, S12, Q03 y Q10 con sus dependencias documentadas. La siguiente intervención debe ampliar la matriz a los otros pies cambiados y revisar el recorrido de foco y semántica, conservando pruebas y evidencia válidas. Los adjuntos privados de adopción no se deben volver obligatorios sin resolver D02.

## Integración y entrega

Todo permanece local, sin commits, push, despliegue ni servicios de pago. Los paquetes actualizados se guardan en `output/correcciones-app-2026-11-25/teclado-foco/paquetes`; incluyen los cambios acumulados sobre la base Git, por responsable, y requieren aplicar el conjunto en una copia de validación antes de preparar commits.
