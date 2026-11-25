# Formularios legibles y material de vidrio · Android

Revisión local del 19 de noviembre de 2026. La nueva petición autoriza cambiar la fuente y refinar el diseño con criterio de lectura: conserva la identidad de Figma, pero sustituye la tipografía monoespaciada de la interfaz y sus sombras intensas. No se presenta como un calco literal de los frames.

Se revisaron la guía de los 17 vídeos y el contexto original del formulario `145:1341`. La guía previa se basa en muestras visuales y transcripción local; no se afirma haber vuelto a reproducir los 17 vídeos completos en esta revisión.

## Sistema visual aplicado

- Inter local para interfaz, formularios y controles. La marca y las ilustraciones originales se conservan; la bienvenida mantiene su expresión manuscrita.
- Fondo de bienvenida `#FCF0D3`; lienzo de la aplicación `#FFF9EC`; lectura sobre papel claro `#FFFCF5`. Salvia para la acción principal y selección; tinta cálida para el contenido.
- Tarjetas de información con radio 24; campos de 14; botones de 18; capa de acciones/navegación de 28. Los radios expresan niveles de contención, no se convierte todo en una píldora.
- Botones principales en negrita y salvia. Cancelar es una acción de texto con menor énfasis. Se mantienen objetivos táctiles y adaptación a texto ampliado.
- Sombras suaves en el contenedor del grupo; se eliminan las sombras oscuras de cada campo, de sus contadores y de los bloques de identidad.
- Etiquetas persistentes fuera de los campos. Los límites de longitud siguen activos aunque se retire el contador permanente para reducir ruido.
- La navegación y la barra de acciones usan vidrio con tinte claro, borde, sombra corta y desenfoque recortado. Los párrafos y campos no tienen un filtro de desenfoque por cada elemento.
- Reducir transparencia y contraste alto sustituyen el material por una superficie sólida. Se conserva la preferencia y no se hace otra consulta al cambiarla.

Es una adaptación en Flutter/Android, no el componente nativo Liquid Glass de Apple. El desenfoque se limita al rectángulo recortado del control, siguiendo la [documentación de BackdropFilter](https://api.flutter.dev/flutter/widgets/BackdropFilter-class.html). No se ha certificado rendimiento en dispositivos físicos ni equivalencia óptica con iOS.

## Distribución de la información

**Reportar un animal:** explicación breve → Situación (tipo y descripción pública) → Ubicación (ciudad, barrio, dirección e indicaciones) → Contacto privado opcional. Los datos públicos y privados no se mezclan. Enviar permanece fuera del scroll. Al escribir la ciudad se reposiciona el campo para dejar espacio a las sugerencias, incluido texto al 200 %.

**Solicitud de adopción:** ilustración original → una tarjeta con el animal como dato protagonista, identidad de quien envía como texto informativo y motivo opcional. El nombre de la cuenta no parece un campo editable. Se explica dónde consultar el resultado. Cancelar y Enviar permanecen visibles; el resultado incierto conserva su salida a Mis solicitudes y evita repetir el POST.

## Aplicación de los 17 fundamentos

| Vídeo | Aplicación y alcance real |
|---|---|
| 1 · Confirmaciones | Se conservan las confirmaciones existentes y sus consecuencias. Este cambio no añade un borrado nuevo. |
| 2 · Jerarquía de tarjetas | Mascota protagonista en la solicitud; secciones claras en reporte; identidad secundaria. |
| 3 · Navegación frente a acción | Los cuatro destinos siguen en la barra; Reportar/Enviar siguen siendo acciones separadas. Selección mediante fondo y peso, además del color. |
| 4 · Movimiento | No se agregan parallax ni esperas a los formularios. Se respetan preferencias del sistema. Las nubes/landing web quedan fuera de esta revisión Android. |
| 5 · Una operación y respuesta | Se preservan bloqueo de envío, texto Enviando y manejo de respuesta incierta. Cubiertos por pruebas existentes. |
| 6 · Proximidad | Se elimina la caja/sombra por cada campo y se agrupan datos relacionados dentro de tres secciones. |
| 7 · Login sencillo | Conserva acceso directo y validación; recibe tipografía y superficies del sistema. No se simulan recuperación o CAPTCHA que el contrato móvil no tiene. |
| 8 · Decisiones iniciales | Solicitud presenta animal, identidad y motivo; el resto de la gestión continúa en sus destinos. No se ocultan permisos o roles para simplificar. |
| 9 · Escala de lectura | Inter, lectura de formulario a 16, apoyo a 14 y títulos de sección a 18. La revisión posterior del catálogo usa nombres de 16, resúmenes de 14 y microetiquetas/filtros de 12, con altura calculada y un único anuncio accesible por ficha. |
| 10 · Etiquetas | Etiquetas externas persistentes en reporte y solicitud; el placeholder aporta solo un ejemplo. |
| 11 · Carga | Se conservan carga localizada y estados reales; no se incorpora un skeleton artificial ni se retrasa una respuesta para mostrarlo. |
| 12 · Prioridades de botones | Enviar principal; Cancelar discreto. Negrita y geometría coherente. |
| 13 · Después del clic | Texto de seguimiento visible; error/resultado incierto y salida conservados. No se inventan confirmaciones. |
| 14 · Validación | Se mantienen errores al enviar y validación autoritativa del servidor; no se crean peticiones por comprobaciones de formato locales. La ciudad conserva su búsqueda necesaria y temporizada. |
| 15 · Fechas | No corresponde añadir un calendario a estos dos formularios. Los filtros de auditoría web quedan fuera de esta revisión. |
| 16 · Énfasis | La acción principal tiene mayor peso que cancelación y navegación; no todas las acciones reciben fondo salvia. |
| 17 · Alineación | Información del formulario alineada al inicio; espacios de 8/12 dentro de grupos y 20/24 entre bloques. |

No se declara implementado todo el proyecto por citar los 17 fundamentos: hay criterios conservados, aplicados ahora y otros que pertenecen a pantallas distintas. Mapa, tienda, apadrinamiento y los contratos pendientes de la guía 40 siguen pendientes.

## Verificación

Evidencias en `output/adopcion-movil/*formularios-glass-20261119.log`; suite Flutter, análisis y APK de QA local. Se revisan formularios normal/al 200 %, teclado y ciudad, cancelación, permisos existentes, preferencias de transparencia y navegación. Las pruebas de navegación cargan la fuente Inter real para medir su geometría.

La comparación y las capturas nuevas se guardan en `output/formularios-liquid-glass-2026-11-19/`; el mosaico vigente se vuelve a capturar desde el APK. Las cuentas/datos visibles son sintéticos. No se envían formularios de negocio para obtener las imágenes, ni se publica en Railway.
