# Creación de reportes por etapas

24 de noviembre de 2026. Cierre local de R09/R10 de la guía 75. Continúa las guías 77/78 con los mismos fundamentos de jerarquía, proximidad, tipografía, controles, privacidad y contraste. Sin commits, publicación ni recursos de pago.

## Recorrido y decisiones

1. **Situación:** tipos reales del catálogo, selección inequívoca, descripción pública y foto opcional. La ayuda cambia para una situación de pérdida sin inventar campos clínicos ni añadir un párrafo a la descripción que escribió la persona.
2. **Ubicación:** ciudad seleccionada en autocompletado, barrio/sector, lugar de referencia e indicaciones opcionales. Escribir dos letras habilita búsqueda con espera de 300 ms; se descartan respuestas obsoletas o de una etapa/sesión anterior. No se descarga todo el catálogo ni hay sondeo en reposo.
3. **Revisión y contacto:** situación y ubicación editables, indicaciones si existen, descripción desplegable, foto seleccionada, confirmación de publicación y contacto privado opcional. La confirmación de foto empieza desmarcada y se reinicia al reemplazar o quitar la imagen. No se exige si no hay foto.

Progreso de tres etapas con iconos. Formularios pastel con títulos e iconos compartidos; ancho de lectura acotado, sin huecos dobles incondicionales entre grupos. Los controles inferiores usan Wrap para conservar acceso con texto ampliado. Hay Cancelar desde cualquier etapa y Anterior cuando corresponde; salir con borrador requiere confirmar descarte. Navegar no crea un reporte por etapa.

La foto se mantiene en memoria, se muestra completa en la revisión y no se sube antes del envío final. La API del cliente exige `photoPublic: true` para enviar archivo; el servidor valida el indicador también. Seleccionar una foto no implica enviar ni publicar nada aún. El contrato de autenticación y la consulta posterior de Mis reportes se conservan.

## Protección del borrador y red

- `Session.identityRevision` identifica límites de autenticación sin invalidar por un simple cambio del nombre del perfil. El formulario liga el borrador a revisión y correo iniciales.
- Al cambiar sesión se eliminan datos y foto del borrador y se permite salir aunque haya una subida/picker antiguo pendiente. Una respuesta antigua no puede restaurar la foto ni cerrar una pantalla de otra identidad.
- Cambiar de sesión no deshace una petición que ya llegó al servidor: una creación autenticada enviada antes sigue vinculada a la identidad que la autorizó. No se reasigna a la siguiente cuenta.
- Validación local por etapa y validación final antes del POST; selección de ciudad exacta, campos requeridos y límites existentes.
- Un envío activo deshabilita otra pulsación. Un resultado incierto conserva los datos, informa mediante diálogo y bloquea reenvíos automáticos. Si había cuenta, permite abrir Mis reportes para comprobarlo.
- En modo sin cuenta se explica que la clave privada podría no haberse recibido si se perdió la respuesta. No se promete recuperarla desde el listado público ni se inventa una nueva clave.
- Esto evita repeticiones accidentales dentro del intento actual, no certifica entrega global «exactamente una vez». Recargar o iniciar otro reporte es otro intento. La recuperación idempotente de recibos anónimos requiere una política adicional; permanece en Q04, sin publicar claves ni guardar texto plano como atajo.

## Backend

`rescue/serializers.py`: los campos desconocidos, incluidas identidades/estados suministrados fuera del contrato, se rechazan; se mantienen límites de descripción/contacto/ubicación, pares de coordenadas, ciudad activa y tipo de reporte perteneciente a un catálogo activo. El archivo requiere confirmación pública. Una entrada inválida no crea filas parciales.

`rescue/views.py`: respuestas de creación y errores son `no-store`, porque el recibo anónimo contiene una credencial que se entrega únicamente al confirmar. Se conservan transacción, permiso configurable `reportes.participar`, atribución al usuario autenticado y hash de la clave anónima.

La normalización existente de fotos queda comprobada: WebP, lado máximo 960 px, salida máxima 128 KiB y EXIF eliminado. Estos límites son de la copia almacenada/servida, no una afirmación de que todo archivo subido pese menos de 128 KiB. El cliente conserva el límite de selección de 5 MiB y las opciones de reducción del picker. No se añade imagen de fondo, dependencia, SDK ni servicio externo.

## Trazabilidad

| Necesidad | Código | Verificación |
|---|---|---|
| R09: etapas, selección y campos pertinentes | `rescue_screens.dart`, `form_surfaces.dart` | Validación local; tipos reales; foto/consentimiento condicionales |
| R10: datos, foto y vuelta atrás | controladores y bytes en memoria del formulario | Foto preservada, ciudad/datos intactos, resumen e indicaciones |
| R10: envío, salida y red incierta | `rescue_api.dart`, formulario y `session.dart` | Doble pulsación bloqueada, Cancelar/Descartar, respuesta tardía tras cambio de cuenta/picker |
| Reglas del servidor | serializers y vista de creación | Desconocidos, inactivos, datos faltantes, foto sin autorización, estado de BD sin cambios |
| Integración con foto real de prueba | `report_edit_http_test.dart` optativo | Cliente Flutter → HTTP loopback → Django → MySQL; foto pública, edición y cierre único |

## Evidencias locales

Carpeta del workspace: `output/correcciones-app-2026-11-24/creacion-reportes`.

- Backend: 59 pruebas aprobadas en MySQL aislado, rescate y RBAC (`backend.txt`).
- Cliente canónico: 282 aprobadas, 6 optativas omitidas (`cliente.txt`); once focales finales del wizard (`wizard-final.txt`) y recorrido con capturas (`visual-final.txt`).
- Demo Android local: 356 aprobadas y 4 capturas optativas omitidas (`demo.txt`); focales finales para la misma interfaz y contrato. La demo no representa persistencia productiva.
- Demo web: doce focales aprobadas. Análisis y compilaciones tienen sus logs separados; no se ha actualizado el enlace público.
- HTTP real optativo ejecutado aparte (`http-cliente.txt`, `http-real.json`): crea con confirmación de foto, verifica descriptor público y descarga HTTP de WebP; rechaza clave incorrecta, edita, oculta contacto/clave y cierra una vez. Muestra sintética almacenada: 45912 bytes; no es una estimación del peso de todas las fotos.
- Comprobación SQL posterior (`persistencia-real.json`): WebP dentro de límites, sin EXIF, contacto retirado y un solo historial de cierre. Servidor QA detenido al terminar; base aislada y datos ficticios.
- `01-situacion.png` a `04-confirmacion-foto.png`: renderizados Flutter a 393×852 con datos e imagen de prueba de un asset existente. No son capturas de dispositivo ni un animal/caso real publicado. La regresión de las tres etapas también usa 320 px y texto al 200 %.

La demostración con fotografía usa un recurso existente solo como fixture; no acredita licencia comercial ni añade un animal ficticio al entorno productivo. El consentimiento de publicación de foto no sustituye políticas jurídicas, términos o la trazabilidad completa de sus aceptaciones de la guía 74.

## Estado y siguiente bloque

Se cierran R09 y R10: **29/57 (50,9 %)**, conteo simple de la guía 75. Continúa O01/O02: notificaciones con lectura/destino reales y Mis solicitudes con estados, detalle y actualización coherentes. Luego cuenta/mascotas/ayudas/rutas restantes y Q01-Q10. Continúan abiertos adjuntos/D02, condiciones jurídicas, derechos/retención, licencias, aceptación física, respaldo/restauración, auditoría de seguridad/security-audit por identificar, paquetes de tres integrantes y presupuesto final gratuito/VPS. Ningún resultado de este bloque declara el producto listo para publicar.


## Cierre de compilación

APK Android debug y demo web release compilados correctamente en local (`android-cierre.txt`, `web-build-cierre.txt`). Análisis sin observaciones en cliente y ambas demos (`analyze-final.txt`, `demo-analyze-final.txt`, `web-analyze-final.txt`). El aviso preexistente de CupertinoIcons no empaquetada permanece anotado para la auditoría global de iconos; la compilación web finaliza. No se actualizó el `dist` alojado ni el enlace público. Los últimos cambios de salida tras cambio de identidad quedaron comprobados en las once focales finales. El mosaico se guarda como `mosaico-creacion-reportes.png`.
