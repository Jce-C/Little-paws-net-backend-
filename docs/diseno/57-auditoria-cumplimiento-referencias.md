# Auditoría de cumplimiento · Little Paws Net · 21 noviembre 2026

> La guía58 registra un bloque posterior que resuelve onda, integración de Inicio, capas, formularios, perfil y movimiento. Este informe conserva el diagnóstico previo; los pendientes de contratos públicos y validación real continúan.

## Dictamen

El rediseño NO cumple todavía todos los puntos al nivel solicitado. La guía56 y el resumen de entrega describían cobertura de áreas, pero eso no equivale a cumplir cada requisito visual o de datos. Las pruebas funcionales aprobadas tampoco prueban fidelidad visual. Esta auditoría sustituye cualquier interpretación de «todo completado» de la entrega anterior.

Se contrastaron el encargo integral de14 apartados, las6 páginas renderizadas del PDF, el inventario de7 HTML del ZIP, la guía de los17 vídeos, las fuentes reales y las20 capturas Android de la revisión56. No se volvieron a reproducir los17 vídeos ni se repitió una auditoría del panel administrativo Django. La inspección de navegador de56 cubre bienvenida/login, no todos los procesos autenticados en producción.

**Publicado:** demo Sites v5, commit ff4f099e0c72ab34aad83fa28b37c3c241dcc712. **Local:** tres correcciones adicionales de esta auditoría, aún no publicadas ni instaladas en el emulador. El mosaico de56 muestra la versión anterior a estas tres correcciones. No confundir ambos estados.

## 1. Identidad visual y estilo

**Base implementada; fidelidad parcial.**

- Paleta propia: bienvenidaFCF0D3 y operaciónFFF9EC, salvia, rosa, mantequilla y carbón: sí.
- Tipografía, radios y botones compartidos: sí, en lpn_theme.dart y refined_surfaces.dart.
- Iconos consistentes con variantes para selección: sí. No se han sustituido por familias inconexas.
- Jerarquía y agrupación: mejoradas, pero Inicio sigue siendo una cuadrícula de tarjetas opacas parecidas entre sí; falta el trabajo de capas/material de la referencia AI Notes.
- Contraste: se detectó muted sobre blush4,456:1. Corregido localmente de675D50 a655B4E, manteniendo la familia cálida. La prueba nueva comprueba19 combinaciones planas a4,5:1. Esto NO certifica todos los estados, transparencias, foco o TalkBack.
- Personalidad/coherencia de todas las pantallas: parcial; existen superficies antiguas y tarjetas nuevas, no una aceptación visual completa de todos los estados.

## 2. Logotipo e iconografía

**Parcial.**

- Perro completo en acceso, encabezado y medallón: sí; el logo ya no se limita al hocico.
- Estudio orgánico: existe docs/diseno/recursos/logo-organico-estudio.svg.
- No se presentó ni validó una comparación aplicada del hocico nuevo frente al original. El archivo de estudio no equivale a haber implementado esa variante en la interfaz.
- No hay una imposibilidad técnica o de accesibilidad que impida explorar esa forma; la decisión pendiente es visual y de identidad.

## 3. Bienvenida antes de iniciar sesión

**Cumplimiento funcional y de distribución básica.**

- Acceso directo a login y registro: sí, sin pasar por otra pantalla promocional.
- Acción principal diferenciada y secundarias discretas: sí.
- Ilustración original, descripción de adopción/red/ayuda/comunidad y marca completa: sí.
- Ajuste en ventanas ordinarias y texto ampliado: comprobado por las pruebas de bienvenida/viewports de56.
- En móviles muy altos queda espacio libre al final. No se deben inflar controles para llenarlo; sigue siendo posible afinar la composición.
- La descripción resume el propósito; puede explicitar mejor «solicitar adopción» y aportes monetarios. No se da por implementado un sistema de pago.

## 4. Inicio después de iniciar sesión

**Parcial importante de diseño.**

- Imagen sin textos ni botones superpuestos: sí.
- Textos y acciones separados y seis destinos reales: sí.
- Imagen como fondo integrado, no un encabezado independiente: NO. ExploreScreen usa ClipRRect + Image.asset de168px y después la introducción; sigue siendo un bloque de cabecera.
- Composición editorial con profundidad/materiales suficientemente cercana a la referencia: todavía no.
- Además Home inicia en índice1 (Adoptar); Inicio es índice0. La pantalla nueva de servicios no es necesariamente el primer destino tras acceder. Hay que decidir y probar ese recorrido, no presentarlo como ya alineado con el encargo.

## 5. Adopción

**Funcionalidad principal existente; presentación y contenido parciales.**

- Fotos reales autorizadas, tamaño uniforme y fallback sin foto: sí. Stock solo en registros ficticios identificados de la demo.
- Galería, deslizamiento e indicadores: implementados. pet_gallery_test.dart prueba dos fotos y compatibilidad con portada antigua; rechaza rutas de otra mascota y más de6 imágenes. La captura de demo muestra1 foto, por lo que NO demuestra visualmente una galería de varias fotos en producción.
- Nombre, edad, sexo y tamaño fuera de la fotografía: sí.
- Estado «En adopción» y acción de detalle: sí, en catálogo de disponibles.
- Etiquetas/iconos de metadatos en tarjetas: parcial; las tarjetas usan líneas de texto centradas, las cápsulas/iconos están principalmente en el detalle.
- Descripción editorial breve: falta. Especie/raza no reemplazan una descripción de la mascota.
- Requisitos de espacio, responsabilidad y recursos: sí, agrupados antes del envío.
- Cuidados especiales individualizados: no. Se muestra orientación general para consultar a la organización; el contrato público no devuelve esa información. No se debe extraer el expediente privado ni inventarla.
- Formulario, envío, salida, recuperación de respuesta incierta y límites de sesión: conservados y comprobados por la suite del cliente; no es una nueva prueba contra Railway.

## 6. Ayudas y voluntariado

**Parcial con un fallo funcional corregido localmente.**

- Tres modalidades diferenciadas: sí.
- Fondos/aportes registrados como compromisos, sin fingir dinero recibido: sí.
- Medios oficiales bancarios: no se publican; falta contrato/configuración y datos consentidos.
- Necesidades en especie: se muestra necesidades_ayuda cuando existe; no hay catálogo estructurado de cantidades, fechas o materiales.
- Voluntariado: antes se listaban TODAS las fundaciones, incluso acepta_voluntarios=false o sin publicar. Dos regresiones reprodujeron el error. Ahora solo aparecen fundaciones con aceptación explícita true. Sin datos se muestra estado vacío. No se eliminan organizaciones ni se cambia autorización.
- Actividades concretas de voluntariado: no hay lista estructurada. Texto libre de necesidades no equivale a un programa de actividades.
- Herramientas de gestión: ocultas para401/403; se conserva reintento para fallos del servicio. Sin embargo, una cuenta con acceso autorizado sigue viendo gestión y participación en la misma pantalla. El divisor no constituye una separación visual completa de ambas áreas.

## 7. Organizaciones y veterinarias

**Parcial.**

- Nombre, tipo, ciudad, dirección/descripción disponibles y filtros por tipo: sí.
- Diferenciación por iconos: sí.
- Logo/foto, contacto público y servicios ofrecidos: no están en el contrato público.
- Preparación visual de esos campos: insuficiente. Hay un aviso de «no publicados», pero no una ficha ampliada preparada para todos los campos solicitados. No se puede llamar completa a esa integración.
- Refugio como tipo independiente: no existe en el directorio actual; los tipos públicos son Fundación, Veterinaria y Tienda. No fabricar una clasificación que la BD no publica.

## 8. Comunidad

**Funcionalidad principal implementada; aspecto de perfil parcial.**

- Publicar, consultar, comentar, responder, reaccionar, autor/fecha y orden cronológico: sí, con API real y pruebas de cliente.
- Carga, vacío, errores y validación de contenido: sí.
- Tarjetas e interacciones: mejoradas y funcionales.
- Fotografías reales de perfil: no se integran; se utiliza una inicial, un fallback válido pero distinto al solicitado.
- El simulador guarda temporalmente en memoria; está identificado como demo y no prueba persistencia de producción.

## 9. Tienda

**Parcial.**

- Catálogo, categorías, precio, disponibilidad, descripción/detalle y preparar pedido: sí.
- Pedido sin cobro: real en el cliente, con confirmación explícita de que no procesa un pago.
- Fotografías de productos: NO. Se añadió un contenedor con icono/aviso, no un proveedor de imagen funcional.
- Existe ProductoImagen en el modelo, pero el catálogo no lo expone. Se necesita publicación, autorización y retirada de imágenes; no basta con añadir Image.network ni con publicar ArchivoDigital privado.
- Composición de hotel/viaje: aproximación parcial. El contenedor sin foto no alcanza el resultado de la referencia.
- No se requiere inventar carrito o proveedor bancario para «rellenar» esta sección.

## 10. Nomenclatura de reportes

**Completo localmente tras corregir una omisión.**

- Título principal «Animales que necesitan ayuda»: ya estaba.
- Seguían tres mensajes vacíos con «casos activos»: corregidos a reportes y ayuda. Se actualiza la regresión de búsqueda; no se cambia el significado ni el filtrado de estados.
- La demo publicada v5 todavía contiene esos textos anteriores hasta una nueva publicación.

## 11. Navegación

**Cumplimiento básico verificado.**

- Cuatro destinos persistentes, etiquetas y selección reconocible: sí.
- Inicio da acceso a adopciones, ayudas, comunidad, tienda y directorio: sí, sin poner todos en la barra.
- Cápsula con concavidad y medallón fuera de ella: sí.
- Medallón funcional: Inicio y, en Solicitudes, más para elegir mascota: sí.
- Área táctil mínima48, teclado/zona segura y texto ampliado: comprobados por los tests existentes.
- La decisión de arranque de Inicio/Adoptar sigue señalada en4; no es una barrera técnica.

## 12. Animaciones

**Parcial.**

- Entrada finita280ms, cambio de icono central180ms, transición de rutas y galería240ms: sí.
- Movimiento reducido: previsto en las animaciones propias.
- Aparición progresiva/escalonada de tarjetas y una presentación más elaborada siguiendo las referencias: no. FeatureDeck es estático; OrganicSurface no anima por defecto.
- No se debe afirmar que se aplicó íntegramente el estudio de movimiento de los vídeos por tener un fade inicial.

## 13. Arquitectura y restricciones

**Cumplimiento del bloque local comprobado.**

- Se mantienen Flutter, API y componentes reutilizables; no se sustituye el producto por una maqueta.
- No se inventan registros reales, pagos, contactos ni fotos de mascotas reales.
- No se eliminan datos ni se alteran permisos/backend en esta auditoría.
- Se conservan borradores por identidad y defensas ante respuesta tardía; los dos filtros nuevos no cambian autorizaciones.
- No se hacen commits oficiales, despliegues/migraciones Railway o modificaciones del Figma manual.

## 14. Verificación final

**Parcial como aceptación integral; pruebas de cliente sí.**

- Antes:191 pruebas canónicas y197 del simulador. No representan191 comprobaciones visuales ni certificarían toda producción.
- Esta auditoría: dos regresiones de voluntariado reproducidas antes del arreglo y una de contraste reproducida antes del ajuste. Después:194 pruebas canónicas completas y análisis limpio.
- Contraste medido de19 combinaciones planas; no una certificación WCAG completa.
- Capturas inspeccionadas: las20 de56, comparadas de nuevo con las6 páginas del PDF. No se generaron capturas nuevas ni se instalaron los arreglos de auditoría.
- Sigue faltando una aceptación de fidelidad visual de todos los estados y recorridos autenticados, dispositivo físico/TalkBack, y prueba de datos/operaciones reales contra un entorno de validación.

## PDF · resultado por página

| Página | Resultado de la revisión |
| --- | --- |
| 1 | Adopción mejorada. Inicio continúa demasiado próximo a seis bloques opacos; no se da por cerrado. |
| 2 | Corregidos superposiciones y recuadro grande de la huella. Tienda sigue sin presentación fotográfica final. |
| 3 | Iconos inferiores reducidos. Perfil casi conserva la estructura previa; se cambió más el nombre/copy que la distribución. Tienda estilo viaje/hotel: parcial. |
| 4 | Tarjetas AI Notes: aproximación débil. Gestión y usuario no tienen una separación visual completa. Formularios con sugerencias, pero varios mantienen el mismo fondo y estructura simple. |
| 5 | Chips y campos existen. Falta una composición de formularios más cercana a la referencia editorial y de temas. |
| 6 | NO está calcada. El masthead es un rectángulo con radios asimétricos, sin la onda ni la división de superficies de la referencia. No lo impide la accesibilidad. |

## ZIP · siete referencias

El inventario confirma siete code.html diferentes. No existe un calco de los siete ejemplos en Flutter ni una biblioteca importada del ZIP. Son referencias de composición; las funciones de viaje/notas no son requisitos del negocio.

- furniture_store_home: imagen/categorías/cuadrícula adoptadas parcialmente.
- bangkok_hotels_card: agrupación de metadatos aproximada; falta fotografía de producto.
- asia_trip_itinerary: no se construyó un equivalente claro de sus agrupaciones; influencia declarada no es evidencia de cumplimiento.
- ai_notes_your_notes: no se reproduce su composición de capas/materiales en Inicio.
- ai_notes_lecture: no hay una adaptación visual completa de lectura y acciones.
- ai_notes_editor: las sugerencias existen; el formulario conserva mucha estructura anterior.
- anana_resort_reviews: se tomó idea de tarjeta, pero no hay una reproducción de su materialidad; no se inventaron reseñas porque no forman parte del pedido funcional.

## Guía de los17 vídeos · revisión de aplicación en móvil

Se leyó la guía previa, no se volvió a analizar el audio/vídeo. Sus criterios que pertenecen a matrices RBAC, landing web o auditoría administrativa quedan fuera de esta comprobación móvil.

| Vídeo/principio | Evidencia y límite |
| --- | --- |
| 1 Confirmaciones claras | Descartar borrador/cambios tiene acciones explícitas. Bajas de productos/roles web: no revalidadas aquí. |
| 2 Jerarquía de tarjetas | Mejorada; metadatos centrados y composición de tienda todavía parciales. |
| 3 Destino frente a acción | Barra con destinos y medallón contextual: implementado y probado. |
| 4 Movimiento coordinado | Parcial: entrada breve, sin desfase progresivo de tarjetas. Landing/nubes web no auditadas de nuevo. |
| 5 Una operación por acción | Pruebas de envío/busy/respuesta incierta del cliente. Idempotencia multiusuario del servidor no certificada en esta auditoría. |
| 6 Proximidad y alineación | Mejoradas; aún hay superficies anidadas y decisiones de distribución por resolver. |
| 7 Acceso simple | Acceso directo y estados; recuperación de contraseña móvil no aparece en LoginScreen. El objetivo de una petición inicial corresponde al login web, no se atribuye a Flutter. |
| 8 Acceso progresivo | Cuatro pestañas y resto en Inicio. Dashboard web con indicadores/RBAC: fuera de esta revisión. |
| 9 Lectura sin miniaturizar | Pruebas con texto ampliado; contraste de19 pares corregido. No certifica legibilidad en todos los dispositivos. |
| 10 Etiquetas persistentes | Los campos conservan etiquetas. No se depende solo del placeholder. |
| 11 Carga sin saltos | Parcial: varias listas sustituyen el contenido por un spinner, sin reservar la estructura de lectura. |
| 12 Jerarquía de botones | CTA principal, secundarias outlined/text y acciones inferiores: implementado a nivel básico. |
| 13 Estados después del clic | Documentación y defensas de sesión existentes; faltan recorridos reales de aceptación integral. |
| 14 Validación oportuna | Validación al enviar, sin consultas triviales por tecla. La limpieza inmediata del error al corregir no está implementada de forma uniforme. |
| 15 Rango de fechas | Requisito de auditoría web: no se revalida en el móvil ni se inventa un selector de viaje. |
| 16 No destacar todo | Mejorado en bienvenida y formularios; sigue pendiente revisión visual completa de todas las acciones. |
| 17 Agrupar por contenido | Varias tarjetas aún centran todos sus metadatos; no está aplicada uniformemente la recomendación. |

## Prioridades para cerrar el encargo

1. Corregir funcionalidad/legibilidad: voluntariado, nomenclatura y contraste (ya corregidos en local en esta auditoría).
2. Rediseño visual pendiente, con los recursos ya disponibles: Inicio integrado, tarjetas de capas/materiales, login con onda y separación real de superficies, formularios más organizados y perfil redistribuido. No requiere inventar datos ni nuevos permisos.
3. Definir contratos públicos y gestión de publicación de fotos de productos, contactos/servicios de entidades y descripción/cuidados de mascotas. Después integrar sus campos reales.
4. Datos/actividades de voluntariado y medios oficiales de aportes. No convertir un compromiso en un pago ni mostrar «recibido» sin confirmación real.
5. Cerrar movimiento y estados de carga; comparar pantallas y estados con una lista de aceptación visual.
6. Validar móvil real y flujos de un entorno de pruebas del backend. Publicar solo el estado verificado y distinguirlo de los paquetes locales.

## Entrega de esta auditoría

Fuentes locales modificadas: explore/explore_screens.dart, rescue/rescue_screens.dart, design/lpn_theme.dart. Pruebas: volunteer_directory_test.dart (nueva), palette_contrast_test.dart (nueva) y ajuste del texto esperado en rescue_layout_test.dart. Las evidencias antes/después y contraste.json están en output/auditoria-referencias-2026-11-21.

No se cambió la demo Sites v5, el emulador, Railway, el backend o el documento Figma. El informe no promete que las correcciones locales ya se vean en el enlace.
