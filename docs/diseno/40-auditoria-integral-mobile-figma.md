# Auditoría de las 29 pantallas móviles de Figma

Referencia: archivo `sR48elLBOFINiQXIfwJsNu`, página `0:1`. Revisión del 19 de noviembre de 2026. Trabajo local; no publicado.

## Hallazgo principal

La implementación había sustituido parte de la composición por listas verticales, controles grandes y una cabecera de vidrio que no corresponden al prototipo. Esas diferencias no eran exigencias de Android ni de accesibilidad. El criterio corregido es conservar la estructura de Figma y adaptar únicamente datos reales, permisos, texto ampliado y controles operables.

Se consultaron los contextos de diseño y sus capturas de los 29 frames, incluidos los alternativos. Revisar un frame no significa que todas sus funciones estén implementadas. Las variantes de Max, Luna y Nala deben salir de un mismo componente con datos, no de pantallas y animales ficticios escritos a mano.

## Inventario completo y correspondencia

| Nodo | Pantalla | Resultado y diferencias que siguen abiertas |
|---|---|---|
| `3:2` | Bienvenida | Logo original, crema `#FCF0D3`, texto manuscrito y dos accesos. Conserva explorar sin cuenta como acción secundaria real. |
| `5:7` | Login | Marca original, etiquetas externas, sombras cálidas, botón compacto. El contrato móvil actual no contiene el desafío aritmético ni recuperación de contraseña; no se simulan. |
| `8:44` | Rescates | Se recuperan carrusel horizontal, categorías originales y búsqueda sobre el banner. Las tarjetas usan datos reales; el endpoint no entrega fotos ni nombres de animales. |
| `83:2` | Rescates, desplazamiento | Mismo carrusel desplazable, no una segunda pantalla duplicada. No se reproducen datos de Lucy/Cat/Rocky como registros reales. |
| `62:269` | Reportes cercanos | Pendiente el mapa operativo: faltan contrato público de coordenadas y proveedor de mapas. No se inserta una imagen de mapa que parezca interactiva. |
| `75:385` | Caso Lucy | Componente real de detalle de reporte, estado y seguimiento disponible. Faltan fotografía pública, cronología completa y financiación. |
| `93:257` | Caso Cat | Misma vista parametrizada. No se muestran etapas como completadas sin evidencia del backend. |
| `103:324` | Caso Rocky | Misma vista parametrizada. Importes de ejemplo y tratamiento no se convierten en hechos reales. |
| `136:875` | Apadrinamiento | Pendiente flujo móvil operativo: beneficiario verificado, finalidad, cuenta y comprobación del aporte. No se crean transferencias ficticias. |
| `145:1341` | Reportar animal | Formulario real con ciudad, dirección y validaciones. Usa superficies y botones del sistema corregido; selector directo de situaciones; todavía difiere del prototipo en algunos campos. La subida de foto de reporte necesita soporte específico, distinto de foto pública de adopción. |
| `145:1421` | Reporte enviado | Recupera logo y titular manuscrito. Conserva identificador/estado y protección de clave anónima. No promete que una fundación ya haya aceptado. |
| `108:376` | Adoptar | Banner original, filtros sobre su borde, cuadrícula y fotos dinámicas. Se conserva paginación y estados vacíos. |
| `128:502` | Conoce a Max | Componente de ficha pública, imagen y cápsulas de datos, historia verificada. No expone expediente privado ni QR a visitantes. |
| `145:981` | Conoce a Luna | Misma ficha con datos de mascota, sin duplicación de pantallas. |
| `145:1147` | Conoce a Nala | Misma ficha. La variante cromática del prototipo no debe indicar estado médico inexistente. |
| `136:671` | Solicitud, página | Se implementa esta composición en la navegación real: ilustración original, identidad de la cuenta, motivo y acciones siempre accesibles. Tipo de vivienda sigue pendiente en el contrato de solicitud. |
| `136:748` | Solicitud Max, ventana | Variante compacta del mismo formulario y misma operación; no otro POST. Se mantiene cancelación y recuperación de resultado incierto. |
| `145:1078` | Solicitud Luna, ventana | Misma variante parametrizada. |
| `145:1244` | Solicitud Nala, ventana | Misma variante parametrizada. |
| `128:599` | Expediente Max | Expediente privado existente con datos autorizados. Pendiente reproducir su composición compacta como ventana; actualmente es página. QR se genera bajo autorización. |
| `145:1023` | Expediente Luna | Mismo componente privado, sin vacunas ni documentos inventados. |
| `145:1190` | Expediente Nala | Mismo componente privado; la foto pública no concede acceso clínico. |
| `156:1796` | Perfil | Tarjeta de identidad y roles reales. Se añaden mascotas reales dentro del perfil, hasta tres y acceso a la lista completa. Los roles son informativos, no interruptores para concederse permisos. |
| `156:2037` | Perfil, iconos inferiores | Variante del mismo perfil. La navegación conserva destinos implementados: solicitudes ocupa el lugar de tienda mientras tienda no exista. |
| `156:1924` | Expediente desde perfil | Acceso directo al expediente permitido desde cada mascota sin custodia vigente. La presentación sigue en página; no se declara idéntica a la ventana de Figma. |
| `185:16` | Crear cuenta | Sin logo gigante repetido; etiquetas externas, campos con sombra, confirmación de contraseña, mínimo de 12 caracteres y botón compacto. Falta integrar aviso de privacidad verificable; no se añade una casilla sin documento ni registro de aceptación. |
| `150:1482` | Tienda | Pendiente interfaz y flujo comercial real con catálogo, disponibilidad y vendedores. No hay una tienda funcional móvil actualmente. |
| `156:1682` | Producto | Depende del catálogo comercial y datos reales del vendedor. No se muestra PetZone como comercio real integrado. |
| `156:1746` | Pedido por WhatsApp | Depende de producto, cantidad y teléfono validado del vendedor. Pendiente integración; no se usan teléfonos ni pedidos ficticios. |

## Cambios de esta revisión

- Cabecera principal plana, sin filtro de vidrio ajeno al diseño. Encabezados de sección centrados.
- Tarjetas horizontales en Rescates, de 122 px en texto normal; crecen con texto grande. La descripción completa sigue disponible al abrir el reporte.
- Categorías con imágenes originales, recorte `cover` conforme a sus slots, bordes suaves, rótulos y sombra. El conjunto tiene máximo 393 px para no producir tarjetas gigantes en horizontal/tablet.
- Historias abre un archivo real de reportes cargados; Adopta ya cambia al catálogo existente. Sin descargas adicionales para filtrar o abrir la categoría de historias.
- Casos cerrados, resueltos, cancelados o rechazados pasan al archivo; no se presentan bajo Casos activos.
- Login/registro con etiquetas fuera de los campos, confirmación local y botón de 200 px como máximo, adaptable al ancho disponible.
- Solicitud de adopción con página propia y banner original; conserva el mismo contrato, prevención de doble envío y estado incierto. Cancelar/enviar permanece fuera del scroll.
- Perfil consulta sus mascotas autorizadas una vez al entrar. No consulta fichas privadas desde bienvenida/login ni conserva resultados tras cambiar de cuenta.
- Confirmación de reporte con identidad y tipografía del prototipo; se conserva la clave anónima y su advertencia.
- Botones con superficie visual más baja y objetivo táctil acolchado; títulos secundarios y espacios menos dominantes. Modo de contraste/reducir transparencia conservado.

## Verificación y alcance

Las evidencias se guardan en `output/fidelidad-figma-2026-11-19/`, capturas 32 en adelante; pruebas y análisis en `output/adopcion-movil/`. El APK es de QA local, no una publicación de tienda. Los archivos de pruebas registran el resultado vigente; no se considera cerrado un cambio con pruebas fallidas.

Esta auditoría no certifica un calco completo ni convierte las áreas pendientes en funciones disponibles. Para cerrar fidelidad visual faltan, principalmente: foto de reporte, composición compacta del expediente, login con verificación real y recuperación, aviso de privacidad, y las pantallas operativas de mapa, tienda y apadrinamiento. Esas diferencias requieren trabajo de contrato/flujo además de estilos.

Orden de cierre: completar contratos y permisos de esas funciones; implementar composición de cada frame con sus recursos originales; probar éxito/vacío/error/permisos; contrastar capturas normales y al 200 % en Android; distribuir por bloques sin credenciales ni commits automáticos.


### Regresión posterior del perfil

Se verifican respuesta 403/reintento, custodia vigente y respuesta tardía tras logout. La prueba de reintento detectó un Future devuelto desde setState; corregido con asignación síncrona. Suite vigente: 126 pruebas y análisis limpio. No cambian el contrato ni la autorización del backend.
