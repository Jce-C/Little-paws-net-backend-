# Registro de cambios

## Sin publicar

- Presentación aislada: carga transaccional de datos ficticios con protección contra sobrescritura, cuentas por función, catálogos completos y verificación HTTP reversible. Se prepara la integración de los tres responsables contra el `main` remoto real; sin publicación ni commits automáticos.

- Base local consolidada (guía 92): tienda paginada con búsqueda/categorías y compatibilidad del listado anterior; carga adicional explícita, recuperación de errores y descarte de respuestas antiguas. La app requiere configurar su backend y no usa Railway por omisión. CI Django amplía la ejecución a todas las aplicaciones y herramientas. Sin cambios de esquema en este bloque, commits, tag o despliegue.

- Guía72: cierre de siete hallazgos, recibos SQL de reintento por actor, historial privado de compromisos, semántica de lectura web y archivos multipart con extensión. Mis reportes revalida permiso y evita caché. Publicación Android requiere firma privada; core.0017 solo migrada en pruebas locales. Railway no modificado.

- Guía 71: paleta móvil renovada, Inicio continuo y foto WebP; reportes con fotos persistentes, mascotas personales privadas, historial paginado y reserva de adopción, apadrinamiento y datos bancarios por destinatario. Migraciones animals.0010/rescue.0004 solo en QA local. Recordarme seguro en Android; persistencia web de sesión pendiente de cookies protegidas.

- Guía64: logos públicos por organización (WebP512px/96KB, autorización/retirada, auditoría y permisos configurables), directorio compacto con ficha completa y copia de contactos autorizados. Actualización explícita sin polling. Migración core.0015 solo en pruebas; conserva compatibilidad con organizaciones sin logo.

- Guía63: jerarquía de tarjetas según vídeos2/6/9/12/17; actividades y canales oficiales por organización con borrador/publicación/retirada, permiso por ámbito y versión409. Interés de actividad conserva snapshot. Acceso público explícito a canales, sin pagos ni consulta remota al copiar. Migraciones core.0013/0014 solo en prueba.

- Guía62: presentación pública por mascota (descripción, cuidados y espacio), autorizada por fundación y separada del expediente. Publicar/borrador/retirar desde panel/API; ficha, tarjeta y solicitud compatibles. Etiqueta de atributos y altura adaptativa. Migración animals.0009 solo en pruebas;212 pruebas móviles y76 backend. Cierre técnico9/14,64,3%.

- Guía61: materiales de formularios/diálogos/switches unificados, perro completo con hocico orgánico aplicado, bienvenida descriptiva e ilustración de Inicio en fondo independiente del desplazamiento. Modo sólido respeta sombras/capas.208 pruebas del cliente; cierre técnico8/14 puntos,57,1%, con validación integral pendiente.

- Guía60: flechas centradas dentro del círculo de las tarjetas, con regresión en cuatro anchuras. Perfil público editorial por organización con consentimiento, retirada, RBAC configurable, auditoría legible y cliente compatible. Migración core.0012 solo en pruebas. La corrección de flechas está publicada por separado en demo v7; backend permanece local.

- Guía59: fotos comerciales autorizadas desde panel/API; copia WebP hasta512KB/1280px, retirada, RBAC por tienda y trazabilidad. Tarjeta/ficha móvil admiten imagen pública validada y marcador compatible. Migración commerce.0003 solo en pruebas;54 pruebas backend y199 Flutter, análisis limpio.

- Guía58: onda a ancho completo en acceso, Inicio integrado, tarjetas por capas con movimiento reducido, formularios agrupados y mascotas antes de roles. Validación progresiva después del primer intento y vuelta al encabezado al pasar a registro.197 pruebas canónicas y203 del simulador.


- Auditoría57: voluntariado filtra aceptación explícita, vacíos de rescates usan nomenclatura clara y se ajusta el contraste del texto secundario sobre rosa. Dos regresiones funcionales y una de contraste;194 pruebas canónicas. Correcciones locales, aún sin actualizar la demo v5.


- Rediseño móvil según PDF de seis páginas y siete ejemplos de composición: acceso orgánico, bienvenida compacta, Inicio, adopción, rescates, ayudas, directorio, comunidad, tienda y perfil. Controles compactos, requisitos por temas y sugerencias que no envían datos (guía56).
- Corregidos desbordes con texto ampliado, avisos fuera de vista del compositor y excepción al reintentar gestión de ayudas; conserva separación por permisos y protección de borradores por identidad.


- El compositor retira su diálogo de descarte al salir o cambiar de cuenta; una confirmación antigua ya no bloquea la sesión nueva. Guía55 y186 pruebas del cliente.

- Bienvenida compacta con entrada escalonada y navegación flotante sin corte rectangular del contenido; etiquetas dentro de la cápsula y espacio final para todas las acciones. Acceso Stitch conservado. Guía52,174 pruebas y demo visual independiente v4.

- Mis mascotas y expediente agrupan actualizaciones simultáneas en una consulta pendiente, deshabilitan actualizar durante la carga y permiten recuperar errores explícitamente (guía 46).

- Seis regresiones del transporte HTTP real verifican que las respuestas 302/307/308 no transmiten la sesión a otro destino ni repiten una adopción; sin cambios de ejecución (guía 45).

- Android recupera controles crema con borde de 15,5 y sombra acotada al campo, y navegación de ancho completo que respeta teclado/zona segura; guía 44 y 139 regresiones.

- Medidor HTTP local incorpora reportes paginados, presupuesto de peticiones, rechazo de redirecciones y límite de respuesta; evidencia y alcance en guía 43.

- API pública de reportes con páginas de 20, búsqueda previa al límite y presupuesto de lectura separado; comparte ocultación con la ruta legacy. Android integra búsqueda temporizada, carga por página y recuperación explícita (guía 42).

- Rescates Android integra búsqueda en la ilustración y agrupa acciones; búsqueda temporizada del servidor y paginación, conservando lectura accesible al ampliar texto.

- Actividad y auditoría explican publicación/retirada de fotos, contacto, envío de adopción y errores; conservan los códigos y traducen el resultado del detalle.

- Panel web recupera Inter y la jerarquía del Figma; los indicadores se muestran en cuadrícula adaptable sin carrusel, conservando datos, enlaces autorizados y traducción.

- Perfil Android recupera la tarjeta y jerarquía de Figma e incorpora consulta de roles propios por ámbito, sin permitir autoasignación y descartando datos tras denegación o cierre de sesión.

- Android recupera navegación inferior de ancho completo y vectores originales; la ficha incorpora cápsulas de edad/tamaño e historia visual basada en datos públicos verificados, con acción de adopción siempre visible.

- Catálogo Android recupera la composición del Figma: encabezado centrado, filtros integrados en la ilustración y filas compactas adaptadas al texto ampliado.

- Cliente móvil acota respuestas JSON a 1 MiB antes de decodificarlas y señala cancelación al vencer el plazo; conserva estados HTTP y evita reenvíos automáticos.

- Adopción móvil permite consultar el resultado tras una respuesta perdida, sin anunciar éxito ni repetir el envío; mantiene cancelación y acciones visibles con texto ampliado.

- Android unifica encabezados de sección medidos con la fuente del Figma: evita títulos cortados con texto ampliado, preservando volver y actualizar.

- Se documenta una medición HTTP reproducible exclusivamente local, con latencia, tamaño de respuesta y límites explícitos.

- Solicitudes de adopción creadas desde la API móvil emiten auditoría transaccional y revisión del panel; el flujo web evita duplicar eventos y no registra observaciones privadas.

- Corrección de fidelidad al Figma original: JetBrains Mono, sombras cálidas visibles, campos translúcidos y tarjetas/controles comunes en Android y panel, con alternativa accesible sólida.

- Panel incorpora publicación/retirada de fotografías con vista previa local, consentimiento, cancelación segura y traducción; se verificó su lectura en Android.

- Android muestra fotos públicas autorizadas en catálogo/ficha, sin pedir imágenes inexistentes; incorpora validación, versión y reintento. La publicación se gestiona desde la pantalla de fotografías del panel.

- Backend prepara fotografías públicas con autorización explícita, WebP optimizado, retirada y migración propia; integración visual en panel y Android.

- Android integra catálogo de 24 fichas por página, carga manual y filtros globales; API conserva el contrato anterior y añade un escenario QA reversible.

- Catálogo Android adapta columnas y altura de tarjetas al texto ampliado, con nombres de hasta dos líneas.

- Android evita que un registro tardío reabra la sesión cerrada o reemplace una cuenta que ingresó después; dos regresiones verifican ambas carreras.

### Añadido

- Identidad visual compartida en Android y panel: bienvenida crema, lienzo operativo claro, navegación translúcida accesible, tipografía local y acceso móvil directo desde bienvenida.

- Edición móvil del nombre y teléfono propios, con confirmación al descartar borradores, guardado transaccional y auditoría sin ampliar permisos de cuenta.

- QR temporal de identificación en Android, generado por el backend al solicitarlo, con confirmación al reemplazar y retirada local al vencer o salir de la app. No concede acceso clínico.

- Mis mascotas y lectura privada del expediente en Android, con atenciones y correcciones sujetas a los permisos existentes.

- Ficha pública individual de adopción con edad, tamaño, organización y custodia reales; deja de estar disponible cuando la mascota sale del catálogo.

- Gestión móvil de reportes anónimos mediante número y clave: corrección, eliminación de contacto y cierre confirmado.

- Campana y bandeja móvil de notificaciones de la cuenta, con filtro sin leer y confirmación de lectura.

- Pantallas móviles de rescates, búsqueda pública, reporte, confirmación y seguimiento privado de reportes.
- Consulta pública de ciudades activas y tipos de reporte, y listado privado con el caso de rescate del propio reportante.

- Cliente Android de Little Paws Net con cuenta, catálogo, ficha, solicitud y seguimiento de adopción.
- Preparación de un escenario sintético de adopción para comprobar la app y el panel contra un MySQL local.
- Nombre de la mascota y fechas de la solicitud en el listado privado de adopciones de la cuenta.

### Optimizado

- Portada móvil convertida a WebP: 87,9 % menos bytes, misma resolución y sin peticiones de imagen al servidor.

### Corregido

- Las mascotas sin nombre registrado no provocan un fallo al cargar el catálogo móvil.

- Cabecera y navegación móviles se adaptan al texto del sistema ampliado al 200 % sin desbordar en pantallas pequeñas ni en horizontal.

- La app controla respuestas incompletas del catálogo y seguimiento de adopciones. Una confirmación sin ID indica consultar las solicitudes antes de repetir el envío.

- La app cierra la sesión si el servidor rechaza el acceso después de renovarlo y permite volver a ingresar.
- Se descartan respuestas atrasadas de otra cuenta y se controlan respuestas inválidas de autenticación.
- La renovación concurrente y la restauración del acceso no modifican una sesión nueva ni notifican después de su cierre.

- Al guardar un recurso que dejó de existir, el panel muestra un aviso y responde con HTTP 404. La operación queda registrada como fallida.


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


### Trabajo local sin publicar · 20 noviembre · rediseño Stitch

- UI móvil orgánica, controles redondeados, inicio compacto y navegación flotante.
- Galería pública consentida (hasta seis fotos) y metadatos fuera de imagen.
- Directorio público verificado, comunidad con comentarios/reacciones/moderación y ayudas por entidad con control de versión.
- Tienda y compromisos de aporte reutilizan contratos reales sin cobro.
- Se conserva aislamiento de sesiones, RBAC, trazabilidad y bloqueo de reenvíos inciertos.
- Nuevas migraciones aplicadas solo en QA local. No se crea una versión/tag ni se declara un despliegue de Railway.


### Corrección local · barra contextual y acceso

- Botón central elevado y pulsable, con concavidad real: Inicio o selección de mascota para nueva solicitud según la pestaña.
- Tema anterior de login/registro aislado del resto de Stitch.
- Demo Android independiente con fotografías ficticias, cabecera accesible y área segura; conserva el cliente QA real.
- 161 pruebas móviles aprobadas; sin cambios de backend/Railway o commits oficiales.


### Corrección local · ofrecimientos privados

- Ocultar Mis ofrecimientos al salir y volver a consultar al cambiar de cuenta.
- Rechazar respuestas tardías y rutas privadas sin sesión; evitar recargar por una edición del mismo perfil.
- Cuatro regresiones nuevas,165 pruebas Flutter y análisis limpio; candidato QA separado, sin instalación o publicación.


### Corrección local · 21 noviembre · formularios y sesión

- Separar borradores y confirmaciones de pedidos/aportes por cuenta; ocultarlos al salir y descartar respuestas de otra sesión.
- Conservar una edición del mismo perfil y mantener público el catálogo; autenticar antes de redactar un pedido/aporte.
- Seis regresiones nuevas;171 pruebas Flutter y análisis limpio. Sin cobros, cambios de backend o publicación.


## Comunidad y reportes · 22-11-2026

Fotos públicas de perfil con consentimiento y retirada, navegación central a reportes, rescates en cuadrícula, directorio editorial y tienda con imagen lateral. Guía65; integración local y aceptación real pendientes.


## Cierre tienda y referencias visuales ·22-11-2026

Tienda con fotos autorizadas, importe decimal exacto y comprobante del servidor; bienvenida/login según los SVG del usuario; accesos circulares de Inicio, reporte por etapas y retrato opcional en expediente protegido. Ver docs/diseno/66-tienda-fotos-y-pedido-trazable.md y docs/diseno/67-referencias-acceso-expediente-y-reporte.md. Implementación local; el punto14 conserva la aceptación en dispositivo y entorno real pendiente.

### Revisión local 68 — 22/11/2026
Selección deslizante en navegación de vidrio con alternativa opaca, transiciones breves sin duplicar vistas privadas, tarjetas de inicio más concisas, acciones de tarjeta sin relleno innecesario y revisión renderizada de 34 vistas a dos escalas. Aceptación en dispositivo e integración real pendientes.
