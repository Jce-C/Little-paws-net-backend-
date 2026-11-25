# Panel compacto y recorridos en contexto

Edición del 30 de octubre de 2026. Implementación en el panel Django real; el laboratorio estático queda como referencia histórica. Sustituye las indicaciones anteriores de formularios en páginas independientes y de alternar entre checks y switches.

## Criterios aplicados

Referencia Duna suministrada por el usuario y fundamentos TypeUI locales: superficies cálidas, separación por jerarquía y bordes sutiles, tipografía contenida y formularios agrupados. Se conservan logo, ilustraciones, Inter, Leckerli One y paleta Little Paws Net. La escala de marketing de Duna (72-80 px y secciones de 80-120 px) no se traslada al panel: el usuario pidió expresamente reducir tamaños y huecos. El panel usa títulos de 24-28 px, superficies de 16-20 px de padding y agrupación de 8/12/16/24 px; controles visuales compactos con foco visible y texto ampliable.

## Cambios por grupo

| Requisito | Implementación |
| --- | --- |
| Landing y bienvenida | Información integrada en el recorrido; recuadro central, fondo #F8E4C5, nubes originales y texto existente, sin inventar contenido de una imagen no adjuntada |
| Login | Fondo más visible, tarjeta #F6D9B1, envío directo; intensidad, velo, visibilidad y encuadre configurables con validación |
| Dashboard | Carrusel horizontal nativo con flechas, indicadores de posición y adaptación móvil; mismos indicadores autorizados |
| Accesos actuales | Barras y conteos derivados de permisos efectivos; seis áreas principales y detalle expandible con todas las capacidades y sus orígenes |
| Navegación | X pequeña, cabecera con contraseña/configuración/vista/salir; configuración fuera del menú lateral |
| Formularios | Modales sobre las vistas originales, errores en contexto, acciones visibles, columnas adaptables, campos requeridos y protección de borradores |
| Usuarios | Alta y edición en modal, búsqueda progresiva por nombre/correo/ID, acciones horizontales o menú compacto |
| Roles y recursos | Catálogo y asignación por persona separados; creación/edición de metadatos en modal; búsqueda de personas limitada y sin catálogo inicial completo |
| Permisos | Selector de rol arriba y matriz de ancho completo, solo switches; consulta/creación/edición/otras acciones reales |
| Excepciones | Tabla de recurso/capacidad/decisión con filtro; Heredar/Permitir/Denegar se conservan porque un switch binario no representa los tres estados |
| Negocio | Formularios puntuales y detalles en modales; consultas básicas de entidades y mascotas sin conceder acceso clínico ajeno |
| Accesibilidad | Menú compacto y preferencias inmediatas; se retiró el selector de color. El color persistente existente se extiende a indicadores, tablas y elementos activos |
| Auditoría | Tabla, filtros por persona/tipo/fechas y búsqueda; detalle modal anterior/nuevo y categorías de eventos existentes; no se modifica el historial |

## Funcionamiento conservado

No se sustituyó Django, la sesión, CSRF, los servicios de negocio ni el motor RBAC. Los formularios conservan sus rutas, validaciones y transacciones. Sin JavaScript se mantienen las vistas SSR de respaldo. Los modales no inventan operaciones ni cambian reglas de aprobación, custodia o asignación.

Los cambios de contraseña utilizan PasswordChangeForm y update_session_auth_hash. Las peticiones AJAX llevan el token CSRF del formulario y se realizan al mismo origen. Se evitan solicitudes de listado redundantes cuando la respuesta del guardado ya contiene el listado actualizado.

La sincronización sigue comprobando permisos en el servidor. Se vuelve a verificar el estado después de guardar. Las concesiones remotas no destruyen un borrador abierto; las revocaciones conservan prioridad para retirar contenido protegido.

El login mantiene una petición inicial del documento: sus recursos permanecen integrados. El fondo configurado se aplica en la siguiente carga; no se añade una conexión automática a la pantalla de acceso.

## Correcciones lógicas

- Auditoría por fechas y el contador de actividad de hoy usan límites temporales explícitos, evitando depender de tablas de zonas horarias de MySQL y permitiendo usar el índice de fecha.
- La consulta básica de una mascota no implica permiso sobre su expediente. Los botones de autorización dependen de custodia/propiedad o capacidad vigente, además de las validaciones del servicio.
- La consulta de una organización respeta el permiso global o el contexto de membresía autorizado.
- Las matrices conservan la protección contra sobrescribir cambios concurrentes.
- Cancelar o cerrar un formulario modificado solicita confirmación dentro del propio modal. Los errores de validación mantienen el formulario abierto.

## Organización de archivos

- static/seguridad/compacto.css: escala, contenedores, modales, tablas y responsividad.
- static/seguridad/interacciones.js: mejora progresiva de modales, guardado, búsquedas, menús de acciones y carrusel.
- static/seguridad/administracion.js: switches definitivos y navegación lateral.
- static/seguridad/sincronizacion.js: integración con guardados y borradores en modal.
- static/acceso/bienvenida.css: integración visual de la parte inferior de la landing.
- templates/seguridad/web/: plantillas de las pantallas y fragmentos.
- web/dashboard.py: indicadores existentes, presentación de accesos, configuración y filtros de auditoría.
- web/administracion.py: selección de personas y metadatos; conserva el guardado y sus permisos.
- web/negocio.py: formularios existentes y detalles autorizados en contexto.
- migrations/0013_personalizacion_acceso.py: valores configurables del fondo, sin cambiar registros de negocio.
- tests_ui_compacta.py y ampliaciones de tests_negocio_web.py: verificaciones de configuración, filtros, matrices y alcance de datos.

## Evidencia local

165 pruebas Django aprobadas en MySQL aislado. Recorridos de navegador: alta/edición de usuario, búsqueda progresiva, protección de borrador, cambio real de contraseña, creación de recurso y organización, roles, configuración del fondo y detalle de auditoría. Prueba de login con una petición inicial. Revisión de cinco vistas en claro/oscuro y móvil con axe; pruebas de 2K, 1366x768 y 390x844 con texto ampliado. Las pruebas usan exclusivamente datos sintéticos locales y no crean cuentas ni registros de prueba en producción.

La revisión automática no certifica por sí sola WCAG completo ni capacidad de carga. Se conserva el contenido actual de bienvenida porque el pedido menciona una imagen de referencia con texto que no venía adjunta. Los gráficos representan capacidades disponibles, no tendencias de actividad inventadas.

## Publicación y comprobación final

Desplegado en el servicio del panel de Railway: `5ff461fa-de54-436f-997a-ee43dfcbd134`, estado SUCCESS. La base `little_paws_panel_v2` recibió únicamente la migración adicional 0013 después de generar y verificar un respaldo privado. No se modificó el servicio anterior ni se crearon commits o ramas en el repositorio oficial.

La compilación detectó una referencia residual a Manrope.ttf en panel.css; se sustituyó por la familia Inter ya utilizada. La recopilación con manifiesto de archivos estáticos finalizó correctamente.

La verificación final aprobó las 165 pruebas Django, los recorridos reales de guardado en una base local aislada, 15 combinaciones de resolución y vistas con texto ampliado, y la revisión axe de cinco vistas en claro/oscuro más los modales de usuario y preferencias en móvil. Una actualización remota de datos conserva el borrador de contraseña abierto. La concesión y revocación entre dos sesiones funcionaron sin iniciar sesión nuevamente; la revocación de la prueba local se reflejó en 855 ms, una medición puntual, no una garantía de latencia.

En producción se verificaron nueve rutas autenticadas, el estado y la conexión SSE: respuestas 200 y ningún error JavaScript observado. El login realizó una sola petición inicial, con una transferencia de 86.526 bytes en esa medición. Las verificaciones de producción fueron de lectura; las altas de prueba, cambios de contraseña y asignaciones se efectuaron exclusivamente en la base aislada.

Quedan fuera de esta revisión una prueba de carga concurrente, una auditoría manual completa con lectores de pantalla y la traducción integral de los nuevos textos al inglés. No se afirma certificación WCAG ni un tiempo de respuesta garantizado para cualquier red o volumen de usuarios.
