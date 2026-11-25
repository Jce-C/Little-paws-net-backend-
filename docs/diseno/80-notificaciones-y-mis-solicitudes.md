# Notificaciones y Mis solicitudes

24 de noviembre de 2026. Cierre local de O01/O02 de la guía 75. Sin commits, cambios productivos ni servicios de pago. Mantiene paleta, jerarquía, bordes e iconos de los formularios; no elimina la lógica del cuestionario ni la compatibilidad previa.

## Notificaciones

- Icono según el tipo conocido y fallback para otros tipos, etiqueta Sin leer/Leída, contenido, fecha real y acciones diferenciadas. La información no depende solo del color.
- El cambio a Leída ocurre únicamente después de la confirmación del servidor. El servidor devuelve `fecha_lectura`; una repetición conserva el mismo valor. El cliente ya no fabrica esa fecha con su reloj local. Con un servidor antiguo que solo devuelve `leida: true`, reconoce el estado confirmado sin inventar una fecha.
- Marcar como leída no abre ni modifica una solicitud. Abrir Ver solicitud tampoco la marca automáticamente; son acciones explícitas. Si falla la operación o el destino no se puede consultar, no se finge éxito.
- Las decisiones nuevas de adopción relacionan la notificación mediante una FK explícita a la solicitud. No se extraen identificadores de frases ni se construyen URLs arbitrarias. Los avisos históricos sin relación, y otros avisos sin pantalla móvil asociada, continúan informativos sin inventar enlaces.
- El API incluye destino solo cuando coinciden destinatario/adoptante y sigue vigente `adopcion.participar`. La pantalla de destino comprueba también autorización en su propio backend; revocar el permiso o cambiar de cuenta no permite reutilizar ese enlace para leer registros ajenos.
- Paginación de 20, botón Ver más y filtro local de no leídos. El contador dice «en esta lista»: no representa todos los avisos de la cuenta ni oculta que pueden existir otras páginas. Un filtro vacío no impide cargar la siguiente página. Los elementos se deduplican por ID y las operaciones en curso bloquean repeticiones.
- Actualización manual/al volver del detalle; no hay sondeo, correo, WhatsApp, push, rastreo ni SDK nuevo.

## Mis solicitudes y detalle

Tarjeta compacta con mascota/foto o fallback, número, estado exacto y fecha recibidos. No se convierten estados a fases inventadas. Se mantiene paginación y errores recuperables; las cargas viejas no sobrescriben cursores de una actualización nueva.

El detalle conserva respuestas iniciales, motivo de decisión e historial autorizado. Añade Actualizar solicitud, control de peticiones repetidas y fecha de resolución cuando el servidor la proporciona. Al volver se actualiza la primera página del listado; el resto puede cargarse nuevamente con Ver más. Es una actualización explícita, no sincronización push permanente entre todas las sesiones.

Las listas y el detalle usan claves que incluyen la revisión de autenticación y la identidad. Cambios normales del perfil no recargan innecesariamente; una nueva autenticación no conserva respuestas privadas de la anterior.

## Persistencia y compatibilidad

- `core/migrations/0018_notificacion_solicitud.py`: FK nullable `Notificacion.solicitud_adopcion`, con SET_NULL. Depende de core.0017 y adoption.0002. Conserva filas antiguas; no hay migración que deduzca vínculos por el texto.
- `adoption/services.py`: relaciona el aviso tanto al resolver una solicitud como al cerrar las otras por adopción de la misma mascota.
- `core/api.py`: consultas limitadas, relación por objeto, lectura idempotente y respuestas privadas `no-store`, también errores. La consulta difiere las observaciones de la solicitud: no carga ni expone la evaluación cifrada en la bandeja.
- Compatibilidad: `/api/notificaciones/` sin `paginado=1` conserva lista de hasta 100 registros. El cliente nuevo solicita `paginado=1`, recibe veinte y cursor, y tolera listas antiguas sin inventar más páginas.
- `adoption/request_history.py`: mantiene titularidad y permiso, ampliando `no-store` a errores del listado. No cambia estados ni decisiones.
- El API de lectura ignora el destinatario que intente suministrar el cliente y siempre filtra por la sesión. Una cuenta administradora tampoco obtiene el buzón personal de otra mediante estos endpoints.

Al integrar el backend deberá aplicarse la migración en la base de destino antes de ejecutar este código. Solo se aplicó en bases locales aisladas de QA; no en Railway/Northflank ni en la base productiva. La app nueva funciona con avisos de versiones anteriores, pero añadir la FK requiere migrar el backend actualizado.

## Evidencia y trazabilidad

Carpeta del workspace: `output/correcciones-app-2026-11-24/notificaciones-solicitudes`.

| Necesidad | Código | Evidencia |
|---|---|---|
| O01: estado de lectura verdadero | `notifications_api.dart`, pantalla, `core/api.py` | Fecha persistida, repetición idempotente, fallo sin falso éxito y pulsación duplicada bloqueada |
| O01: destino autorizado | modelo/FK, servicio de adopción, API y ruta tipada | Titular/permiso/objeto; destino desconocido ignorado; sin vínculos extraídos del texto |
| O01: consumo y páginas | API opcional paginada y cliente compatible | 20 filas, cursor, deduplicación, filtro sin consultas y ausencia de sondeo |
| O02: estado/detalle/actualización | `adoption_screens.dart`, `request_detail_screen.dart` | Actualizar detalle, volver y obtener estado vigente en lista; respuestas iniciales preservadas |
| Integración | Flutter → HTTP loopback → Django → MySQL | Decisión de gestor asignado, notificación vinculada, misma fecha de lectura y rechazo a otra cuenta |

Resultados:

- Backend: 64 pruebas aprobadas, incluyendo adopción, notificaciones y RBAC (`backend-final.txt`).
- Cliente: 289 aprobadas y 6 optativas omitidas en la regresión previa al nuevo test HTTP optativo. Ese recorrido adicional se ejecutó aparte contra MySQL; la suite por defecto incorpora ahora ese séptimo optativo.
- Demo: 363 aprobadas y 4 capturas optativas omitidas (`demo.txt`). Son datos ficticios en memoria; no prueban persistencia real.
- Focales y capturas finales: once de notificaciones/solicitudes; las focales ampliadas de demo incluyen también navegación y respuesta incierta. Imágenes en español con el mismo locale de la app, a 393×852; también se prueban acciones a 320 px/200 %.
- `http-real.json` y `http-cliente.txt`: usuario ficticio crea evaluación, gestor asignado resuelve, aviso propio apunta al ID correcto, lectura repetida conserva fecha y otra cuenta recibe 404. Lista y detalle coinciden en Rechazada.
- `persistencia-real.json`: FK/titular y fecha de API coinciden con la base; core.0018 aplicada en QA. `migraciones.txt`: no hay migraciones faltantes. El servidor HTTP QA se detuvo.
- Las capturas son renderizados Flutter con fixtures, no un dispositivo físico ni capturas de datos productivos. El detalle de la captura tiene un historial vacío de ejemplo; el recorrido HTTP real comprueba la evaluación conservada y el estado resuelto; las pruebas backend cubren además el historial del proceso.

No se agregan recursos gráficos ni dependencias. Los tiempos de la muestra HTTP local usan configuración de pruebas y no acreditan latencia de producción. La demo web conserva su advertencia previa de CupertinoIcons no empaquetada al compilar, pendiente de revisión global.

## Estado y siguiente bloque

**31/57 (54,4 %)** de la guía 75. Próximo bloque: O03/O04, Mi cuenta y Agregar mascota, con datos, validaciones, propiedad, fotografía y salidas claras. Siguen pendientes O05/O06 y Q01-Q10, además de las decisiones D02, datos sensibles, condiciones jurídicas, licencias, retención/derechos, firma Android, dispositivo físico, respaldo/restauración, seguridad/security-audit por identificar, paquetes para tres integrantes y presupuesto final gratuito/VPS. Este cierre no certifica publicación ni sincronización instantánea de todos los procesos.


## Cierre de compilación

APK Android debug y demo web release compilados correctamente en local, con logs `android-cierre.txt` y `web-build-final.txt`. Análisis sin observaciones en las tres copias (`analyze-cierre.txt`, `demo-analyze-final.txt`, `web-analyze-final.txt`). Focales finales: once en cliente/web y veintidós en demo al incluir navegación y recuperación. El servidor HTTP QA quedó detenido. No se sustituyó `dist` de alojamiento, no se hicieron commits ni se publicó la migración.
