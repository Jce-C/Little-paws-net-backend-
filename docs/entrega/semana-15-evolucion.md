# Evidencias de Semana 15

## Diagnóstico

| ID | Deuda técnica observada | Impacto | Riesgo | Prioridad | Acción |
| --- | --- | --- | --- | --- | --- |
| DT-01 | El panel desplegado y la punta de main provienen de estados distintos | Alto | Alto | Alta | Revisar la base local del despliegue e integrarla mediante PR. |
| DT-02 | La entrega aún no tiene un tag que identifique el código demostrado | Alto | Medio | Alta | Registrar la versión, validar el commit integrado y etiquetarlo. |
| DT-03 | El workflow de pruebas del panel está en entrega-panel y falta trasladarlo a main | Alto | Alto | Alta | Llevar el workflow existente y comprobar que corre en los PR. |
| DT-04 | El README del backend-panel dice que la revisión todavía no se publicó | Medio | Medio | Media | Actualizar las instrucciones del despliegue vigente y comprobar un arranque desde cero. |
| DT-05 | interacciones.js concentra navegación, diálogos, sincronización y guardado | Medio | Medio | Media | Separar responsabilidades por cambios pequeños con regresión. |
| DT-06 | El guardado de un recurso inexistente no controlaba la excepción del modelo | Medio | Medio | Alta | Responder con 404, mostrar el aviso y verificar que no se altere otro recurso. |
| DT-07 | Una repetición con BD de tests conservada encontró datos residuales de escenarios anteriores | Medio | Medio | Media | Aceptar con esquema efímero aislado e investigar la limpieza entre suites. |

## Preparación local para tres autores

| Autor propuesto | Módulo | Rutas del cambio |
| --- | --- | --- |
| José Carlos | API y escenario QA | Consultas y pruebas móviles de accounts, animals, adoption, rescue y core; parches de rutas/privacidad y config/settings_qa.py. |
| María José | Aplicación ciudadana Android | frontend/mobile/ |
| Sally Andrea | Corrección de edición y evidencia académica | Cambios puntuales en backend-panel/seguridad/web/administracion.py, templates/seguridad/web/administracion.html, static/seguridad/interacciones.js y tests_ui_compacta.py. Documentación raíz y de entrega. |

Los archivos existentes pueden contener trabajo anterior del panel. Revisar cada diff y escoger las partes correspondientes a cada autor después de coordinar la integración de la base. En archivos compartidos, usar git add -p. La app móvil puede trabajar con la respuesta anterior de seguimiento usando el ID de solicitud como etiqueta, lo que permite separar su revisión de la ampliación de la API.

## Issues pendientes de registrar

| Tipo | Título propuesto | Prioridad | Responsable propuesto | Criterio de cierre |
| --- | --- | --- | --- | --- |
| Bug | El panel falla al guardar un recurso inexistente | Alta | Sally Andrea | Devuelve 404 con aviso claro, registra el fallo y conserva los demás recursos. |
| Mejora | Completar un recorrido de adopción en Android | Alta | María José, con API de José Carlos | Desde Android se envía la solicitud, el gestor decide en el panel y Android consulta el nuevo estado. |
| Deuda | Integrar en main la versión del panel que se demuestra | Alta | José Carlos | main contiene el panel y el flujo de pruebas, y una instalación local reproduce el recorrido documentado. |

## Trazabilidad para completar en GitHub

| Cambio | Issue | Rama propuesta | Commit propuesto | PR | Integración | Versión |
| --- | --- | --- | --- | --- | --- | --- |
| Recurso inexistente | Pendiente | fix/recurso-inexistente | fix(panel): informar cuando el recurso editado ya no existe | Pendiente | Pendiente | Pendiente |
| Adopción móvil | Pendiente | feature/adopcion-movil | feat(movil): enviar y consultar solicitudes de adopción | Pendiente | Pendiente | Pendiente |

El registro de cambios queda en **Sin publicar** hasta que los PR se integren. v0.1.0 es una propuesta para el primer piloto etiquetado. Incorpora una app y una ampliación compatible de la respuesta de seguimiento.

## Estado para la sustentación

El panel web ofrece cuentas, roles, permisos, gestión por organización, auditoría y operaciones de rescate y adopción. El piloto Android local cubre catálogo/ficha pública y solicitud de adopción, rescates y reportes con/sin cuenta, notificaciones internas, mascotas propias, lectura privada de expediente, QR temporal y edición limitada del perfil propio. El corte actual conserva 77 pruebas Flutter y pasa 316 pruebas Django en la regresión completa; los recorridos Android se registran al final de este documento. La validación del APK normal por controles Android incluye guardar con teclado abierto. Quedan fotos públicas autorizadas, adjuntos médicos móviles, recuperación de acceso, mapa, paginación, comercio/donaciones móviles y validación física. Para uso externo faltan también un piloto con organización real, restauración de respaldo, firma y soporte. La incidencia ANR del ensayo instrumentado permanece documentada; no se observó un nuevo evento durante la comprobación independiente del APK normal. No hay commits, tag ni despliegue de este trabajo local.

## Reflexión para revisar en grupo

1. La deuda principal es poder vincular el código de GitHub con el panel desplegado.
2. Esa diferencia dificulta reproducir defectos, revisar qué salió a producción y recuperar una versión anterior.
3. Se aplicó mantenimiento correctivo en la edición de recursos y perfectivo al ofrecer el recorrido de adopción en Android.
4. Las ramas permiten revisar y probar un cambio con alcance claro antes de integrarlo.
5. Los issues dejan explícitos el problema, el responsable y el resultado que se acepta.
6. Los commits descriptivos muestran la intención de cada cambio y facilitan investigar regresiones.
7. El tag señala el commit de una versión y permite reproducir su código.
8. Sin control de versiones se pueden sobrescribir cambios y perder la referencia de qué código funcionaba.
9. Otro desarrollador puede apoyarse en las guías y las pruebas. Lo comprobaremos cuando alguien del equipo instale y ejecute el proyecto desde el commit integrado.
10. El siguiente mantenimiento debe centrarse en que el primer piloto pueda funcionar con cuentas de una fundación y recuperarse mediante un respaldo comprobado.

## Resultado verificado en local

- Android en el emulador Pixel 6a envió una solicitud y comprobó el estado Pendiente. Un gestor autenticado la tomó y aprobó desde el panel. Android actualizó la lista y mostró Aprobada. El catálogo público dejó de ofrecer esa mascota.
- En el bug de recursos, Django devolvió HTTP 404 y el navegador conservó el borrador con un aviso visible.
- Flutter analyze sin hallazgos y 38 pruebas de Flutter aprobadas (nueve de sesión, cinco de datos de adopción, tres de interfaz de adopción, dos de adaptación, tres de rescates, cuatro de notificaciones, cuatro de gestión anónima, cuatro de ficha pública y cuatro de mascotas propias/expediente). Pasaron 252 pruebas de Django en MySQL aislado y no se detectaron migraciones pendientes.
- Se restauró una copia de QA en un esquema separado. Coincidieron los recuentos de 99 tablas y se recuperó la solicitud resuelta del ensayo móvil. El respaldo del almacenamiento privado y la recuperación de Railway siguen pendientes de un ensayo propio.
- Los enlaces de GitHub de cada issue, commit, PR y tag se completan cuando sus autores registren e integren el trabajo.

## Revisión de sesión móvil — 18 de noviembre de 2026

Se corrigieron el acceso local que permanecía activo después de un segundo rechazo HTTP 401, las respuestas de autenticación mal formadas y la notificación después de destruir la sesión. Las pruebas cubren renovación compartida, restauración segura, cambio de cuenta durante una petición y recuperación desde la pantalla de solicitudes. Un HTTP 403 no cierra la cuenta. Estos cambios permanecen locales y se entregan en el módulo Android para revisión de su autora.

La integración se repitió en Pixel 6a el 18 de noviembre: Android envió la solicitud, el gestor la aprobó desde el panel web y Android mostró Aprobada. La prueba terminó correctamente y la mascota dejó el catálogo público. Los registros se guardan fuera del código fuente en output/adopcion-movil/android-sesion-20261118.log y panel-sesion-final-20261118.log.

## Validación de respuestas de adopción — 18 de noviembre de 2026

Se reprodujeron tres errores de conversión ante respuestas incompletas del catálogo, seguimiento y confirmación de solicitud. La app valida ahora la estructura y muestra un mensaje recuperable. Ante una confirmación sin ID se recomienda consultar Mis solicitudes antes de enviar de nuevo; no se reintenta automáticamente una creación. Se conservan el catálogo vacío y la compatibilidad con el seguimiento anterior sin nombre de mascota. Pasaron 17 pruebas Flutter. No cambiaron permisos, servicios ni datos del backend. Autora propuesta: María José, módulo 02-App-Android.zip.

## Optimización de portada móvil — 18 de noviembre de 2026

La imagen de Figma se convirtió a WebP sin reducir sus 1024 × 434 píxeles. Pasó de 848 920 a 102 376 bytes (87,9 % menos). El catálogo usa el asset local WebP y el PNG original se conserva fuera de la entrega en output/adopcion-movil/referencias. No se generaron ilustraciones nuevas. La conversión se inspeccionó visualmente y queda documentada para reproducirla. Autora propuesta: María José, módulo Android.

Próximo bloque: revisar el acceso público a fotos reales. Mascota no tiene una relación específica de foto de adopción; DocumentoAdjunto pertenece al expediente. No se publicarán esos adjuntos como fotos por defecto. Hace falta una relación explícita, carga autorizada y revocación, usando el almacenamiento y permisos existentes; comprobar permitidos y denegados en QA antes de conectarla al catálogo.

## Texto ampliado y pantallas pequeñas — 18 de noviembre de 2026

Se reprodujo un desbordamiento horizontal de 192 píxeles en la cabecera a 320 × 640 con texto al 200 %, y otro vertical en la navegación. La marca ahora tiene ancho flexible; cabecera y navegación reservan altura según el escalado del sistema. Se conserva el texto ampliado, sin imponer una escala menor. Dos pruebas recorren catálogo, Mi cuenta y acceso en 320 × 640 y 800 × 360 con texto al 200 %, verifican ausencia de desbordamientos y que el botón de ingreso sea alcanzable mediante desplazamiento. Se aplicaron los fundamentos de accesibilidad de TypeUI y se conservó la paleta. Autora propuesta: María José, módulo Android. No sustituye una revisión con TalkBack y un dispositivo físico.

## Rescates y reporte móvil — 18 de noviembre de 2026

Se añadieron rescates con búsqueda y detalle público, formulario de reporte, confirmación y seguimiento propio. El formulario consulta ciudades activas a partir de dos letras, muestra departamento y exige seleccionar el registro real. Se admiten reportes con cuenta y anónimos según el servicio existente. La confirmación anónima muestra la clave privada una sola vez y permite copiarla. Los reportes con cuenta aparecen en Mis reportes, con estado y fundación cuando existe caso. No se fabrican hitos, fotografías ni coordenadas.

Figma de referencia: `sR48elLBOFINiQXIfwJsNu`, pantallas `83:2` y `145:1341`. Se conservó el fondo crema y se descargó y convirtió a WebP la portada de rescates. La composición se adaptó a controles accesibles y datos reales. El mapa y la subida de fotos quedan pendientes de conectar al almacenamiento y a las reglas de privacidad.

Reparto: José Carlos incorpora `rescue/mobile_views.py`, `rescue/tests_mobile.py` y el parche de rutas del módulo 01. María José incorpora `lib/rescue/`, navegación, portada y pruebas del módulo 02. Sally incorpora esta evidencia y el changelog del módulo 03. Se mantienen sin commits.

Las cinco pruebas nuevas de Django verifican ciudades activas, aislamiento entre cuentas, consulta del caso propio, creación permitida/revocada y clave anónima guardada como hash. Junto a seguimiento de adopción pasaron seis pruebas en MySQL aislado. Las pruebas de interfaz cubren envío con y sin cuenta, autocompletado y consulta del caso. La gestión anónima se completó en el bloque posterior descrito al final de este documento.

La integración de rescates pasó en Pixel 6a contra Django QA local: ingreso con una cuenta sintética, búsqueda y selección de RIOHACHA, envío de reporte y consulta del mismo en Mis reportes. Se verificó que no se entrega clave anónima a una cuenta autenticada. Registro: output/adopcion-movil/android-rescate-20261118.log. Pasaron las 22 pruebas Flutter, las seis pruebas específicas de backend y la comprobación de migraciones.

Pendientes móviles: bienvenida y fidelidad visual completa del acceso; fotos autorizadas y mapa; expediente/QR con permisos; perfil completo, donaciones y tienda. Los listados actuales muestran hasta 100 registros; falta paginación para volúmenes mayores. No hay publicación ni firma de producción en este corte.

El APK QA se regeneró sin credenciales del ensayo, se instaló y abrió en Pixel 6a y se inspeccionó la pestaña Rescates. Captura: rescates-android-20261118.png, incluida en el módulo de evidencias. Flutter analyze terminó sin hallazgos.

## Notificaciones internas en móvil — 18 de noviembre de 2026

Se conectó la campana de la cabecera a una bandeja con contenido real de la cuenta, fecha, estado leído/sin leer, filtro local y actualización manual. No se agrega sondeo ni una consulta de notificaciones antes de iniciar sesión. La app confirma la lectura solo después de la respuesta del backend y conserva el estado ante un error. Una respuesta pendiente de la cuenta anterior no aparece al cambiar de persona. La cabecera calcula el espacio del nombre completo junto a la campana sin reducir la escala de texto del sistema.

Se reutilizan las rutas existentes de core, sin cambiar autorización ni esquema. Tres pruebas nuevas de backend verifican acceso anónimo denegado, listado propio y lectura idempotente sin modificar avisos ajenos. Cuatro pruebas Flutter verifican ausencia de consultas privadas sin cuenta, recuperación ante fallo, aislamiento al cambiar de cuenta y datos inválidos. La bandeja es interna: no implica push, correo ni entrega fuera de la app. Pendientes: paginación y validación con TalkBack real.

Reparto: José Carlos incorpora core/tests_mobile.py en el módulo 01; María José, lib/notifications/, campana, cabecera y pruebas del módulo 02; Sally, documentación del módulo 03. Todos los cambios permanecen locales y sin commits.

La integración de la bandeja pasó en Pixel 6a con un aviso explícitamente sintético de QA: ingreso, apertura de campana, lectura, actualización y filtro sin leer. Registro: output/adopcion-movil/android-notificaciones-20261118.log. Pasaron 26 pruebas Flutter y nueve pruebas específicas de backend. No se usaron cuentas reales ni se enviaron mensajes externos.

## Gestión anónima de reportes — 18 de noviembre de 2026

Se completó la pantalla de número/clave, corrección, eliminación explícita de contacto y cierre confirmado. Se puede acceder desde Rescates o desde la confirmación del envío anónimo. La clave se oculta al escribir, no se persiste y se elimina del formulario al confirmar. Un error conserva los datos para corregirlos; el cierre exige confirmación y el servidor vuelve a comprobar que no exista una aceptación. Al volver a rescates se actualiza la lista.

Se reutiliza el endpoint existente; no se cambian permisos ni el esquema. Las pruebas de backend verifican clave inválida sin modificaciones, corrección válida, eliminación de contacto, cierre con historial y rechazo de cambios después de cierre/aceptación. Se comprobó también Android contra QA: corrección real, confirmación, consulta pública del texto corregido, cierre y rechazo HTTP 409 posterior. Registro: output/adopcion-movil/android-anonimo-20261118.log.

Cuatro pruebas Flutter cubren envío sin token de cuenta, confirmación/cancelación, error recuperable con texto al 200 % y eliminación explícita de contacto. Pasaron 12 pruebas específicas de Django en MySQL aislado. Reparto: José Carlos actualiza rescue/tests_mobile.py (módulo 01); María José incorpora pantalla, API y pruebas móviles (módulo 02); Sally actualiza documentación (módulo 03). No hay commits ni despliegue.

## Ficha pública completa de adopción — 18 de noviembre de 2026

Se conectó una ficha individual al backend y se adaptó su composición a Figma `128:502`: imagen central, datos e historia en tarjeta. Los datos proceden de la mascota y su custodia; se distinguen edad estimada y datos sin registrar. La tarjeta muestra la organización y disponibilidad actuales sin convertir el expediente médico en información pública ni añadir hitos ficticios. La ciudad se identifica como la de la organización, sin afirmar una ubicación GPS del animal.

El endpoint aplica la misma elegibilidad del catálogo: sin dueño, en adopción, custodia única vigente y organización verificada/activa. Una ficha que deja de estar disponible responde 404 y la app retira el botón de solicitud. El backend mantiene la validación al enviar la solicitud. Las mascotas sin nombre no rompen el catálogo.

Seis pruebas nuevas de backend verifican campos públicos permitidos, exclusión de mascotas adoptadas o fuera de adopción, custodia cerrada, organización no verificada/desactivada, datos desconocidos y la restricción SQL que impide dos custodias vigentes. Cuatro pruebas Flutter cubren retirada de la acción, composición a 320 px con texto al 200 %, edad desconocida/estimada y nombre no registrado. Pasaron 34 pruebas Flutter y 18 pruebas específicas de Django en MySQL aislado. Flutter analyze no reportó hallazgos.

Reparto: José Carlos incorpora adoption/mobile_views.py y el parche 01-ficha-publica-adopcion.patch, y amplía adoption/tests_mobile.py (módulo 01). María José incorpora modelo, consulta, ficha y pruebas (módulo 02). Sally actualiza documentación (módulo 03). Se mantienen fotos autorizadas y expediente/QR entre los pendientes. Sin commits ni despliegue.

Se repitió el recorrido completo en Pixel 6a: ficha nueva → solicitud → aprobación en el panel → estado Aprobada en Android. El catálogo retiró la mascota y su ficha pública respondió 404 después de aprobar. Registros: output/adopcion-movil/android-ficha-20261118.log y panel-ficha-20261118.log. No se cambió el esquema.

Se inspeccionó la ficha en el APK normal instalado en el emulador, con un registro sintético del catálogo. La foto ausente se indica explícitamente; los datos desconocidos no se sustituyen por edades o tamaños de ejemplo. Captura real incluida en el módulo de evidencias: ficha-publica-android-20261118.png.

## Mascotas propias y expediente privado

Se incorporó Mi cuenta → Mis mascotas → Ver expediente. La lista devuelve solo fichas de la cuenta y no notas clínicas; el expediente reutiliza el servicio privado existente y presenta atenciones, autor, fecha y correcciones. Los datos se retiran de la pantalla al cerrar sesión o recibir una denegación al actualizar. No se inventan atenciones ni se convierte el QR de Figma en una credencial real. Referencias: perfil 156:1796 y expediente 128:599.

La nueva consulta requiere mascotas.participar y no permite consultar por otro usuario. Se identifica una ficha con custodia vigente para que se revise el conflicto de titularidad. Se conservaron las reglas del expediente: relación con la mascota y permisos vigentes, además de no-store. Cuatro pruebas de backend cubren aislamiento entre cuentas, anonimato denegado, expediente propio/ajeno, revocación y señalización de conflicto. Cuatro pruebas Flutter cubren lectura de original/corrección, retirada de datos ante denegación o cierre y respuesta inválida.

Se verificó en Pixel 6a contra QA: después de aprobar la adopción en el panel, la mascota aparece en la cuenta del adoptante y abre su expediente real vacío. Se volvió a consultar sin inventar datos clínicos. Registro: output/adopcion-movil/android-expediente-20261119.log. Las 22 pruebas específicas de Django pasaron en MySQL aislado. No hubo cambios de esquema ni de las reglas clínicas.

Reparto: José Carlos incorpora animals/mobile_views.py, animals/tests_mobile.py y 01-mascotas-propias.patch (módulo 01); María José incorpora lib/pets/, acceso desde la cuenta y pruebas (módulo 02); Sally actualiza documentación (módulo 03). Quedan pendientes adjuntos y QR en móvil, edición de perfil, fotos autorizadas, mapa, tienda y donaciones. Sin commits ni despliegue.


## QR temporal del expediente — 19 de noviembre de 2026

Se conectó Expediente privado → QR de identificación → Generar QR al endpoint existente de animals. No se emite nada al abrir la pantalla. El código es real y revocable, con vigencia de 24 horas, y se dibuja localmente con qr_flutter 4.1.0; no se reutiliza la imagen de muestra del Figma 128:599. Se mantienen el fondo crema, la tarjeta y el acento salvia del cliente. El botón de emisión queda fijo al pie para que el texto ampliado no obligue a buscarlo al final del contenido.

El reemplazo exige confirmación y el backend invalida el código anterior. Al pasar la app a segundo plano, vencer o cerrar sesión se retira de la pantalla; también se descarta una respuesta de emisión que termine después de salir. No se guarda en disco ni se copia al portapapeles. Ocultarlo no lo revoca en el servidor: vence, se reemplaza o queda revocado por un cambio de titularidad conforme al servicio ya existente.

El QR contiene solo el identificador, sin historial ni contactos. Un lector entrega ese identificador para el flujo veterinario del panel; no es un enlace público al expediente. La lectura pública de identificación entrega únicamente ID/nombre. El profesional sigue necesitando cuenta verificada y autorización clínica vigente para escribir. La app ciudadana no incorpora lector, autorización veterinaria ni escritura clínica en este bloque. Las respuestas de emisión y consulta, incluso errores, ahora llevan no-store y nosniff; no se cambió la política de autorización ni el esquema.

Reparto sin commits: José Carlos incorpora animals/tests_mobile.py y 01-qr-privacidad.patch sobre la base revisada; María José incorpora pantalla, API, dependencia/lockfile y pruebas Android; Sally incorpora documentación y evidencias. Los ZIP conservan los tres módulos de trabajo y sus parches verificables. No usar capturas de códigos vigentes como evidencia pública.

Validación: 46 pruebas Flutter aprobadas y flutter analyze sin hallazgos; 26 pruebas específicas de Django aprobadas en MySQL aislado, sin migraciones nuevas. Las ocho pruebas móviles del QR incluyen una emisión que termina en segundo plano y no debe reaparecer. Las cuatro nuevas pruebas de backend comprueban emisión propia/denegada, hash, rotación/expiración y rechazo de escritura clínica sin autorización. La integración nativa pasó en Pixel 6a: cuenta → mascota adoptada → expediente vacío real → emisión de QR → regreso al expediente y actualización. Registros: output/adopcion-movil/flutter-qr-20261119.log, backend-qr-20261119.log, analyze-qr-20261119.log y android-qr-20261119.log.

Continuidad: siguen pendientes fotos públicas con autorización y relación de almacenamiento explícitas, adjuntos médicos privados en móvil, perfil/recuperación de contraseña, mapa, tienda/donaciones y paginación. El lector QR para profesionales requiere su propia interfaz y reglas de sesión; este bloque no lo simula. La app sigue siendo un piloto local, sin firma ni publicación comercial.

Se recompiló el APK normal de QA desde lib/main.dart con la URL local, sin los defines privados de integración. Se comprobó integridad, ausencia de las credenciales sintéticas del ensayo, instalación y apertura en el emulador. Hash y resultados en output/adopcion-movil/validacion-qr-20261119.json. Los tres ZIP se regeneraron y revisaron para excluir .env, tokens, archivos privados, claves, builds y APK. Los parches pasan git apply --check --reverse sobre la base local revisada; esto no implica compatibilidad automática con otra base del equipo.


## Edición de perfil propio — 19 de noviembre de 2026

Se incorporó Mi cuenta → Editar perfil para nombre y teléfono opcional. La pantalla muestra el correo como dato de acceso de solo lectura. Guardar envía únicamente los campos modificados y refleja la respuesta confirmada por Django en la cuenta. Borrar explícitamente el teléfono lo elimina; un fallo conserva el borrador. Cancelar o volver ofrece seguir editando o descartar, sin escribir en el servidor. Al cerrar sesión se retiran los datos privados del formulario y una respuesta tardía no puede restaurar la identidad anterior.

El PATCH del perfil existente obtiene la cuenta desde la autenticación, bloquea su fila y vuelve a comprobar que esté activa. Rechaza IDs, correo, credenciales, roles y atributos administrativos, incluso si se envían junto a un nombre válido. Esta operación de datos propios no concede acceso a editar otras cuentas ni cambia el RBAC. La modificación y auditoría son atómicas: se registra quién cambió qué campos sin copiar el teléfono al evento, y una falla de auditoría revierte el cambio. Guardar valores iguales no duplica el evento. Las respuestas del perfil llevan no-store y nosniff; no se cambia el esquema.

Se conservan la paleta crema/salvia y controles nativos accesibles. Se consultó el perfil del Figma original 156:1796; no se copiaron el avatar, mascota ni switches de roles de ejemplo como datos reales. Durante la inspección en emulador se detectó que el teclado podía cubrir los botones. Se corrigió colocando las acciones dentro del área que se ajusta al teclado, con contenido desplazable separado. La prueba de 320 px y texto al 200 % verifica que guardar quede por encima del teclado simulado.

Reparto sin commits: José Carlos incorpora accounts/tests_mobile.py y 01-perfil-propio.patch (views y serializer); María José incorpora pantalla, PATCH del cliente, actualización segura de sesión y pruebas; Sally incorpora documentación y evidencias. Continúan pendientes recuperación/cambio de contraseña móvil, cambio de correo verificado, foto de perfil y cierre de cuenta; esta entrega no los simula. Las fotos públicas de mascotas siguen requiriendo una relación explícita de almacenamiento y autorización, sin reutilizar archivos privados del expediente.

También se detectó que, al reabrir inmediatamente el perfil después de guardar, la confirmación anterior podía cubrir una acción. Se retira esa confirmación al entrar a editar y se comprueba una segunda edición inmediata. No se silencian los fallos de interacción del ensayo Android: se espera que el botón pueda recibir el toque.

Incidencia de ensayo: durante una captura con pausas del runner de integración Android mostró un ANR por FocusEvent de más de 5 s. Se conserva la captura como diagnóstico, no como imagen de presentación. No se atribuye a una causa sin comprobarla: se retiraron las pausas del ensayo reproducible y se valida por separado el APK normal. La prueba en dispositivo físico sigue pendiente.

Validación funcional final: 54 pruebas Flutter aprobadas, flutter analyze sin hallazgos y 32 pruebas específicas de Django aprobadas en MySQL aislado. Las ocho pruebas del perfil móvil cubren guardado parcial, segunda edición inmediata, cancelación, retirada al cerrar sesión, error recuperable, eliminación explícita de teléfono, 320 px con texto al 200 %, teclado y respuesta tardía. Las seis pruebas de backend incluyen sobreasignación de campos, cuenta desactivada, aislamiento, validación, auditoría y rollback. No hay nuevas migraciones. La integración Android sin pausas de captura completó edición, persistencia y restauración de la cuenta sintética; registro android-perfil-20261119.log.

Comprobación independiente del APK normal: se recompiló desde lib/main.dart sin defines privados, se verificó integridad/base local/ausencia de credenciales y se instaló en Pixel 6a. Con controles Android reales por ADB se ingresó, se editó un teléfono sintético y se pulsó Guardar con el teclado abierto; el dato apareció confirmado en la cuenta. Se cerró la sesión y se restauró el teléfono en QA. La captura real perfil-teclado-apk-normal-20261119.png muestra el botón encima del teclado. Se observaron 0 ANR nuevos del paquete desde la compilación normal durante esta comprobación; esto no sustituye una validación prolongada o en dispositivo físico. Resultados y hash: validacion-perfil-20261119.json.


## Renovación visual compartida — 19 de noviembre de 2026

Se implementó la aplicación profesional de Modern Web Guidance, Adopt Liquid Glass y TypeUI en Android y panel web. Bienvenida usa #FCF0D3; el lienzo de las demás pantallas, #FFF9EC. Se mantiene la identidad de la app, con fuentes locales, componentes de lectura sólidos y vidrio acotado a capas funcionales. El login web conserva una petición inicial; la bienvenida Android no consulta el catálogo hasta explorar. El acceso y el registro están disponibles directamente desde la bienvenida.

Se verificaron 61 pruebas Flutter, flutter analyze sin hallazgos, el recorrido real de bienvenida/acceso/apariencia en Pixel 6a y 63 pruebas de regresión web/RBAC en MySQL aislado. Las capturas de navegador cubren 320–2560 px, claro/oscuro y contraste reforzado. Axe no detectó infracciones en login público, bienvenida, dashboard y matriz, en ambos temas. Se corrigieron filas y selecciones oscuras con contraste insuficiente. No se modificaron permisos ni modelos; no hay migración nueva.

Criterios y rutas: docs/diseno/23-materiales-y-paleta.md. Evidencias: output/diseno-materiales-2026-11-19. Los casos y cuentas visibles son sintéticos; no se generan imágenes ni historiales ficticios para fichas reales. Reparto: María José incorpora Android; Sally, estilos/plantillas web y documentación; José Carlos revisa integración y regresión. La copia sigue local, sin commits ni despliegues.


## Continuidad · registro pendiente y cambio de sesión · 19 noviembre

Se encontró una carrera en Android: si una petición de registro terminaba después de cerrar sesión o de entrar con otra cuenta, su inicio automático podía reemplazar la sesión elegida después. El registro ahora comprueba que sigue perteneciendo a la misma generación de sesión antes de iniciar acceso. Esto no revierte una cuenta que el servidor ya creó; evita un inicio de sesión tardío e involuntario.

- Se añadieron dos regresiones con respuestas demoradas: cerrar sesión durante el registro y entrar con otra cuenta mientras el registro espera.
- Pasan las 63 pruebas Flutter y el análisis no informa hallazgos. Evidencia: output/adopcion-movil/flutter-registro-sesion-20261119.log y analyze-registro-sesion-20261119.log.
- Pruebas HTTP simuladas, sin peticiones a Railway ni altas de usuarios reales. No cambia el RBAC ni el esquema de datos.
- Módulo para María José: frontend/mobile/lib/auth/session.dart y test/session_test.dart. José Carlos revisa el contrato de acceso; Sally conserva el módulo web y sus evidencias.
- Continuidad pendiente: fotos públicas autorizadas (revisar primero almacenamiento y permisos existentes), TalkBack/dispositivo físico, rendimiento y firma. Sin commits ni publicación.


## Continuidad · catálogo con texto ampliado · 19 noviembre

Las tarjetas del catálogo tenían una altura fija y nombres de una sola línea. Aunque no producían errores de layout en el ensayo anterior, reducían demasiado la lectura al ampliar texto. Ahora la cuadrícula calcula sus columnas con el ancho real y la escala del sistema: a 200 % en 390 px queda una columna, se reserva altura para el texto y los nombres y descripciones admiten dos líneas. No se limita el tamaño de fuente elegido por la persona.

Validación: 65 pruebas Flutter, análisis limpio y compilación debug de QA. Las nuevas regresiones comprueban la columna única, el nombre de dos líneas y el escalado no lineal de Android, junto con los casos existentes de 320×640 y 800×360 al 200 %. Evidencias: flutter-catalogo-accesible-20261119.log, analyze-catalogo-accesible-20261119.log y build-catalogo-accesible-20261119.log, en output/adopcion-movil. Se actualiza el módulo de María José; no cambia el backend ni el RBAC. Sin commits ni publicación.

Revisión preparatoria de fotografías: Mascota no tiene relación de foto pública. ArchivoDigital almacena metadatos y visibilidad, mientras DocumentoAdjunto pertenece al expediente y puede contener documentos privados. No se reutilizan adjuntos como imágenes públicas. El siguiente bloque debe incorporar una relación explícita de publicación, validación del archivo y retirada efectiva al revocar publicación o disponibilidad de adopción, con pruebas de autorización. Es necesario verificar primero la política de carga existente; no publicar URLs externas arbitrarias ni crear fotos ficticias para mascotas reales.


La comprobación en el APK normal detectó que Android amplía los tamaños pequeños de forma distinta a los grandes. Se ajustó el cálculo de columnas a la escala real del texto de 14 sp, en lugar de escalar un ancho como si fuera una fuente de 140 sp. Se verificó en Pixel 6a a 200 %, con una tarjeta por fila y se restauró la escala original del emulador. Captura: output/diseno-materiales-2026-11-19/android/08-catalogo-texto-200.png. La validación de TalkBack sigue pendiente.


## Continuidad · API de catálogo paginado · 19 noviembre

Se preparó `GET /api/adopcion/catalogo/` con páginas de 24 y cursor por ID estable. Reutiliza disponibilidad y visibilidad de adopción; conserva la lista anterior para que el APK actual siga funcionando. No hay cambios de modelos ni RBAC. Pasan 37 pruebas de API móvil en MySQL aislado, incluidas cinco nuevas de límite, privacidad, navegación, retirada y compatibilidad. Registro: output/adopcion-movil/backend-catalogo-paginado-20261119.log.

El cliente Android todavía no usa esta ruta: su integración con carga progresiva y filtros globales es el siguiente bloque independiente. No se afirma que la paginación ya esté disponible visualmente. Contrato, reparto y criterios: docs/diseno/24-catalogo-publico-paginado.md. Se actualiza el paquete de API de José Carlos y la documentación de Sally, sin commits ni publicación; el APK y la interfaz de María José conservan el corte anterior verificado.


## Continuidad · paginación conectada en Android · 19 noviembre

La app ya consulta el catálogo por páginas y muestra Cargar más. Los filtros se resuelven en Django sobre todas las mascotas publicables. El contador distingue resultados cargados de un total; no hay descarga automática de todas las páginas. El controlador conserva resultados ante un error de página, evita duplicados y descarta respuestas de filtros anteriores. Los enlaces siguientes se validan y se reducen a un cursor; no se sigue una URL externa con credenciales.

Validación: 73 pruebas Flutter, análisis limpio, 39 pruebas de API móvil en MySQL aislado e integración Android con 27 fichas sintéticas (24 + 3). El ensayo nativo tuvo que volver al encabezado virtualizado para comprobar el contador; no se confundió su ausencia fuera de pantalla con un fallo del servidor. Se añadió preparar_catalogo_qa y su limpieza reversible, con barrera de base local y manifiesto de IDs, para reproducir el ensayo sin datos reales. Contrato y comandos: docs/diseno/24-catalogo-publico-paginado.md.

Reparto: José Carlos recibe API y escenario QA; María José, cliente/controlador/interfaz/tests; Sally, documentación y registros. Sin cambios de RBAC ni esquema, sin commits ni publicación. Continúan fotos públicas autorizadas y almacenamiento, TalkBack/dispositivo físico y rendimiento.


Comprobación del APK normal de este bloque: compilado desde lib/main.dart con API local, sin defines privados; integridad, hash y ausencia de credenciales comprobados antes de instalar. Mediante controles Android se filtraron las 27 fichas temporales, se cargaron 24 + 3 y se visualizó QA Pagina 26. Se capturaron 09-catalogo-pagina-24, 10-catalogo-ultima-pagina y 11-catalogo-27-resultados en output/diseno-materiales-2026-11-19/android. Se ejecutó --limpiar y se devolvió la app al catálogo QA habitual. Resultado y hash: output/adopcion-movil/validacion-paginacion-20261119.json.


## Continuidad · fotografías públicas autorizadas en Django · 19 noviembre

Se implementó una relación explícita de foto pública, carga multipart con confirmación, normalización a WebP, descarga pública condicionada y retirada. Reutiliza mascotas.publicar_adopcion y su contexto; no abre documentos del expediente ni concede permisos nuevos. La autorización se vuelve a comprobar después del procesamiento para respetar revocaciones concurrentes. La migración animals.0007 agrega una tabla vacía; se aplicó solo en MySQL QA local, donde no hay fotos publicadas.

Pasan 303 pruebas Django, incluidas 13 nuevas de fotos, autorización/denegación y límites. Se verificó HTTP local: foto inexistente 404 con no-store y carga anónima 401. Se fijó Pillow 13.0.0 y se habilitó LPN_PRIVATE_ROOT como ruta configurable con el mismo valor predeterminado. El almacenamiento real requiere volumen persistente y respaldo antes de despliegue; Railway permanece intacto.

La integración visual todavía está pendiente: Sally debe incorporar carga/retirada en el panel y María José consumir descriptores explícitos en catálogo/ficha, evitando peticiones a mascotas sin foto. José Carlos recibe modelo, migración, dependencia, configuración, servicios/rutas y pruebas. Guía: docs/diseno/25-fotografias-publicas-autorizadas.md. Evidencias en output/adopcion-movil/backend-fotos-*.log y validacion-fotos-publicas-20261119.json. El APK no cambia en este bloque. Sin commits ni publicación.


Incidencia de validación documentada: un reintento con --keepdb encontró datos residuales y produjo fallos de recuento/duplicados. La regresión final se ejecuta en un esquema de tests recreado y destruido por Django; la base QA de aceptación se conserva. Se registra DT-07 para investigar el aislamiento, sin atribuir una causa aún no comprobada. También se verificó la ruta privada configurable sin escribir archivos. Un fallo de disco en las operaciones de foto devuelve 503 genérico y no expone rutas.


## Continuidad · fotos publicadas visibles en Android · 19 noviembre

El catálogo y la ficha reciben un descriptor opcional de imagen, condicionado a publicación y custodia vigente. Android valida que la ruta corresponda a la misma mascota y al origen configurado; evita enlaces externos y documentos privados. Sin descriptor no hace peticiones de fotos. Incluye estado de carga, marcador ante error, reintento explícito y límite de decodificación. Una versión de publicación distinta actualiza la imagen; una retirada se refleja al refrescar los datos.

Pasan 77 pruebas Flutter, análisis limpio y 306 pruebas Django en una base limpia. La consulta del catálogo no hace un acceso de foto por mascota. El ensayo Android decodifica WebP real desde Django en catálogo y ficha, usando exclusivamente un patrón rotulado IMAGEN SINTETICA y una ficha QA temporal. Se sustituyó FileResponse en este GET acotado por una respuesta binaria limitada para evitar su adaptación síncrona bajo ASGI. No hay migración nueva ni cambio de permisos.

Código, reproducción y reparto: docs/diseno/26-fotos-publicas-en-android.md. José Carlos incorpora los descriptores y el escenario; María José, componente/modelo y pruebas; Sally, guía/evidencias y próximo formulario del panel. Sigue pendiente la carga/retirada visual en el panel, además de almacenamiento persistente y restauración antes de usar fotos reales. Sin commits ni publicación.

La inspección del APK normal detectó un aviso antiguo de foto no disponible incluso con imagen y un recorte innecesario en la ficha. Se condicionó el aviso y se conserva la imagen completa en detalle; el ensayo nativo verifica ambas correcciones.

APK normal final: compilado desde lib/main.dart sin credenciales, instalado y comprobado con controles Android. Las capturas 12-catalogo-foto-qa.png y 13-ficha-foto-qa.png muestran el patrón temporal; se retiraron ficha, metadatos y WebP y se restauró el catálogo habitual. Hash y comprobaciones: output/adopcion-movil/validacion-fotos-movil-20261119.json.


## Continuidad · publicación y retirada visual de fotos · 19 noviembre

Se completó Mascotas → Fotografía en una pantalla propia, con selección nativa, vista previa local sin POST, consentimiento no premarcado y envío explícito. Los cambios sin publicar se pueden continuar o descartar; no se publica implícitamente al salir. La retirada tiene confirmación en pantalla y aplica las mismas reglas de servicio, permiso/contexto y CSRF. Se tradujeron etiquetas/ayudas y se preservaron temas, paleta y navegación.

Pasan 316 pruebas Django, incluidas diez web nuevas. En navegador se comprobaron publicación única, vista previa sin envío, validación local, limpieza, cancelación, retirada, idioma, cero errores JS y 320–2560 px sin desbordes. Axe no encontró infracciones en esta pantalla en claro/oscuro. La inspección detectó que el marcador genérico de bajas requería campos que no existen en fotos; se separó la exigencia de envío explícito para evitar el error sin modificar las bajas existentes.

Se comprobó Android con el APK normal existente: la imagen publicada desde el panel apareció en la ficha. Se retiró desde el panel (GET de imagen 404), se eliminaron los datos/archivo temporales y se volvió al catálogo QA habitual. Guía y reparto: docs/diseno/27-fotografias-desde-panel.md. Sally incorpora el módulo web; José Carlos revisa el servicio y María José la lectura móvil. Sin migraciones nuevas, commits ni publicación. Siguen pendientes persistencia/restauración, validación física/TalkBack y rendimiento para un piloto real.

El retorno de la pantalla de fotografía utiliza el nombre actual del recurso, y cuenta con una regresión de renombrado. Se verificó además la aplicación secuencial de los parches de traducción previos y de la nueva pantalla en una copia aislada.


## Continuidad · fidelidad al Figma original · 19 noviembre

La revisión visual anterior era una interpretación y el usuario pidió una reproducción más fiel en todas las pantallas. Se consultaron directamente los frames de bienvenida, login, catálogo y perfil. Se recuperó JetBrains Mono y se ajustaron sombras cálidas, campos translúcidos, botones beige, tarjetas, menús y diálogos comunes. La bienvenida recupera la composición del original y el catálogo separa imagen y texto. Los datos de mascotas continúan viniendo de la API; no se colocan fotos del mockup en registros reales.

Pasan 77 pruebas Flutter, análisis limpio y 48 pruebas de regresión del panel. Se comprobó el APK normal en el emulador y el navegador a 320, 390, 1366 y 2560 px. El login conserva una única petición inicial; el dashboard revisado no presenta infracciones Axe en claro/oscuro. Se mantienen reducción de transparencias, navegación por permisos y adaptación al texto al 200 %. Guía y límites: docs/diseno/28-fidelidad-figma.md. Capturas comparadas en output/fidelidad-figma-2026-11-19, con referencias separadas de la implementación.

María José incorpora componentes/recursos y pruebas Flutter; Sally, estilos y plantilla de acceso web y documentación; José Carlos valida la integración. No se afirma coincidencia píxel a píxel de todas las vistas: existen pantallas funcionales sin equivalente en Figma, contenido dinámico y controles accesibles adicionales. Sin commits ni publicación.


## Continuidad · trazabilidad de la solicitud ciudadana · 19 noviembre

Se detectó una diferencia real: el panel registraba la creación mediante su envoltorio, pero una solicitud enviada directamente desde Android no emitía el evento ni actualizaba la revisión del panel. La API ahora llama al servicio auditar existente dentro de la transacción de creación, con actor, solicitud, mascota, fundación y estado Pendiente. No registra observaciones privadas ni duplica el evento genérico web.

Pasan 323 pruebas Django en MySQL local aislado con esquema recreado, incluidas siete nuevas de éxito, duplicado, anonimato, rol revocado, indisponibilidad, fallo de auditoría y recorrido web. El fallo de auditoría revierte la solicitud; el middleware registra el intento fallido por separado, por lo que la revisión puede aumentar legítimamente sin que exista una solicitud nueva. Evidencias: backend-solicitud-auditoria-20261119.log, backend-solicitud-regresion-20261119.log y validacion-solicitud-auditoria-20261119.json en output/adopcion-movil.

José Carlos incorpora un parche independiente de adoption/api.py y sus pruebas; Sally, guía 29 y evidencia; María José conserva el contrato de respuesta y recibe el estado actual del diseño en su módulo. Se actualizan los tres paquetes con la revisión de fidelidad, fuentes locales/licencias y este arreglo, verificando sus parches y contenido. No hay migración, permiso nuevo, commit ni publicación. Pendientes: validar almacenamiento/restauración y rendimiento del piloto, dispositivo físico/TalkBack, firma y revisión visual de pantallas aún sin correspondencia exacta con Figma.


## Continuidad · encabezados accesibles y medición local · 19 noviembre

Se localizaron encabezados de altura fija en Notificaciones y confirmaciones, y aproximaciones duplicadas en reportes y mascotas. Se centraliza la medida real de fuente/escala/ancho en lpn_app_bar.dart, con estilo de sección de 15 sp del Figma, espacio para volver/acciones y hasta tres líneas para nombres largos. Se aplica a todas las barras de pantallas secundarias; la barra de marca del inicio conserva su composición propia.

Pasan 81 pruebas Flutter, incluidas cuatro nuevas de título al 200 %, navegación de regreso y acción de actualización en horizontal. Análisis limpio y APK normal compilado sin credenciales, instalado y comprobado en Pixel 6a con texto al 200 %. Se guardaron 08-notificaciones-texto-200.png y 09-notificaciones-normal.png en output/fidelidad-figma-2026-11-19 y se restauró la escala original 1.0. No se alteraron cuentas ni registros de negocio. Guía 31 y validacion-encabezados-20261119.json documentan alcance y límites; TalkBack/físico siguen pendientes.

Además, se midieron catálogo, ficha y documento de login sobre QA local con cinco registros: p95 secuencial de 35,48 / 34,53 / 48,84 ms; cuatro clientes concurrentes dieron 62,35 / 54,59 / 71,10 ms. Son muestras de veinte solicitudes por modalidad, sin WAN, TLS ni renderizado, y no demuestran tiempos de producción. La primera muestra no es un arranque en frío. Se entrega scripts/medir_rendimiento_local.py y la guía 30 con cómo revisar Network/Timing y sin incluir credenciales o HAR privados. El documento inicial pesa 228.045 bytes recibidos en este ensayo; contar una única petición no sustituye medir su tamaño.

María José incorpora el componente y las pantallas/tests móviles; José Carlos, el script de medición local; Sally, guías/evidencias. Backend y RBAC no cambian en este bloque; se conserva la regresión previa de 323 pruebas Django. Paquetes separados actualizados, sin commits ni publicación. Continuidad: ampliar la comparación visual de vistas sin equivalencia exacta, validar almacenamiento/restauración y una preproducción de rendimiento autorizada, dispositivo físico/TalkBack y firma.


## Continuidad · recuperación de una solicitud sin confirmación · 19 noviembre

El formulario habilitaba de nuevo Enviar tras una respuesta perdida, aunque el servidor podía haber creado la solicitud. Ahora distingue resultados no confirmados (timeout, 5xx o respuesta de éxito malformada), conserva la nota y dirige con un solo botón a Mis solicitudes. No repite el POST ni anuncia un éxito no comprobado. Los errores explícitos corregibles permiten editar; cancelar sigue disponible y un doble clic no duplica el envío.

Ocho regresiones nuevas verifican los estados, el recorrido completo catálogo/ficha/acceso/consulta y la visibilidad de las acciones a 320×640 y 800×360 con texto al 200 %. El caso de respuesta perdida usa HTTP simulado: el servidor ficticio del test guarda el resultado, pierde la respuesta y la lista recupera la solicitud pendiente con un POST y una consulta explícita. No se provocan fallos ni se crean solicitudes en Railway. El backend y sus protecciones/auditoría no cambian en este bloque.

Se ejecuta la suite móvil actual de 89 pruebas, análisis y compilación debug normal con API QA local. El APK se instaló en el emulador de este proyecto y se comprobó el inicio/catálogo; el escenario de fallo se verifica mediante tests, sin presentarlo como una interrupción real en producción. Evidencia y límites en guía 32 y flutter-envio-incierto-20261119.log. María José incorpora formulario/tests; Sally, guía/evidencias; José Carlos conserva el contrato y la regresión anterior de 323 pruebas Django. Sin migraciones, commits ni publicación.


## Continuidad · presupuesto de respuestas y cancelación HTTP · 19 noviembre

Se observó que ApiClient acumulaba cualquier respuesta completa antes de validar JSON, y el plazo de Future.timeout no enviaba una señal de cancelación. Ahora el cuerpo acumulado tiene un límite de 1 MiB, comprobado por longitud declarada y por bloques reales; al excederlo se cancela la lectura. El plazo normal sigue en quince segundos y activa AbortableRequest de http 1.6.0 ya instalado. No se cambia la API del servidor ni se añade una dependencia. Se conservan los estados HTTP de error para no alterar renovación, denegación o límites de intentos; un 2xx excesivo permanece sin confirmar.

Pasan 99 pruebas Flutter, diez nuevas de presupuesto, longitud falsa/ausente, límite exacto, cancelación, reutilización y estados. Una prueba usa el transporte IO real contra un servidor de loopback que deja un cuerpo incompleto y después responde a una segunda consulta. El resto usa HTTP simulado. Análisis limpio, compilación debug QA e instalación del APK normal; se verificó que el catálogo sintético sigue cargando. No se probaron fallos en Railway ni se crearon datos de negocio. Se aclara que abortar red no revierte una transacción y que 1 MiB de cuerpo no equivale al consumo total de RAM.

Evidencias: flutter-red-acotada-20261119.log, analyze-red-acotada-20261119.log, build-red-acotada-20261119.log y validacion-red-acotada-20261119.json en output/adopcion-movil; captura 11-catalogo-red-acotada.png en output/fidelidad-figma-2026-11-19. Guía 33. María José incorpora cliente/tests; Sally, documentación/evidencias; José Carlos revisa futuros contratos que requieran paginación. Backend y RBAC se mantienen, con la regresión previa de 323 pruebas Django. Paquetes separados actualizados y comprobados, sin commits ni publicación. Continúan validación física/TalkBack, almacenamiento/restauración, preproducción de carga y firma, además de la comparación visual pendiente.


### Revisión local: composición del catálogo (19 de noviembre)

Se aproxima la composición al frame 108:376 sin sustituir datos reales por imágenes de ejemplo. 102 pruebas Flutter y análisis aprobados; APK verificado en emulador a escala normal y 200 %. Se documentan diferencias aún pendientes en [la guía 34](../diseno/34-composicion-catalogo-figma.md). Sin commits ni publicación.


## Continuidad · navegación y ficha según Figma · 19 noviembre

La comparación de los frames 108:376 y 128:502 mostró una barra flotante ajena al original y una ficha con hechos públicos demasiado dispersos. Se recupera navegación de ancho completo, línea superior, marca central y vectores originales, manteniendo destinos funcionales y objetivos de 48 puntos. La selección también se anuncia mediante semántica. La ficha usa las cápsulas verdes y una historia visual con organización/fecha/ciudad y disponibilidad reales; no inventa vacunas, rescates ni expone expedientes o QR públicos. La acción de adopción permanece visible. El material de la historia compone el crema sobre el lienzo para evitar que la sombra tiña todo el fondo.

Pasan 108 pruebas Flutter y análisis limpio; APK normal debug QA compilado. Se comprueban los cuatro destinos en el emulador, con capturas normales y al 200 % y restauración de escala. Se agregan cuatro regresiones de navegación y dos de veracidad/lectura de la ficha. No cambian backend, autorización ni registros de negocio; no es necesario repetir la suite Django por cambios exclusivamente de presentación Android. La regresión previa de 323 pruebas Django se conserva como evidencia histórica, no como una ejecución nueva de este bloque.

Guía 35, logs y JSON locales identifican alcance y límites. María José recibe Android, Sally documentación/evidencias; José Carlos conserva los contratos. Se regeneran módulos sin commits ni publicación. Continuidad: perfil, rescates, formularios/estados y panel web deben seguir comparándose con sus frames; no se declara fidelidad global ni producto comercial terminado. Firma, prueba física/TalkBack y preproducción autorizada siguen pendientes.


## Continuidad · perfil y roles propios Android · 19 noviembre

La revisión del frame 156:1796 reorganiza Mi cuenta con tarjeta crema de identidad, avatar predeterminado original y secciones de 15 puntos. Mis roles deja de ser un hueco del prototipo: consume el endpoint autenticado existente de accesos propios y distingue identificadores de rol globales y por organización. Son de solo lectura; no se implementan switches que permitan autoasignarse privilegios. No se inventan mascotas o vacunas del mockup.

Pasan 115 pruebas Flutter, siete nuevas de lectura, denegación, contratos inválidos, contextos, logout/respuestas tardías y tamaño 320 con texto al 200 %. Las ocho pruebas anteriores de edición de perfil siguen aprobadas. Análisis limpio y APK normal debug QA compilado. Se comprueba localmente el endpoint real con anónimo 401 y ciudadano sintético 200; se revoca la sesión del ensayo. El APK se verifica con el ciudadano QA sin modificar datos de negocio y se cierra su sesión, restaurando la escala del emulador. Backend, permisos y contratos no cambian; la regresión Django previa de 323 pruebas es histórica, no una nueva ejecución.

Guía 36 y capturas 19/20 documentan la referencia y sus diferencias funcionales. Los códigos de rol son identificadores, no sus nombres editables: el contrato actual no proporciona estos últimos y no se derivan etiquetas ficticias. No hay polling; se consulta al entrar y al actualizar explícitamente, y el servidor comprueba cada operación. María José integra Android; Sally, documentación/evidencias; José Carlos conserva la API. Sin commits ni publicación. Siguiente bloque: rescates/formularios/estados y revisión visual del panel web; validación física/TalkBack y firma continúan pendientes.


## Continuidad · dashboard web según Figma · 19 noviembre

Se revisan contexto y capturas de los nodos 9:124 y 9:129 del panel: usaban Inter, mientras la implementación había trasladado indebidamente JetBrains Mono desde móvil. Se recupera Inter para el panel, saludo de 32 px y cifras ligeras; móvil/login conservan su tipografía. El carrusel de indicadores se sustituye por cuadrícula para mostrar los cinco del administrador QA a 1366 px sin desplazamiento horizontal ni controles extra. Valores, enlaces autorizados y traducción se conservan. Paneles de lectura claros y separación de 24 px evitan bloques unidos o sombras excesivas.

Pasan 29 regresiones Django pertinentes en test_lpn_rbac_sandbox recién creado y destruido después: relación contador/listado, idioma, navegación configurable y RBAC dinámico. El navegador verifica administrador/ciudadana en cinco anchos, texto al 200 %, menú plegable, cabecera fija, temas claro/oscuro y colores forzados. Axe no registra infracciones en los dashboards y la matriz inglesa revisados; no equivale a certificación global. Se conserva una sola petición inicial en login. Son 26 comprobaciones registradas y cero errores JavaScript supervisados. Capturas 21–27, JSON y logs en los directorios de evidencia, guía 37.

Se reinicia exclusivamente el ASGI QA identificado para invalidar las plantillas en caché, sin migrar, sembrar o alterar roles. Se renuevan sesiones sintéticas locales para el navegador. Sally recibe materiales.css e inicio.html completos en el módulo 03; no basta el CSS para sustituir el HTML del carrusel. José Carlos y María José conservan sus módulos. APK y 115 pruebas Flutter son evidencia del bloque anterior, sin nueva compilación móvil. Sin commits ni publicación. Continuidad: auditoría/actividad debe describir con claridad las acciones nuevas de fotografía; después seguir listados/formularios web y rescates móvil.


## Continuidad · actividad y auditoría legibles · 19 noviembre

Se corrige la descripción de las operaciones nuevas de fotografía (incluidos alias históricos), contacto y solicitud de adopción. Dashboard y auditoría usan el mismo presentador; los códigos almacenados permanecen intactos y visibles en el detalle. Se explican fallos/rechazos sin inferir causas o rollback; se añaden únicamente dimensiones/bytes, nombres de campos y estado HTTP registrados. El resultado del detalle se traduce, sin mostrar EXITO como etiqueta.

Pasan 27 pruebas Django en MySQL local aislado, con nueve regresiones nuevas de presentación, privacidad, traducción, conservación de eventos y denegación al ciudadano. La prueba de navegador confirma actividad y detalle en español e inglés con registros QA existentes, sin crear cambios de negocio. Se actualiza solo el ASGI identificado y se renuevan sesiones sintéticas. Guía 38, capturas 28/29, JSON y logs registran alcance. Sally recibe archivos web completos, presentador, pruebas y traducciones PO/MO finales; José Carlos/María José mantienen sus módulos. No se repite Flutter ni se cambia el APK (115 pruebas del bloque móvil anterior). Sin commits ni publicación. Continuidad: ampliar eventos históricos genéricos y seguir revisión de listados/formularios web y rescates móvil.


## Continuidad · rescates móvil y búsqueda local · 19 noviembre

Tras comparar el frame 8:44, la búsqueda vuelve a la ilustración de rescates y el título recupera 15 puntos; con texto ampliado se aparta del buscador. Reportar queda accesible antes del listado y las acciones secundarias se agrupan sin duplicar encabezado/campo de búsqueda. Se reutiliza el WebP original. Se filtran situación, estado y descripción sin distinguir tildes/mayúsculas; limpiar no vuelve a consultar. No se inventan ciudad, mapas, fotografías o casos que el endpoint público no devuelve.

Pasan 121 pruebas Flutter, seis nuevas de disposición, acción inicial, búsqueda/limpieza sin red, texto ampliado y reintento. Se conservan pruebas de envío autenticado/anónimo y seguimiento. Análisis limpio y APK debug normal para QA local; capturas 30/31 y guía 39. Se restaura la escala del emulador y no se crean reportes de negocio para la demostración. Backend, permisos y contratos intactos; no se repite Django por cambios de presentación/búsqueda local Android. María José recibe Android, Sally documentación/evidencias, José Carlos conserva API. Paquetes separados y comprobados, sin commits ni publicación. Continuidad: búsqueda global/paginación pública (límite actual 100), más formularios/estados web y validación física/TalkBack/firma/rendimiento.


### Revisión integral de composición móvil (local, 19-11-2026)

Se revisaron los 29 frames de Figma. Se recuperaron las tarjetas horizontales y categorías originales de Rescates, etiquetas externas de acceso, registro con confirmación local, solicitud en página con acciones fuera del scroll, mascotas reales dentro del perfil y confirmación de reporte con identidad original. Cabeceras y botones se ajustaron al prototipo. 123 pruebas Flutter pasan y el análisis está limpio. Ver `docs/diseno/40-auditoria-integral-mobile-figma.md` para la matriz de pantallas y diferencias pendientes; mapa, tienda, apadrinamiento y algunos contratos del prototipo siguen pendientes. No se publica ni se declara un calco completo.


## Continuidad · privacidad y reintento del perfil · 19 noviembre

Se añaden tres regresiones para la vista de mascotas dentro del perfil: datos propios y ocultación de expediente cuando hay custodia vigente; respuesta 403 con reintento explícito sin bucle de red; respuesta tardía después de cerrar sesión sin reinsertar información privada. También se comprueba que el perfil anónimo no consulta mascotas y que actualizar roles no repite esta consulta. Las pruebas detectaron una excepción real al reintentar: la asignación de un Future devolvía ese Future desde setState. Se separa la petición del callback síncrono.

Pasan las 126 pruebas Flutter y el análisis no registra incidencias. Se compila APK debug normal de QA local; no se altera autorización, contratos, permisos ni datos. Las comprobaciones nuevas usan MockClient sin conexiones ni escrituras MySQL. María José recibe corrección y pruebas Android; Sally documentación/evidencias; José Carlos mantiene API sin cambios. Paquetes regenerados, sin commits ni publicación. Pendientes: composición del expediente privado, contratos reales de fotografía de reporte/mapa/tienda/apadrinamiento y validación física/TalkBack; la guía 40 conserva la auditoría de los 29 frames.


## Continuidad · formularios legibles y vidrio acotado · 19 noviembre

Se revisa la guía de los 17 vídeos, fundamentos TypeUI y Adopt Liquid Glass, y se vuelve al frame original de reporte. La nueva petición autoriza cambiar la tipografía: Inter para la interfaz Android, manteniendo marca, ilustraciones, crema y saludo manuscrito. Se reducen sombras por campo y se definen radios de 24/14/18/28 para grupos/campos/botones/barras. Reporte se organiza en Situación, Ubicación y Contacto; solicitud destaca animal e identidad real, motivo opcional y siguiente paso. Navegación y acciones reciben vidrio recortado con alternativa sólida; lectura queda sobre papel claro. Botones principales en negrita y salvia, secundarios con menor énfasis.

Se corrige además el encuadre del autocompletado de ciudad al ampliar texto, y se adaptan pruebas y recorrido Android al nuevo orden de campos. Las pruebas de navegación cargan Inter real para comprobar geometría. Pasan 126 pruebas Flutter; análisis limpio y APK debug QA. Ratios calculados: texto principal 11,98:1, apoyo 6,29:1, botón salvia 7,46:1 y borde de campo 3,70:1 sobre su fondo. No certifica accesibilidad global ni rendimiento físico. Guía 41 distingue los fundamentos aplicados, conservados y ajenos a estos formularios.

María José: Android, materiales/formularios y regresiones. Sally: guía, sistema visual y evidencias. José Carlos: API sin modificaciones de este bloque. Se regeneran capturas/mosaico y paquetes separados tras verificar la compilación. Sin commits, despliegue o cambios de permisos. Continuidad: composición clínica compacta, microtipografía restante del catálogo, contratos pendientes de mapa/foto de reporte/tienda/apadrinamiento y validación física/TalkBack.


## Continuidad · lectura del catálogo y anuncio accesible · 19 noviembre

Se completa el ajuste pendiente del catálogo: nombres Inter 16 seminegrita, resúmenes 14 y microetiquetas/filtros 12; título de sección 18. La cuadrícula calcula la altura con los estilos que realmente pinta, conserva dos columnas cuando hay espacio y pasa a una con texto ampliado. Banner, fotografías dinámicas, paginación y filtros globales se conservan.

Dos regresiones nuevas comprueban nombres largos a 320 px, texto normal/al 200 %, objetivos alcanzables, anuncio completo y una sola consulta de catálogo al recorrerlos. Detectaron duplicación del anuncio por combinación de la etiqueta del botón y el texto de sus hijos; la ficha ahora publica un único nombre accesible completo y conserva acción táctil y de accesibilidad. No se cambia el acceso a fotos ni la autorización. Pasan las 128 pruebas Flutter, análisis limpio y compilación del APK debug QA. No se escriben datos en estas pruebas (MockClient).

María José recibe catálogo y pruebas; Sally documentación y evidencias; José Carlos conserva API. Capturas/mosaico y módulos se regeneran al validar el APK. Sin commits ni publicación. Continuidad: expediente privado compacto y contratos pendientes; lector de pantalla físico aún requiere validación manual.


## Continuidad · distribución verificable del catálogo · 20 noviembre

Se cierra la distribución que había quedado pendiente: el APK debug QA contiene el catálogo con nombres 16, resúmenes 14 y filtros 12; conserva 128 pruebas Flutter aprobadas y análisis limpio del bloque anterior. No se repite la suite sin cambios de código. Se verifica que el SHA-256 de la aplicación instalada coincide con el APK distribuible. Se vuelve a capturar el recorrido nativo con datos sintéticos, sin enviar solicitudes/reportes ni emitir QR, y se actualiza el mosaico y su identificación de compilación. La sesión QA se cierra al terminar.

Se regeneran los tres módulos y se comprueban fuentes, integridad, contexto de parches y exclusión de secretos. María José recibe Android y sus pruebas; Sally documentación y evidencias; José Carlos conserva API. Sin commits, ramas, publicaciones ni cambios en Railway. El APK sigue siendo un piloto de QA local. La revisión de referencias solicitada por el usuario se conserva como orientación; no se instalan herramientas nuevas ni se inicia otra sustitución global del estilo en este bloque.

Continuidad: resolver una pantalla de formulario, una ficha y el shell con referencias coherentes antes de extender cambios visuales; expediente privado compacto, contratos reales pendientes de mapa/foto de reporte/tienda/apadrinamiento y validación física/TalkBack/firma permanecen abiertos. Los 128 tests automatizados no certifican TalkBack ni rendimiento en dispositivo físico.


## Continuidad · límites de sesión del expediente privado · 20 noviembre

Se añaden tres regresiones de privacidad del expediente: respuesta clínica tardía después de cerrar sesión; cambio de Ana QA a Carlos QA durante una consulta, con nueva comprobación que devuelve 403; actualización que oculta el registro previo mientras espera y solo reintenta tras una acción explícita. Se comprueba que nunca reaparecen los datos ni el botón QR del expediente de la cuenta anterior, y que no hay consultas repetidas automáticamente. Los tres escenarios pasan con la implementación existente; no fue necesario modificar código de ejecución, autorización ni contratos.

Pasan las 131 pruebas Flutter y el análisis está limpio. Logs flutter-expediente-sesion-20261120.log y analyze-expediente-sesion-20261120.log; pruebas con MockClient y usuarios sintéticos example.invalid, sin conexiones ni escrituras de datos de negocio. No se recompila ni recaptura el APK porque no cambia la aplicación; el APK y las 25 capturas del bloque anterior conservan su hash y metadatos de compilación. El contador 131 corresponde a la suite actual, no a otra versión visual.

María José: pruebas Android; Sally: continuidad, documentación y evidencias; José Carlos: API sin cambios. Se renuevan módulos separados y comprobaciones de integridad/privacidad. Sin commits ni publicación. Continuidad: revisar composición compacta del expediente con las referencias antes de otro cambio general del diseño, y continuar contratos pendientes y validación física. Esta regresión automatizada no certifica una evaluación manual de TalkBack ni sincronización en segundo plano de permisos del servidor.


## Continuidad · API pública de reportes paginada · 20 noviembre

Se prepara el contrato que elimina el límite de consulta de los 100 reportes recientes: GET /api/reportes/publicos/ entrega páginas de 20 con cursor y búsqueda aplicada antes del límite. El selector de ocultación se comparte con la ruta anterior, que conserva su lista de hasta 100 para mantener compatibilidad. No se publican contactos, claves ni campos adicionales. Se acotan parámetros y se añade un presupuesto de lectura anónima independiente; paginar no consume el presupuesto general usado por acceso/opciones. No se cambian permisos de edición, moderación ni modelos.

Pasan 17 pruebas Django en una base MySQL local aislada recién creada y destruida: 105 reportes, búsqueda antigua, ocultación entre páginas, contrato legacy, privacidad, parámetros, una consulta por página, lectura sin escritura y presupuesto separado; se conservan ensayos móviles y de moderación/titularidad. Se corrigió el montaje de fixtures para MySQL, que no devuelve los IDs de bulk_create, y se separó la IP de las pruebas de lectura de los ensayos de registro. Log backend-reportes-paginados-20261120.log; guía 42 explica límites y reproducción. No se modifica ni consulta Railway.

Esta parte es de API: Rescates e Historias Android siguen con el contrato anterior y la búsqueda local de hasta 100 filas. La integración móvil con búsqueda temporizada, paginación y respuestas fuera de orden es la siguiente tarea; no se declara resuelto todavía ese límite en la interfaz. Se conserva APK y capturas, sin repetir Flutter por cambios exclusivos de backend (suite vigente: 131 pruebas del bloque anterior). Se revisó el frame 128:599 del expediente; no se trasladan su carnet/QR de ejemplo a fichas reales.

José Carlos: selector, vista/ruta, pruebas y parche independiente; Sally: guía y evidencias; María José: siguiente integración Android. Módulos separados actualizados con verificación de parches y secretos. Sin commits ni publicación. Pendientes: integración móvil descrita, búsqueda escalable/ensayos de carga, expediente compacto y contratos de mapa/foto de reporte/tienda/apadrinamiento, además de validación física.


## Continuidad · búsqueda y paginación de Rescates en Android · 20 noviembre

Android consume el contrato público de la guía 42. El buscador del banner espera 400 ms desde la última edición y consulta todo el conjunto visible del servidor, reiniciando el cursor; ya no filtra únicamente las primeras 100 filas. Casos activos conserva su carrusel y ofrece Cargar más. Historias comparte los datos consultados, incluye estados archivados y permite continuar páginas sin repetir la descarga al abrir. Si hay un filtro, explica su texto. No se cambian imágenes estáticas ni se inventan fotografías/datos de animales.

El controlador invalida respuestas antiguas desde que cambia el texto, también si una página anterior sigue pendiente. Evita peticiones duplicadas al cargar, conserva resultados ante un error de página y solo reintenta al pulsar. El parser acota el sobre a 20 filas, valida el cursor y detecta falta de progreso. Reportar recibe texto de 14 para mejorar lectura. Las pruebas de búsqueda anteriores se adaptan al nuevo contrato: limpiar sí consulta la primera página. Se preservan regreso, cancelación y envíos existentes.

Pasan 138 pruebas Flutter y el análisis está limpio; APK debug QA compilado e instalado con hash comprobado. Se capturan de nuevo las 25 vistas y se renueva mosaico/comparación. Una comprobación nativa adicional muestra la búsqueda del servidor y un registro de la segunda página en Historias. Solo se usan datos sintéticos de MySQL local ya existentes; se verifican cuentas example.invalid/anonimato y descripciones de ensayos, sin sembrar ni enviar reportes/adopciones/QR. La sesión QA se cierra. Evidencias en reportes-paginados-2026-11-20 y logs *reportes-paginados-20261120.log.

El emulador estaba cerrado; se inicia una instancia Pixel_6a sin ventana, sin interrumpir otro emulador. Durante el arranque frío Android mostró un ANR de System UI; se recuperó con Esperar antes del recorrido. Se documenta esa limitación; no es una certificación de rendimiento físico ni un ANR atribuido a la app. Una captura de consulta tomada antes de asentarse el dibujo se sustituyó por otra captura nativa del mismo APK y consulta; no se retocaron imágenes.

María José: API cliente, controlador, pantallas y pruebas Android. Sally: guía, documentación, capturas y evidencias. José Carlos: conserva API paginada y 17 pruebas verificadas del bloque anterior. Paquetes regenerados y examinados con parches y exclusión de secretos. Sin commits, ramas, publicación o Railway. Para integrar, backend primero y después Android. Continuidad: expediente compacto, contratos reales pendientes de fotografía de reporte/mapa/tienda/apadrinamiento, búsqueda especializada y caché compartida para varias instancias, validación física/TalkBack/firma.


## Continuidad · muestra HTTP local de reportes · 20 noviembre

Se amplía el medidor existente con --reportes: primera página, búsqueda y continuación. Máximo 34 GET de lectura, sin cambiar el límite de 60/minuto ni crear datos. Se conservan los ensayos anteriores de catálogo/login. Se rechazan redirecciones, rutas no permitidas y respuestas de más de 1 MiB; una prueba con HTTP sintético en loopback verifica esas barreras sin MySQL.

En la muestra local debug se observan medianas secuenciales de 19,53/14,65/13,44 ms, con cuerpos de 2.808/335/1.283 bytes. No incluyen TLS, WAN, Railway ni renderizado; el servicio ya estaba activo y los datos son pocos. La guía 43 explica el límite estadístico y la diferencia con los 400 ms intencionales del buscador. JSON de resultados y log de la prueba de barreras se distribuyen con el hash del script medido. No se extrapola a producción ni se repite el ensayo innecesariamente.

José Carlos: herramienta y prueba; Sally: guía/evidencias; María José: Android intacto. Se mantienen APK y 138 pruebas Flutter del bloque anterior, sin recompilar o repetir suites por documentación/herramientas. Paquetes actualizados y verificados; sin commits ni publicaciones. Continuidad funcional y visual del bloque previo permanece abierta, además de medición física/preproducción autorizada con datos representativos.


## Continuidad · controles y barra inferior según Figma · 20 noviembre

Se comparan contexto y captura de bienvenida 3:2, acceso 5:7 y Adoptar 108:376. La variante anterior había introducido salvia plana y cápsula flotante por decisión de implementación. Se recupera radio 15,5 en botones/campos, crema/beige, borde cálido y sombra; se conserva Inter y los objetivos táctiles. La franja inferior vuelve a cubrir el ancho con línea superior, vidrio crema y selección discreta, manteniendo cuatro destinos y logo. Home retira la barra con teclado de inset inferior positivo y conserva la selección al volver.

La revisión nativa detecta que una sombra aplicada al contenedor completo manchaba el texto de error. RaisedInputBorder la pinta en los límites reales de InputDecorator, excluyendo ayuda/error y sin alturas fijas. Se conserva variante plana con contraste alto y se corrige compatibilidad con campos montados bajo Theme por defecto. No se añaden suma/recuperación simuladas ni se cambian API, sesión o permisos.

Pasan 139 pruebas Flutter y análisis limpio; APK debug QA compilado e instalado con hash comprobado. La nueva regresión cubre ancho completo, espacio de contenido, teclado y selección sin consultas extra. En Android se revisan campos vacíos sin envío, escala 200 % y cuatro destinos, restaurando 1,0. El teclado real de este emulador es flotante e informa inset cero: la barra permanece correctamente; el caso inferior con inset positivo se comprueba en widget. Se renuevan las 25 capturas, mosaico y evidencia de controles, con sesión QA cerrada y sin operaciones de negocio.

Guía 44 y STYLE reflejan la decisión vigente. Contrastes calculados: texto/botón 9,68:1 y borde/fondo 3,23:1, sin certificar accesibilidad global. María José recibe componentes, Home y prueba; Sally guía/evidencias; José Carlos conserva API. Paquetes actualizados y comprobados, sin commits, ramas o Railway. El emulador visible queda en el acceso actualizado. Pendientes anteriores de expediente, contratos y validación física se conservan.


## Continuidad · redirecciones y sesión móvil · 20 noviembre

Se incorporan seis regresiones con servidores HTTP efímeros exclusivamente en loopback: GET y POST ante 302, 307 y 308. Se comprueba una sola petición de origen, cero accesos al destino, código original como error y reutilización posterior del cliente. La implementación existente ya impide seguir redirecciones; no se cambia código de ejecución, autorización ni contratos. Sin escrituras de negocio, MySQL o Railway.

Pasan las 145 pruebas Flutter y el análisis está limpio. Logs flutter-redirecciones-20261120.log, flutter-redirecciones-suite-20261120.log y analyze-redirecciones-20261120.log. La guía 45 distingue el transporte IO probado del navegador y de Android físico. APK y capturas anteriores se conservan porque no cambió el binario; su validación visual sigue siendo la del bloque de controles con 139 pruebas.

María José: prueba de transporte; Sally: guía y evidencias; José Carlos: backend intacto. Se renuevan los módulos locales con control de integridad y privacidad. Sin commits, ramas ni publicaciones en este bloque. La demo web compartida en la tarea directa anterior es independiente, con datos ficticios y sin conexión a Railway; no se republica desde esta recurrencia. Continúan pendientes el expediente compacto, contratos de mapa/fotos de reportes/tienda/apadrinamiento y validación física/TalkBack/firma.


## Continuidad · recarga única de vistas privadas · 20 noviembre

Se corrige una fuente de consultas duplicadas: Mis mascotas y Expediente privado comparten una petición por instancia mientras está pendiente. Actualizar se deshabilita durante la carga y varias actualizaciones por gesto reutilizan esa operación. Tras éxito o error se permite volver a consultar. No se retiene una caché persistente; la actualización sigue ocultando el expediente anterior y las claves de sesión aíslan las cuentas. No cambian contratos ni permisos del backend.

Pasan nueve pruebas específicas, las 147 de la suite Flutter y el análisis está limpio. Las nuevas pruebas controlan carga inicial, repeticiones, error 503 y recuperación; se conservan las regresiones de cierre de sesión, cambio de cuenta y denegación 403. Todo usa MockClient y cuentas sintéticas, sin peticiones de negocio ni MySQL. Logs *expediente-recarga*-20261120.log y validacion-expediente-recarga-20261120.json.

Se compila y verifica la integridad del candidato Little-Paws-Net-Android-recarga-QA.apk por separado, con hash en la validación. No se instala ni se altera el emulador visible en este bloque. Little-Paws-Net-Android-QA.apk y las capturas anteriores conservan la referencia nativa del bloque de controles; no se atribuyen al nuevo binario. La demo web alojada tampoco se actualiza.

Se consultan contexto y captura Figma 128:599 para orientar el expediente compacto; su carnet/QR y fotografía de ejemplo no se incorporan a fichas reales. Este bloque corrige la interacción de recarga, no declara terminada esa adaptación visual. María José: pantalla y regresiones; Sally: guía 46 y evidencias; José Carlos: backend intacto. Módulos locales renovados y verificados; sin commits, ramas o publicaciones. Siguiente trabajo: comprobación nativa del candidato cuando no interrumpa al usuario, composición compacta y contratos reales pendientes, además de validación física/TalkBack/firma.


## Continuidad · rediseño integral Stitch · 20 noviembre

El nuevo encargo del usuario y sus dos HTML sustituyen las especificaciones móviles anteriores de controles y navegación. La guía 48 registra los 14 puntos, cambios funcionales, migraciones y límites. Cliente Flutter: 159 pruebas y análisis limpio. Backend: 56 pruebas de galería/comunidad/ayudas/directorio/contratos y 61 regresiones RBAC, aprobadas en MySQL aislado. APK QA recompilado con LPN_API_BASE_URL local e instalado en el emulador; capturas nuevas, sin atribuirle las anteriores.

La nueva galería conserva consentimiento/custodia y admite portada + cinco imágenes. Comunidad guarda publicaciones, comentarios, respuestas y reacciones; las ayudas guardan intereses y convocatorias con permisos de entidad, control de versión y aviso interno. Directorio solo expone organizaciones verificadas. Tienda/pedidos y aportes reutilizan APIs reales sin pago. La demo de navegador independiente simula estos datos en memoria, con fotos de stock claramente de ejemplo, sin conectar con Railway.

José Carlos: backend, migraciones y pruebas; María José: Flutter, pruebas y composición; Sally: guía, recursos, estudio de marca y evidencias. No se crean commits/ramas/tags/PR en el repositorio oficial. Los ZIP son material de revisión local; la trazabilidad académica definitiva requiere los commits y PR reales de cada integrante. No se migra Railway ni se presenta el piloto como producto comercial terminado.

Pendientes: datos y fotos autorizadas reales; fotos de productos y reportes/mapa cuando exista contrato; aceptación operativa de ayudas; medios oficiales de pago/conciliación si se habilitan cobros; moderación operativa; dispositivo físico/TalkBack; firma, distribución y despliegue revisado. No volver automáticamente a la barra rectangular/radio15,5: la referencia vigente es la guía48.


## Continuidad · barra contextual y acceso anterior · 20 noviembre

Se atiende la corrección directa del usuario: el círculo pasa de decoración interna a botón56 elevado sobre una concavidad real. Perro → Inicio; en Solicitudes, más → catálogo para seleccionar mascota, sin enviar un POST. Login/registro recuperan el tema anterior aislado y conservan toda la lógica actual de sesión y validación. Las pruebas de apariencia ahora comprueban la preferencia y persistencia; la cápsula oscura es sólida y ya no mantiene un desenfoque oculto sin efecto visual.

La suite Flutter pasa161 pruebas y el análisis está limpio. La demo pasa ocho pruebas específicas (transporte, reinicio, accesibilidad de cabecera, navegación, hueco, toque superior y acción contextual). Se compilan APK QA real y APK Demo visual independiente .visualdemo. Ambos permanecen instalados; la demo añade fotos locales ficticias con créditos, sin asignarlas a fichas reales o cambiar Railway. Se corrige también la cabecera del simulador para que sus controles sean accesibles en Android y respete el área de estado.

Evidencia nueva en output/barra-contextual-2026-11-20; no sustituye las capturas históricas de48. Reparto: Majo recibe Flutter, tema de acceso, navegación y pruebas; Sally guía49, estilo y capturas; José Carlos conserva backend sin cambios. Sin commits, ramas, tags o despliegues del repositorio oficial; la demo Sites se actualiza por su flujo independiente autorizado. El emulador queda en la demo visual con fotos; para procesos reales usar la app QA y la base aislada. Firma, dispositivo físico, TalkBack y datos consentidos de negocio siguen pendientes.


## Continuidad · aislamiento de ofrecimientos privados · 20 noviembre

Se reproduce y corrige un fallo de estado privado: Mis ofrecimientos conservaba información cargada al cerrar sesión y no recreaba la consulta al cambiar de cuenta. Ahora el contenedor escucha Session y crea/desmonta el listado por identidad, como las mascotas privadas. Sin sesión falla cerrado; actualizar un perfil sin cambiar su identidad no repite la consulta. No se cambian permisos ni contratos del servidor.

Tres regresiones fallan antes del cambio; las cuatro nuevas pasan después. Pasan nueve pruebas focalizadas, las165 de la suite y análisis limpio. Todo usa datos sintéticos/MockClient o las pruebas de transporte loopback existentes, sin MySQL o producción. Guía50 y logs *ayudas-sesion*20261120.log. Se compila un candidato QA con hash separado sin instalarlo; el emulador y las capturas visuales49 conservan su identidad anterior. No se modifica ni publica la demo Sites.

Majo: cliente y cuatro regresiones; Sally: guía/evidencias; José Carlos: backend intacto. Paquetes locales renovados y verificados, sin commits, ramas, publicaciones o cambios en Railway. Próxima ejecución: seguir revisión pequeña de límites de sesión y formularios pendientes; no rehacer el estilo ni atribuir al candidato los ensayos nativos anteriores. Firma, pruebas físicas/TalkBack, datos autorizados y operación de negocio siguen pendientes.


## Continuidad · formularios de pedido y aporte por sesión · 21 noviembre

Se reproducen seis fallos de conservación de borradores/confirmaciones de pedido y aporte al salir o cambiar de cuenta. Session.authorized protegía la respuesta, pero el estado del formulario seguía presente. Un gate de sesión compartido crea y desmonta ambos formularios por identidad; conserva el borrador al editar el perfil de la misma persona. Productos/fondos siguen públicos y el formulario editable exige entrar antes de redactar. No hay pagos ni cambios de contratos, permisos o backend.

Pasan las seis regresiones, nueve pruebas focalizadas y las171 de la suite Flutter, con análisis limpio. Todo usa MockClient y los ensayos de transporte loopback existentes; no se escribe en MySQL o producción. Logs *formularios-sesion*20261121.log y guía51. Candidato QA separado con API local, sin instalar ni modificar el emulador, las capturas anteriores o Sites. La referencia visual49 permanece vigente.

Majo: cliente y pruebas; Sally: documentación/evidencia; José Carlos: backend intacto. Paquetes separados y comprobados, sin commits, ramas o publicaciones. Siguiente bloque: revisión acotada de estado privado/composición de mensajes y controles de envío, sin rehacer la interfaz. Quedan firma, QA física/TalkBack y datos operativos consentidos como límites del piloto.


## Ajuste directo posterior · 21 noviembre

Guía52: bienvenida y corte del viewport sobre la navegación flotante.174 pruebas/análisis limpio; nuevos screenshots Android de .visualdemo y build QA independiente. Solo se publica la demo Sites v4; sin Git oficial o Railway. Acceso conserva Stitch, reemplazando únicamente esa parte de49. Las correcciones de privacidad50/51 siguen en el cliente real y no se atribuyen a la demo mock.


## Documento editable móvil · 21 noviembre

Guía54: archivo Figma nuevo con84 frames y variantes, componentes y recursos editables. Visualización de imágenes, fuentes y límites de texto verificados. Inventario local y enlace en la guía. No se cambian el panel web, la demo Sites, el backend ni Railway para esta exportación.


## Continuidad de sesión · composición de mensajes · 21 noviembre

Guía53: seis regresiones reproducidas y corregidas sobre borradores de mensajes públicos e intereses privados.180 pruebas/análisis limpio; candidato QA compilado pero no instalado. Se mantiene la demo visual y la referencia52. Pendiente revisar diálogo de descarte abierto durante un cambio de identidad. Sin backend/BD/producción.


## Continuidad · descarte y cambio de cuenta · 21 noviembre

Guía55: cuatro fallos reproducidos de diálogo huérfano al cerrar/cambiar sesión, para mensaje público e interés privado. El compositor conserva su DialogRoute y elimina solo esa ruta al desmontarse, después del frame. Seis pruebas nuevas; dos de conservación por misma identidad ya pasaban. Quince focalizadas,186 totales y análisis limpio. Candidato QA compilado, hash registrado y no instalado. Sin BD, backend, cambios de autorización, emulador, Figma, Sites o Railway. Majo código/pruebas; Sally guía/evidencia; José Carlos backend intacto. Siguiente: reproducción del mismo ciclo en edición de perfil.


## Petición directa · rediseño por referencias · 21 noviembre

Guía56: PDF6 páginas, siete ejemplos HTML y catorce apartados del encargo integral. Cambios en Flutter sobre composición de acceso/bienvenida, Inicio, catálogo, rescates, formularios, ayudas/directorio, comunidad, tienda y perfil.191 pruebas canónicas y197 del simulador. El reintento de gestión se corrige y se mantiene la ocultación por permiso; sugerencias sin envío automático. No se fabrican imágenes de productos, servicios/contactos privados o medios bancarios. Capturas y manifiesto de esta revisión en output/redisenio-referencias-2026-11-21. Demo Sites independiente; no Git oficial, datos reales, Railway o Figma manual. Las evidencias y estados definitivos de compilación/publicación están en validacion.json; no atribuir las pruebas mock a producción. Reparto: Majo cliente, Sally guía/evidencia visual, José Carlos contratos públicos pendientes.


## Auditoría de cumplimiento · 21 noviembre

La guía57 corrige la afirmación de cierre integral de56: Inicio integrado, capas de tarjetas, onda del acceso, formularios/perfil y contratos públicos permanecen parciales. Se reproducen y corrigen2 errores de voluntariado y1 de contraste.194 pruebas canónicas. Nomenclatura de3 estados vacíos corregida. No se publica ni se cambia la demo v5; no atribuir sus capturas a este parche local. La auditoría no certifica accesibilidad completa ni backend de producción.


## Continuación visual58 · 21 noviembre

Se resuelven onda y cambio de formulario, fondo integrado, materiales/entrada de tarjetas, alineación de metadatos, grupos de formularios y prioridad del perfil.197 pruebas canónicas/202 demo y análisis limpio; publicación independiente y capturas/hashes en output/cierre-visual-2026-11-21. No se certifican los contratos públicos pendientes ni la producción Railway. Sin commits oficiales.
