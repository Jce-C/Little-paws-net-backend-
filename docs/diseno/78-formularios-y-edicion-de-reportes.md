# Formularios compartidos y cierre de detalle/edición de reportes

24 de noviembre de 2026. Implementación local del bloque 2 de la guía 77 y de la petición posterior de aplicar el estilo a los formularios de la app. Sin commits, despliegue ni recursos de pago. El contrato de adopción de la guía 76 se conserva.

## Formularios

- Paleta común `LpnFormPalette`: azul, verde, amarillo, rosa y lila suaves. `LpnFormSection` y `FormCard` comparten títulos reconocibles, iconos circulares, separadores, radio 20, relleno 16 y bordes delicados. Los tonos tienen asignaciones estables, no cambian al reconstruir.
- Campos con densidad compacta y mínimo 48; el texto ampliado puede aumentar el alto. Los campos que antes usaban `LpnInputSurface` conservan el borde habitual y pierden la sombra individual. No se añade blur a cada control. La preferencia de superficies sólidas conserva su comportamiento.
- Vivienda y otras respuestas cortas: letra 13, relleno horizontal 8 e iconos 14. Prueba explícita de las tres opciones Propia/Arrendada/Otra situación en una fila a 393 px con etiquetas completas y mínimo táctil 48. En anchos menores o texto ampliado se permite envolver; no se reduce el texto hasta volverlo ilegible.
- Aplicación a perfil, datos/foto de mascota, nuevo reporte y gestión con clave, mensajes/publicaciones/interés, convocatorias de voluntariado/canales, preparación de pedidos, aportes y apadrinamientos, además de la evaluación de adopción. Los componentes del formulario anterior de adopción también reciben el estilo; ese recorrido sigue siendo solo compatibilidad.
- El diálogo de moderación tiene fondo suave y contenido desplazable accesible. Las pantallas de autenticación conservan la composición específica solicitada; no se sustituyen por una tarjeta de cuestionario ni se cambia su lógica.
- No se eliminan preguntas ni datos ni se cambian las condiciones de las operaciones de negocio por motivos visuales. No se hacen peticiones para seleccionar una opción o avanzar entre etapas.

## R01/R02: detalle de reportes

`rescue/rescue_screens.dart`: foto y fallback, tipo de situación, estado con icono y texto, ciudad, explicación y seguimiento en grupos. Solo se muestra lo que devuelve el servidor: ciudad pública y, si existe caso, organización, número de caso y estado. No se inventan fechas, responsable individual ni fases de rescate. La dirección/contacto privados no se añaden a la ficha pública. Apadrinar permanece visible en una barra fuera del scroll únicamente cuando existe caso; conserva su puerta de sesión y operación real.

## R08: edición y trazabilidad

`rescue/anonymous_report_screen.dart` conserva los grupos Información / Datos a actualizar / Confirmación. Cancelar pide descartar si hay borrador, no envía datos. Cambiar contacto a vacío requiere la opción explícita. Los errores aparecen en diálogo, con borrador conservado. Una respuesta incierta bloquea guardar/cerrar y pide verificar el reporte antes de repetir; no hay reintento automático. La clave se oculta y se elimina del editor al confirmar el éxito. Acciones fuera del scroll, con ajuste de filas según tamaño de pantalla.

`rescue/views.py`: edición con clave mantiene comprobación de objeto, hash de clave, estado Pendiente, ausencia de caso aceptado y bloqueo transaccional de fila. Un reporte vinculado a una cuenta no puede modificarse con este endpoint anónimo: esto no incorpora un editor de reportes autenticados. Respuestas y errores de gestión son `no-store`.

Cada cambio real agrega auditoría sin clave, hash, contacto ni texto de la descripción; se registran objeto, campos modificados y estados anterior/nuevo. Repetir exactamente una edición no agrega un evento ni cambia la fecha. Un segundo cierre devuelve 409 y no duplica historial. Esto no es una promesa de idempotencia de todas las operaciones de la app.

`seguridad/web/presentacion_eventos.py` y `dashboard.py`: la auditoría identifica la autorización como Reportante con clave privada y explica Actualizó/Cerró un reporte, con nombres legibles de campos. No lo atribuye a un usuario nominal que no se autenticó ni al sistema como si fuera tarea automática. Los roles de consulta de auditoría no cambian.

## Evidencia

Carpeta del workspace: `output/correcciones-app-2026-11-24/reportes-y-formularios`.

| Verificación | Resultado / archivo |
|---|---|
| Backend Django + MySQL aislado, rescate y RBAC | 56 aprobadas, `backend.txt` |
| Repetición focal tras presentación legible de auditoría | 10 aprobadas, `backend-focal.txt` |
| Cliente canónico completo | 274 aprobadas, 6 optativas omitidas, `cliente-cierre.txt` |
| Demo Android local con transporte ficticio | 348 aprobadas, 4 visuales optativas omitidas, `demo.txt` |
| Cliente Flutter → HTTP loopback → Django → MySQL | aprobada, `http-cliente.txt`, `http-real.json` |
| Comprobación SQL posterior al HTTP | contacto eliminado, Cerrado, un historial de cierre, dos eventos de cambios; sin secretos, `persistencia-real.json` |
| Cinco etapas, detalle y editor renderizados | 17 aprobadas con capturas, `visual-final.txt` |
| Ocho pantallas de formulario de demo a 390 px y 320 px/200 % | 16 aprobadas, `formularios-visual.txt` |
| Focales demo web | 19 aprobadas, `web-focal.txt` |
| Análisis | sin observaciones, archivos `*-analyze.txt` y `analyze-cierre.txt` |
| Compilación | APK debug y demo web release correctos, solo locales |

Las seis optativas del cliente incluyen cuatro capturas optativas y dos recorridos HTTP que requieren entorno explícito. El nuevo recorrido HTTP de reportes se ejecutó aparte. Las cuatro capturas optativas de la demo se ejecutaron en el cliente canónico. Los renderizados tienen datos ficticios; no son capturas de un teléfono ni certificación de producción. El inventario visual de demo cubre además sus 34 vistas a escala 1 y 2 en su regresión; esto no sustituye el recorrido integral funcional ni las pruebas físicas.

La muestra real verifica clave incorrecta rechazada, edición reflejada públicamente, ausencia de clave/contacto en respuesta pública y cierre único. El servidor local de QA se detuvo al finalizar; los datos de prueba están en una base aislada y no se han migrado ni editado cuentas productivas. No se ha añadido tabla/migración para este bloque. No se repiten fotografías, SDK ni sondeo; la nueva auditoría usa la tabla existente solo cuando cambian datos.

La demo web conserva el aviso previo de CupertinoIcons no empaquetada al compilar; la compilación termina correctamente. La revisión de iconos global no se da por cerrada por pasar el análisis. La copia web se compila en `build/web`, sin publicar ni reemplazar el `dist` alojado.

## Próximo bloque

R09/R10: creación de reportes, validaciones por etapa, selección de situación, ubicación y foto, preservación al regresar, errores/red incierta y una única operación final. Revisar progresos, acciones fijas y ancho de controles con este mismo sistema visual. Después continúan O01-O06 y Q01-Q10. Se mantienen pendientes adjuntos/D02, datos sensibles, revisión jurídica, licencias, derechos/retención, firma Android, dispositivo físico, respaldo/restauración, security-audit por identificar, paquetes para tres integrantes y presupuesto final gratis/VPS.

Estado de la lista 75: **27/57 (47,4 %)**. No se suman puntos nuevos por aplicar el mismo estilo ni se afirma que toda la aplicación esté terminada.
