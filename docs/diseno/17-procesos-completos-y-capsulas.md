# Quinta fase: procesos completos, selectores y cierre de landing

Fecha: 3 de noviembre de 2026. Alcance: hoja de ruta funcional/visual del mismo día y revisión de scrolls y acciones de confirmación.

## Comportamiento implementado

### Entidades

Los procesos de organización incluyen un selector dentro del formulario. Las acciones desde cada fila precargan su entidad. La cabecera dejó de ser una dependencia oculta para designar responsable, proponer transferencia, resolver una pendiente o pedir verificación.

El selector solo ofrece destinos autorizados por el motor. Cambiarlo recarga el formulario y sus opciones dependientes dentro del diálogo; no envía información privada como parámetros de búsqueda. Un destino ajeno o manipulado se rechaza antes de despachar a la API. La operación sigue utilizando sus servicios transaccionales reales.

Las transferencias muestran organización y participantes, con estado Pendiente, en vez de «Registro #…». Solo el destinatario resuelve la transferencia; no se reemplazó la aceptación por un cambio de rol. Si no hay pendientes elegibles se explica que no hay datos previos. La verificación puede solicitarla el principal vigente o una cuenta con administración de entidades (`entidades.editar`), comprobando la baja administrativa y evitando otra solicitud abierta.

### Ciudades y animales

Riohacha ya estaba activa en producción: DIVIPOLA 44001. No se añadió un duplicado. Se sustituyó la combinación de buscador independiente y select convencional por un combobox que conserva el ID, ofrece coincidencias por nombre/departamento, normaliza mayúsculas/tildes y funciona con ratón, flechas, Enter, Escape y resolución inequívoca al salir. La búsqueda es local sobre las opciones autorizadas de ese formulario; escribir no genera consultas adicionales. Sin JavaScript se conserva el select nativo.

Mascota admite especie independiente, raza opcional y descripción de otra especie o animal no identificado. Una raza conocida infiere especie; una pareja incompatible se rechaza en servidor. No se crean especies o razas ficticias para cumplir campos obligatorios. Quien tenga permisos de catálogos puede añadir especies y razas reales. La compatibilidad con fichas antiguas se mantiene mediante backfill y propiedades que toleran raza nula. Los endpoints de alta propia, alta de rescate, edición y catálogo público usan la nueva identificación.

Los reportes explican Rescate, Mascota perdida, Animal encontrado, Abandono y Maltrato. La mascota registrada es opcional y el tipo se ve separado del estado en el detalle y en el listado. Los reportes de búsqueda/reencuentro no se aceptan como rescates mediante el endpoint de aceptación. No se obliga a crear una ficha para reportar una situación.

### Adopción

Una consulta compartida define la disponibilidad pública: estado En adopción, sin titular particular, custodia vigente única, fundación verificada y no desactivada. Se utiliza en el API público, la selección de mascota para solicitar, el catálogo y el contador del dashboard. La creación de solicitud bloquea el registro y vuelve a comprobar disponibilidad; rechaza una solicitud pendiente duplicada.

La pantalla distingue Disponibles para adopción, Mis animales y Fichas autorizadas. La última respeta la consulta del motor, sin convertirse en una vía para ver expedientes ajenos. El alta propia redirige a Mis animales; los detalles y ediciones autorizados no quedan rotos por el filtro público. La actualización parcial también corrige la URL visible tras guardar, evitando mostrar una pantalla distinta de la ruta.

### Filtros y scroll

En auditoría, seleccionar módulo, resultado, persona o tipo aplica los filtros. Enter en los controles aplica la consulta sin buscar el botón superior. Se conserva el foco al sustituir resultados y se cancelan búsquedas anteriores mediante el mecanismo de navegación parcial existente. Se conservan tabla, agrupación, URL y alternativa explícita de Aplicar filtros.

Los diálogos tienen cabecera, una zona central desplazable y una zona de acciones independiente. Los botones siguen asociados al formulario original mediante el atributo `form`, por lo que se mantienen la validación, CSRF y el envío real. Guardar/Confirmar/Descartar no requieren bajar al final del cuerpo. Se retiraron alturas máximas y scrolls verticales anidados en matrices, listas de roles, selector de roles y grupos de permisos. El scroll horizontal de una tabla ancha y el desplegable de opciones siguen disponibles cuando hacen falta.

### Landing

El cierre usa las tres cápsulas de `Frame 1.svg`, reconstruidas como HTML semántico adaptable y traducible. Se extrajeron cuatro capas de nubes a partir de sus paths originales: 65.708 bytes en total sin los textos convertidos a contornos, fondos duplicados ni filtros de sombra pesados. No se generaron imágenes con IA.

Conserva la tipografía LPN Script/Inter y la identidad crema/salvia/arcilla. Las cápsulas se apilan en móvil, las nubes entran desde los bordes y hay un desplazamiento de profundidad discreto ligado al scroll. Sin movimiento o con movimiento reducido el contenido permanece visible; no se impone scroll controlado ni se retrasa una operación. El modo oscuro adapta superficies y contraste sin navegar al login.

## Los 17 fundamentos: cobertura

| Referencia | Aplicación y comprobación |
| --- | --- |
| 1. Confirmación clara | Se conserva nombre, consecuencia y verbo real de la fase anterior; se corrige la accesibilidad permanente de sus acciones. |
| 2. Jerarquía de tarjetas | Cápsulas con título, información y apoyo; catálogo separado de fichas internas. |
| 3. Navegación/acciones | Se conservan menú dinámico y destinos; acciones contextuales por organización, fuera del catálogo público. |
| 4. Movimiento | Cuatro capas del SVG, aparición escalonada y profundidad leve; alternativa sin movimiento probada. |
| 5. Feedback/reintentos | Envío parcial con estado y bloqueo mientras procesa; confirmación real y errores preservados. Verificación y adopción rechazan duplicados. |
| 6. Proximidad | Formulario de negocio en una columna dentro de modal; grupos de permisos sin scroll interno; tarjetas sin líneas redundantes. |
| 7. Login simple | No recibe recursos de landing; se comprueba una sola petición del documento mientras queda inactivo. |
| 8. Prioridad | Se conservan indicadores y resumen de accesos; el contador de adopciones ahora comparte la regla del catálogo. |
| 9. Tipografía | LPN Script/Inter, títulos adaptables, cuerpo legible y metadatos secundarios sin encoger toda la interfaz. |
| 10. Etiquetas/ayuda | Etiquetas persistentes y ayuda de ciudad, especie, raza, situación y contexto; combobox asociado a su etiqueta. |
| 11. Carga estable | Navegación parcial y carga localizada existentes; recarga de contexto dentro del diálogo, sin skeleton ni retrasos artificiales añadidos. |
| 12. Botones | Jerarquía existente y footer compacto persistente; la alternativa de volver/cancelar no queda perdida al final del scroll. |
| 13. Documentación | Hoja de ruta, contratos, migraciones, escenarios reproducibles y este informe, distinguiendo límites y estado real de validación. |
| 14. Validación | Errores del API se asocian a campos cuando es posible; especie/raza compatibles, selección inequívoca y contexto comprobado en servidor. |
| 15. Fechas | Se conservan Desde/Hasta y agrupación; Enter ejecuta los filtros. No se deshabilita el historial pasado. |
| 16. Énfasis/voz | CTA principal por contexto y traducción de los textos nuevos; no se añadieron primarios competidores. |
| 17. Alineación | Textos y campos alineados para lectura, cápsulas agrupadas y fuentes coherentes con la marca. |

No se reescribieron funciones que ya cumplían el fundamento. La guía se aplica a comportamiento real; no es una afirmación de certificación completa de UX o accesibilidad.

## Cambios de datos

- `animals.0006_identificacion_flexible`: raza nullable, especie opcional independiente y descripción de especie con valor vacío predeterminado también en base de datos, para compatibilidad durante el despliegue. Completa la especie de fichas con raza conocida sin modificar su identificación histórica.
- `core.0010_reporte_encontrado`: añade idempotentemente el valor Animal encontrado si existe el tipo de maestro de reportes.
- No se cambia titularidad, roles, contraseñas ni se crean mascotas/organizaciones ficticias en producción.

## Validación local

- 242 pruebas Django pasaron: la regresión RBAC existente y diez pruebas nuevas de procesos, identificación, privacidad y disponibilidad.
- 15 comprobaciones de navegador pasaron: Riohacha con ID, ayuda de reporte, otra especie sin raza ficticia, designación/entidad propia, verificación, filtros automáticos/Enter, footer fijo con único scroll, cápsulas y cuatro nubes, anchos 390/768/1366/1920/2560 y movimiento reducido.
- Cinco comprobaciones RBAC con dos sesiones abiertas pasaron: ausencia inicial de vista administrativa, concesión y actualización automática, permiso real de entrada, retirada automática y rechazo en backend.
- Seis comprobaciones de asignación múltiple pasaron: catálogo completo, perfiles antes bloqueados, cuatro asignados, persistencia al recargar, móvil y restauración del escenario local.
- Revisión axe de reportes, mascotas, entidad, auditoría y landing en claro/oscuro: sin violaciones automáticas de las reglas WCAG AA ejecutadas. Sin desborde en móvil en esas cinco vistas. Los tres formularios nuevos comprobados se presentan en inglés. Login: una única petición inicial de documento y ninguna adicional en la observación inactiva.
- Comprobación de modelos: ninguna migración faltante; JavaScript validado sintácticamente.

Evidencias: `output/fase5-2026-11-03/`, logs privados de ejecución en `.codex_tmp/` y verificaciones RBAC en `output/roles-abiertos-2026-11-03/`. Los escenarios de escritura se realizaron únicamente en la base aislada local.

## Límites que deben mantenerse visibles

Una prueba automática no certifica navegación completa con lector de pantalla ni comportamiento bajo carga masiva; faltan ensayos manuales y de carga representativa para esa certificación. Los tipos de reporte orientan el proceso, pero no crean por sí solos una operación de rescate ni un servicio público de emergencia. La especie descrita por un usuario no se incorpora automáticamente al catálogo oficial. Las cuentas no pueden aceptar transferencias ajenas ni acceder a expedientes sin la autorización del negocio.

No se crean commits ni ramas en esta entrega. Los resultados de respaldo, migración y despliegue se añaden tras comprobar la publicación.

## Publicación comprobada

Despliegue final Railway `68b395de-9583-4e16-8017-37a204f81a0b`: **SUCCESS**, comprobación de salud correcta. Se mantiene el servicio anterior sin cambios.

Respaldo previo privado: 393.025 bytes; SHA-256 `8d558fc305c892f82972652777d2ba652876d2f72e1f547a2fdc83dcf251fa89`. Aplicadas correctamente `animals.0006_identificacion_flexible` y `core.0010_reporte_encontrado` exclusivamente a `little_paws_panel_v2`. El archivo temporal de conexión se retiró.

La última suite completa repitió las **242 pruebas** y pasó. Dos pruebas adicionales de teclado pasaron: Escape cierra las sugerencias sin cerrar el diálogo y las flechas/Enter seleccionan Riohacha.

Las **12 comprobaciones de producción** pasaron: Riohacha con registro existente, Animal encontrado disponible, identificación flexible sin raza obligatoria, vistas de mascotas separadas, contexto dentro de formulario, filtros automáticos, Enter, footer fijo sin scrolls internos, cápsulas/nubes, móvil sin desbordamiento, API pública de adopciones y login con una sola petición inicial. No hubo errores JavaScript. La verificación pública no envió formularios de negocio ni creó datos ficticios. Se cerró la sesión privada temporal de revisión.
