# Actividad y auditoría: explicar los eventos recientes

Dashboard y auditoría mostraban códigos técnicos como descripción de las operaciones nuevas de fotografía. Se añaden textos compartidos para publicación, reemplazo y retirada de fotos, actualización de contacto y envío de solicitud de adopción. Se reconocen también los códigos históricos de fotografía en singular. Solo se describe una solicitud enviada si la operación registrada indica solicitar-adopcion; no se confunde con aprobación o cambio de titularidad.

Las operaciones fallidas y rechazadas se explican sin inventar su causa. Si consta un estado HTTP válido, se muestra en el detalle. Un error de respuesta no demuestra por sí solo que se hayan revertido cambios. Los códigos originales siguen visibles al final del detalle y no se reescriben los registros.

Se muestra información adicional limitada: dimensiones/tamaño de la foto, nombres de los campos de contacto actualizados y estado HTTP. No se copian payloads, claves de almacenamiento, teléfonos ni valores personales a esa descripción. Se conserva el antes/después registrado, sin inventar datos que faltan. El resultado del detalle usa su texto traducido en lugar del código EXITO.

## Validación

- 27 pruebas Django aprobadas en esquema MySQL local de pruebas nuevo y destruido al finalizar. Incluyen nueve nuevas de presentación/privacidad, alias históricos, traducción, descripción coherente entre dashboard y detalle, conservación del código y denegación de auditoría al ciudadano. Se mantienen las pruebas de auditoría de creación de solicitudes y edición de perfil.
- Navegador QA: dashboard, auditoría y apertura de detalle en español e inglés con eventos sintéticos ya existentes. Capturas 28 y 29 en output/fidelidad-figma-2026-11-19; log, JSON y ejecución Django en output/adopcion-movil.
- Se actualizó exclusivamente el servidor ASGI local tras identificar su proceso y se renovaron sesiones sintéticas. No se alteraron roles, fotos, solicitudes ni registros de negocio para fabricar evidencia.

Sally recibe el presentador, dashboard, fila de detalle, pruebas y traducciones finales en el módulo 03. Copiar los PO/MO finales después de aplicar los parches anteriores. José Carlos y María José conservan sus módulos: no cambian autorización ni contrato móvil. APK/115 pruebas corresponden al bloque Android anterior. Sin commits ni publicación.

Pendiente: ampliar las descripciones de otros eventos históricos que aún usen el texto genérico; continuar listados/formularios web y rescates móvil. Las pruebas no certifican todo el producto ni sustituyen TalkBack, dispositivo físico, firma o rendimiento en preproducción.
