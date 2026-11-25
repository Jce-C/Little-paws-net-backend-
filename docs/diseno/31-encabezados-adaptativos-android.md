# Encabezados de sección medidos en Android

## Hallazgo y corrección

Notificaciones y algunas confirmaciones conservaban AppBar de altura fija; otras vistas repetían una aproximación para dos líneas. Con la fuente monoespaciada del Figma y texto al 200 %, títulos largos podían quedar cortados. La corrección centraliza los encabezados de las pantallas secundarias en lib/design/lpn_app_bar.dart, conservando aparte la barra de marca del inicio.

Se usa la tipografía de sección del Figma, 15 sp, y TextPainter con la fuente y escala reales de Flutter. La medida reserva espacio para volver, márgenes, zonas seguras y acciones de icono existentes. El alto crece cuando el texto lo necesita. Los nombres extraordinariamente largos admiten hasta tres líneas y elipsis visual; el texto semántico conserva el nombre completo. La barra no ocupa una altura ilimitada que impida acceder al contenido.

Se aplica a acceso, registro, perfil, notificaciones, rescates/reportes, confirmaciones, mascotas, ficha y QR. Se eliminan las dos aproximaciones duplicadas de reportes y mascotas. No cambian rutas, tokens, permisos ni peticiones de red.

## Validación y límites

Cuatro pruebas nuevas verifican Notificaciones, Cambio confirmado y QR de la mascota a 320 px con texto al 200 %, el botón Volver y una ficha de nombre largo con acción de actualización en horizontal. Se comprueban los límites renderizados y la interacción, junto con la suite móvil completa. La comprobación nativa usa el APK normal con backend QA local, restaura la escala original del emulador y no autentica ni altera registros.

TalkBack y un dispositivo físico siguen pendientes. No se limita la escala elegida por la persona y no se reduce el texto mediante FittedBox.

## Reparto

María José: componente compartido, integración y test/app_bar_test.dart. Sally: guía y evidencia visual. José Carlos: revisión del contrato existente, sin cambios de backend ni migraciones.


Resultado final: 81 pruebas Flutter y análisis sin hallazgos. Capturas nativas 08-notificaciones-texto-200.png y 09-notificaciones-normal.png en output/fidelidad-figma-2026-11-19. validacion-encabezados-20261119.json confirma la escala 2.0 ensayada y la restauración de la original. El APK es debug QA, sin firma de publicación.
