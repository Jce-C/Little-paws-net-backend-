# Plan verificable de nuevas correcciones de la app

Fuente: C:/Users/DELLPHOTO/Documents/Correciones de Little paws app (1).pdf, 12 páginas revisadas en texto y renderizado. Fundamentos: output/referencias-videos-2026-11-03/guia-aplicacion-little-paws.md del workspace principal. Los principios de los vídeos se aplican a jerarquía, proximidad, navegación, formularios, estados y movimiento; no sustituyen la paleta posterior solicitada por el propietario.

Estado vigente: 49/57 (86,0 %), según la guía 86. V02 completado tras los tres bloques anteriores: etiquetas persistentes y acceso adaptado con teclado. Permanecen abiertos S04/S05/S08/S12 y Q01/Q02/Q03/Q10. Sin commits ni publicación.

## Decisiones pendientes

- D01 RESUELTA por el propietario: la foto del perro y el gato de espaldas al atardecer va en Adopción; la foto de perros del refugio con una persona acariciando va en Rescate. Usar las imágenes exactas adjuntas a su aclaración. El login conserva su recurso actual y se ajusta de tamaño según la página 8; no usar el atardecer en login. Archivos fuente: C:/Users/DELLPH~1/AppData/Local/Temp/codex-clipboard-c49f535b-6a7f-496b-b677-9e584df31675.png y C:/Users/DELLPH~1/AppData/Local/Temp/codex-clipboard-9dfbfc18-2166-49e6-9861-c01e9b6bb571.png. Esta aclaración no acredita licencia comercial de las fotografías.
- D02: momento y necesidad de adjuntos de identidad, recibo y fotografías de vivienda. Propuesta: evaluación inicial mínima y solicitud posterior justificada de documentos privados. Confirmar alcance; disponibilidad de adjuntos no implica que todos deban ser obligatorios.
- Evaluar necesidad y tratamiento de información de salud/terceros/menores del hogar antes de habilitar esos campos. No asumir que aceptar términos autoriza recopilar datos ajenos. No pedir nombres de menores, diagnósticos detallados, historias clínicas ni ingresos exactos como consecuencia implícita de este formulario.

## A. Base visual común y recursos (páginas 1-12)

- [x] V01 Inventariar pantallas/rutas reales y componentes compartidos afectados; contrastar capturas del PDF con versión local actual y separar demo de servidor real.
- [x] V02 Definir escala de títulos, cuerpo, metadatos, estados y acciones; etiquetas persistentes, párrafos cortos y alineación predecible (vídeos 2, 6, 9, 10, 17).
- [x] V03 Unificar radios, sombras, espaciado, iconos, formas orgánicas y texturas sutiles, conservando paleta vigente y jerarquía de botones (vídeos 12, 16).
- [x] V04 Definir uso estable de pasteles amarillo, verde, rosa, lila y azul; no colores aleatorios en cada reconstrucción ni significado de estado basado solo en color.
- [x] V05 Extraer las fotografías exactas del PDF; guardar referencia de origen/licencia pendiente, optimizar a WebP y comparar bytes y fidelidad. No sustituir por imágenes parecidas ni inventar licencia comercial.
- [x] V06 Adaptar imágenes a tamaños de pantalla sin perder sujetos; dimensiones reservadas, semántica y sin decoraciones que bloqueen campos o acciones.
- [x] V07 Mantener vidrio/transparencia de forma contenida, con fallback visual y contraste. Evitar blur o texturas costosas por cada tarjeta.
- [x] V08 Aplicar movimiento breve y fluido a cambios de paso, estados y controles, sin retardos artificiales; respetar reducción de movimiento (vídeos 4, 5, 11).

## B. Comunidad (páginas 1-2 y 11)

- [x] C01 Una familia de tarjetas con fondos pastel alternados establemente; misma estructura, tipografía y espaciado, sin rediseño diferente por publicación.
- [x] C02 Jerarquizar autor/avatar, fecha, mensaje y acciones Me gusta/Comentarios. Mantener legibilidad para mensajes cortos y largos.
- [x] C03 Conservar creación, lectura, comentarios, reacciones, permisos, paginación y estados reales; no duplicar operaciones ni contadores ficticios.

## C. Login y catálogo de adopción (páginas 3-4 y 8)

- [x] L01 Resolver D01 antes de cambiar la fotografía: atardecer en Adopción, refugio en Rescate; aclaración del propietario registrada. Esto no marca la implementación visual como terminada.
- [x] L02 Ampliar la imagen del login hasta cerca del primer campo sin superponerlo; preservar marca, colores y distribución general, animales/paisaje y acceso al teclado.
- [x] L03 Mantener acceso directo, verificación y ausencia de peticiones adicionales en reposo; probar campos visibles con teclado, escalado de texto y pantalla pequeña (vídeo 7).
- [x] A01 Cabecera destacada y redondeada de Adopción integrada como Inicio; ajustar a D01 y conservar listados reales.
- [x] A02 Filtros Todos/Gatos/Perros con iconos, etiquetas breves, selección inequívoca y objetivo táctil adecuado; mantener opciones de otras especies existentes y no esconder animales válidos.
- [x] A03 Confirmar que filtros modifican la consulta real, conservan paginación/errores/vacío y solo muestran animales disponibles para adopción según backend.

## D. Reportes y rescate (páginas 4-7 y 11)

- [x] R01 Detalle: organizar tipo de caso, estado, ubicación, descripción y fotos en grupos; acento pastel, formas suaves y fondo coherente sin cajas anidadas innecesarias.
- [x] R02 Estados con texto e icono/distintivo; conservar estados y acciones que realmente admite el servidor, responsable/próxima acción si existen y permisos de consulta.
- [x] R03 Animales que necesitan ayuda: usar foto exacta de los dos perros del refugio, contenedor amplio redondeado, título Ayúdanos a rescatar y contraste mediante capa suave.
- [x] R04 Integrar buscador legible y translúcido con la cabecera; conservar su lógica real, controles accesibles y consultas eficientes.
- [x] R05 Conservar Reportar, Mis reportes, Con clave, Historial y Actualizar; ordenarlos con iconos y etiquetas cortas, sin opciones repetidas ni eliminación de rutas.
- [x] R06 Editar reporte: bloques Información del reporte / Datos que deseas actualizar / Confirmación de cambios, sin perder campos ni valores existentes.
- [x] R07 Acciones claras Guardar cambios y Cancelar/Regresar, ayuda breve y acciones accesibles sin recorrer un scroll excesivo. Advertencia de borrador cuando corresponda.
- [x] R08 Probar edición real, validaciones, control de acceso por clave/titular, errores, respuesta perdida, cancelación y prevención de duplicados.
- [x] R09 Nuevo reporte: flujo progresivo por temas, opciones rápidas y campos condicionales, sin información repetida; pasos solo si reducen esfuerzo real.
- [x] R10 Mantener respuestas y foto al avanzar/regresar, validar oportunamente, identificar el tipo de situación y enviar una sola operación real con su resultado.

## E. Solicitud de adopción completa (páginas 9-10)

- [x] S01 Revisar modelo, API, validaciones, permisos y solicitud existente antes de diseñar persistencia; mantener compatibilidad/migraciones y vínculo usuario-animal-organización.
- [x] S02 Cinco etapas con título, explicación breve y progreso basado en etapas reales. Continuar/Regresar/Enviar solicitud y salida con borrador protegido; no publicar solicitud en cada paso.
- [x] S03 Etapa 1: nombres y apellidos, documento, teléfono, correo y dirección. Reutilizar datos del usuario con confirmación y definir obligatoriedad/finalidad de cada campo.
- [ ] S04 Adjuntos de identidad y recibo cuando sean necesarios, con finalidad visible y momento según D02. No convertirlos por defecto en requisitos universales.
- [ ] S05 Etapa 2: casa/apartamento, propia/arrendada, autorización del propietario condicional, seguridad de ventanas/balcones, fotos opcionales justificadas, número de convivientes, presencia/edades de niños, acuerdo del hogar y alergias/asma. Resolver minimización y protección de terceros antes de activar campos sensibles.
- [x] S06 Etapa 3: disponibilidad de tiempo, capacidad para cubrir cuidados sin pedir cifras económicas innecesarias, compromiso con cuidados especiales y aceptación de seguimiento/visitas bajo condiciones explícitas de la organización.
- [x] S07 Etapa 4: mascotas actuales; cantidad, especies, edades y esterilización condicionales; experiencia previa y qué ocurrió; motivo de adopción obligatorio.
- [ ] S08 Etapa 5: resumen legible, regresar/corregir, confirmación de exactitud, aceptación de condiciones de adopción y tratamiento informado correspondiente, casillas sin preselección y versiones/fecha registradas.
- [x] S09 Usar preguntas cerradas y cortas donde ayuden, detalles solo al seleccionar respuestas pertinentes; definir qué se borra/ignora al cambiar una respuesta para no enviar campos ocultos obsoletos.
- [x] S10 Conservar respuestas entre etapas; errores asociados al campo, envío único, fallos de red, reintento seguro y cancelación sin pérdida silenciosa (vídeos 5, 10, 13, 14).
- [x] S11 Backend: validar también en servidor, límites de texto/archivos/cantidad y respuestas coherentes; no confiar solo en widgets o motivo libre concatenado.
- [ ] S12 Documentos privados: comprobar formato/tamaño, almacenamiento restringido, descarga autorizada por objeto y finalidad, sin URL pública, caché pública ni datos personales en logs. Definir retención y eliminación; fotografías de vivienda no van a galería pública.
- [x] S13 Panel y admin Django: personal autorizado puede consultar la evaluación asociada a la solicitud y gestionar su estado real; auditoría entendible y acceso denegado a otras organizaciones/usuarios.
- [x] S14 Pruebas de autorización, campos condicionales, datos faltantes, migración, envío/reintento y conservación de respuestas; recorrido real app → API → panel/admin → estado visible en Mis solicitudes.

## F. Otras pantallas (páginas 11-12)

- [x] O01 Notificaciones: tarjetas con icono según tipo, texto jerarquizado, nuevo/leído real, acciones y enlace al destino autorizado; no marcar como leído solo cambiando color local.
- [x] O02 Mis solicitudes: animal, fecha y estado real identificables; distintivos sin inventar estados, detalle y actualización coherentes con el backend.
- [x] O03 Mi cuenta: bloques de información, iconos y accesos claros a edición/configuración; conservar seguridad y cambio de sesión.
- [x] O04 Agregar mascota: campos agrupados, foto, controles y errores claros; mantener catálogos, validaciones y registro real.
- [x] O05 Ayudas y ofrecimientos: diferenciar modalidades con iconos/colores y jerarquía, preservar compromisos y operaciones reales.
- [x] O06 Recorrer todas las rutas restantes (Inicio, directorio, tienda/pedidos, historial, perfiles, documentos y demás existentes) para detectar estilos discordantes, sin inventar funciones fuera del alcance.

## G. Integración y cierre (condiciones transversales)

- [ ] Q01 Revisar todas las pantallas: pequeño/grande, orientación, teclado, áreas seguras, texto aumentado y oscuro/claro; sin cortes, doble scroll ni acciones finales inaccesibles.
- [ ] Q02 Validar contraste, lector de pantalla, etiquetas, teclado/foco en versión web y objetivos táctiles; no usar solo colores para transmitir estados.
- [ ] Q03 Medir peticiones, bytes, consultas SQL, tiempos y memoria en recorridos completos. Evitar cargas en build, recomprimir al leer, búsquedas duplicadas y servicios de pago para ocultar ineficiencias.
- [x] Q04 Regresión RBAC, revocación y sincronización entre sesiones, aislamiento entre usuarios/organizaciones, auditoría, idempotencia y permisos del admin Django.
- [x] Q05 Identificar claramente demo/datos ficticios y verificar integración con MySQL local real. No validar persistencia solo con mocks.
- [x] Q06 Actualizar documentación por cambio: ID → fuente/página → ruta → componente/modelo/API → permiso → prueba → evidencia → resultado/pendiente. No marcar terminado sin evidencia de integración.
- [x] Q07 Capturas/mosaico de todas las pantallas afectadas y verificación visual contra PDF y guía de 17 vídeos; revisión de estados vacío, cargando, error, sin permiso y éxito.
- [x] Q08 Ejecutar pruebas apropiadas y análisis del cliente; compilar Android/demo web cuando cambien; distinguir pruebas automatizadas de aceptación física pendiente.
- [x] Q09 Actualizar paquetes separados de los tres integrantes y notas de integración, sin commits ni publicación automática.
- [ ] Q10 Conservar puertas de publicación de las guías 72-74: seguridad/security-audit (repositorio por identificar), licencias, privacidad, retención/derechos, respaldo/restauración, firma Android, dispositivo real y presupuesto final VPS. No declararlas resueltas por este rediseño.

## Orden de trabajo

1. Resolver D01/D02 y levantar inventario local/modelo de solicitud.
2. Cerrar contrato de datos, privacidad, validaciones y trazabilidad de adopción y reportes; no dejar interfaz sin persistencia.
3. Implementar componentes comunes y recursos exactos optimizados.
4. Aplicar Comunidad, login/Adopción y reportes de uno en uno, con pruebas por flujo.
5. Completar solicitud en cinco pasos y su lectura/gestión en backend/panel/admin.
6. Completar otras pantallas y regresión integral, actualizar evidencias y paquetes.

Cada avance debe informar identificadores cerrados, evidencia, pendientes y porcentaje calculado sobre el inventario vigente. Si aparecen dependencias nuevas, se añaden explícitamente; no aumentar el porcentaje por código no probado ni reutilizar porcentajes de tablas anteriores.


## Avance del primer bloque local

Implementación: fotos exactas WebP (Adopción 34020 bytes; Rescate 21482 bytes), iconos vectoriales nativos de gato/perro y selección conservando otras especies, altura de cabecera adaptativa para filtros accesibles, búsqueda integrada, Comunidad con cinco tonos estables por ID, foto actual del login ampliada, edición de reporte en tres bloques con Cancelar y descarte confirmado. Detalle de reporte y notificaciones recibieron ajustes iniciales; sus unidades completas siguen pendientes.

Evidencias: output/correcciones-app-2026-11-24 del workspace principal. Las capturas son renderizados Flutter con contenido de prueba, no capturas de un dispositivo físico ni prueba de persistencia en MySQL. Las de Adopción/Rescate muestran sus cabeceras; no se presentan como recorrido integral del catálogo. El registro de fotos conserva origen y licencia comercial pendiente.

Se conserva la API existente sin migraciones nuevas. Las pruebas de filtros y paginación, reacciones/comentarios, edición sin cuenta y reintentos usan servidor simulado. No se ha cerrado S01-S14: la solicitud completa requiere cambios del modelo/API, formulario y gestión administrativa con pruebas reales. No se han creado mecanismos de documentos privados aún; D02 sigue pendiente de respuesta.

Las tareas marcadas reflejan únicamente el alcance descrito y comprobado en este bloque. Las comprobaciones globales Q01-Q10 siguen abiertas: este primer bloque no certifica accesibilidad total, despliegue, privacidad ni producto terminado. La reducción WebP es de las dos imágenes nuevas; no equivale al ahorro de toda la aplicación.

Resultado de pruebas del bloque: 260 pruebas Flutter aprobadas; cuatro capturas visuales opcionales se ejecutaron por separado, análisis sin observaciones y APK debug compilado. 14/57 unidades de esta lista están marcadas (24,6%, conteo simple, no porcentaje de toda la app ni estimación de esfuerzo). No hubo nuevas pruebas de integración con backend real.


## Segundo bloque: evaluación inicial de adopción

Guía detallada: `76-evaluacion-adopcion-por-etapas.md`. Se cierran S01, S02, S03, S06, S07, S09, S10, S11, S13 y S14 para el alcance descrito allí. El recorrido comprobado incluye cliente Flutter real, HTTP local, Django y MySQL aislado; consulta del panel y del admin, resolución por gestor asignado y lectura posterior del titular. La nueva migración agrega evaluación cifrada sin alterar solicitudes anteriores. El endpoint anterior permanece compatible y aún no exige la evaluación; su deprecación queda pendiente.

S04 y S12 siguen pendientes por adjuntos privados/D02; S05 por los campos sensibles y de terceros no habilitados; S08 por condiciones de adopción y revisión jurídica. Hay resumen y confirmaciones sin preselección, pero eso no sustituye dichas condiciones. Q01-Q10 continúan abiertas como aceptación integral del producto.

Validación: 77 pruebas backend aprobadas; 15 focales repetidas tras optimizar la consulta del admin. Cliente canónico: 268 aprobadas y 5 opcionales omitidas; 28 focales finales aprobadas, análisis limpio y APK debug compilado. Demo Android local: 342 aprobadas y 4 visuales opcionales omitidas; análisis limpio. La demo usa datos ficticios en memoria y no acredita persistencia real. Capturas de las cinco etapas y mosaico en la carpeta de evidencias; son renderizados Flutter, no capturas de un dispositivo.

24/57 unidades cerradas (42,1 %, conteo simple de esta lista, no avance de toda la aplicación ni esfuerzo ponderado). Sin commits, publicación, migraciones productivas ni servicios de pago.


Demo web local sincronizada en `sites/little-paws-mobile-demo`: 2 pruebas focales aprobadas, análisis sin observaciones y `flutter build web --release --no-pub --target lib/demo_main.dart` correcto. Salida en `build/web`; no publicada ni copiada a `dist` de alojamiento. El compilador informa una referencia a la familia CupertinoIcons no empaquetada; la compilación finaliza y esta advertencia queda pendiente de revisar en la auditoría global de iconos. No se agrega una dependencia solo para silenciarla.


## Refinamiento visual y nuevo orden operativo

La guía 77 registra la petición posterior de formularios cálidos/compactos, los componentes compartidos modificados y los seis bloques de continuación. Se preserva el contrato de la guía 76. Este refinamiento no aumenta el conteo 24/57 y no cierra la auditoría de todas las pantallas. Siguiente bloque: detalle y edición de reportes R01/R02/R08; después creación R09/R10 y pantallas restantes.


## Tercer bloque: formularios comunes, detalle y edición de reportes

La guía 78 documenta la extensión del sistema visual a formularios, selección de vivienda compacta y el cierre de R01/R02/R08. Se preservan R09/R10 para la próxima ejecución: creación completa de reportes. Hay pruebas del cliente, backend MySQL y recorrido HTTP real de edición con clave, con evidencia separada de las capturas ficticias.

Estado actualizado: **27/57 unidades (47,4 %)**, conteo simple de esta lista. No se certifica el producto completo, la aceptación física ni la auditoría visual de todas las rutas por cerrar estos tres puntos. No hay commits, cambios productivos ni servicios de pago.


## Cuarto bloque: creación de reportes

La guía 79 registra R09/R10: tres etapas, borrador/foto conservados, confirmación explícita de publicación, resumen completo, salida desde cualquier etapa, sesión vinculada, validación backend y recorrido HTTP real con WebP. Estado actualizado: **29/57 (50,9 %)** de esta lista. No es un porcentaje del producto entero ni una autorización para publicar. Próximo bloque: O01/O02, notificaciones y Mis solicitudes; después O03-O06 y Q01-Q10.


## Quinto bloque: notificaciones y Mis solicitudes

O01/O02 se cierran con la guía 80: destino explícito/autorizado de avisos de adopción, lectura persistida con fecha del servidor, paginación, separación por sesión y actualización del detalle/listado. Migración core.0018 preparada y aplicada únicamente en MySQL QA aislado. **31/57 (54,4 %)**, conteo de esta lista, no del producto completo. Siguiente: O03/O04, Mi cuenta y registro de mascota; continúan O05/O06 y Q01-Q10.


## Sexto bloque: Mi cuenta y mascotas personales

O03/O04 se cierran con la guía 81: actualización de perfil, vista previa limitada con destino correcto, formulario agrupado con cancelación/descarte y foto privada, validación servidor, protección por sesión/titular y reintento sin duplicados. Comprobado mediante Flutter → HTTP local → Django → MySQL aislado. **33/57 (57,9 %)** de esta lista. Siguen O05/O06 y Q01-Q10; no se certifica aún el producto completo ni la publicación. Sin commits ni cambios productivos.


## Séptimo bloque: ayudas y ofrecimientos

O05 cerrado con la guía 82: modalidades diferenciadas, intereses con actividad/fecha, formulario de organización agrupado, cancelación persistente, recuperación de conflictos y separación por sesión. Comprobado mediante Flutter → HTTP local → Django → MySQL aislado, sin pagos reales. **34/57 (59,6 %)** de esta lista. Continúan O06 y Q01-Q10; este bloque no cierra la aceptación global ni las puertas de publicación. Sin commits ni cambios productivos.


## Tres bloques agrupados — cierre del 25 de noviembre

Guías 83-85: inventario y coherencia de rutas (41/57), comunidad/integración/RBAC real con dos sesiones SSE (44/57), atlas, pruebas y paquetes (48/57). Resultado **84,2 %** de esta lista. V02 se mantiene abierto porque el acceso aún utiliza pistas internas en lugar de etiquetas visuales persistentes; no se redondea ni se marca para alcanzar una cifra. Los otros ocho pendientes están enumerados en la guía 85. No hay commits, producción ni servicios de pago.


## Continuación programada — etiquetas del acceso

La guía 86 cierra V02 con etiquetas persistentes, rótulos adaptados al 200 %, semántica nativa y botón por encima del teclado simulado. 308 pruebas del cliente, focales en las demos, análisis y compilaciones correctos. **49/57 (86,0 %)**. Continúan los ocho puntos de documentos/datos sensibles y aceptación global; no se certifica publicación.

La guía 87 avanza Q01/Q02: diez pies de formulario adaptados al teclado, caso horizontal extremo corregido, nueve pruebas nuevas de adaptación/foco/borrador. Suite final: 317 aprobadas, nueve optativas omitidas; 28 focales por demo, análisis limpio y compilaciones Android/web correctas. Se conserva **49/57 (86,0 %)** porque TalkBack, dispositivo físico y aceptación global siguen pendientes.

La guía 88 amplía la matriz a los ocho destinos restantes, corrige el pie ausente tras cargar ayudas y mejora dos textos con contraste insuficiente. 34 pruebas nuevas; 351 aprobadas y nueve optativas omitidas en cliente, 55 focales por demo. Continúa **49/57 (86,0 %)**: esta verificación automatizada no sustituye la aceptación integral.

La guía 89 corrige anuncios duplicados, dirige al primer error y mantiene los campos obligatorios en la validación después de desplazarse. Ocho pruebas nuevas; acceso, perfil, adopciones, ayudas y reportes comparten recuperación de foco. Se conserva **49/57 (86,0 %)** hasta completar aceptación nativa/asistiva y las puertas de publicación.

La guía 90 comprueba recorridos concretos en Android 15: login, foco, IME, rotación, registro incompleto de mascota, corrección de errores, texto ampliado y descarte conservando borrador. Corrige el pie horizontal del acceso y el paso entre campos; 363 pruebas aprobadas y nueve optativas omitidas, 29 focales por demo. Continúa **49/57 (86,0 %)**, sin certificar TalkBack ni todos los dispositivos.

La guía 91 avanza Q03: fixture de 1.000 mascotas/500 productos, 312 peticiones de negocio con 104 escrituras verificadas en MySQL, p95 local de 129,77 ms con ocho clientes y siete pruebas de herramientas aprobadas. Hay SQL, memoria de servidor y estimador de tráfico; faltan perfil móvil representativo, transferencia real y presupuesto del alojamiento. Se conserva **49/57 (86,0 %)**; no se presenta el ensayo local como capacidad comercial.
