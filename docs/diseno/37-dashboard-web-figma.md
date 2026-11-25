# Dashboard web: jerarquía y tarjetas del Figma

Referencias: [encabezado 9:124](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR/Untitled?node-id=9-124) y [resumen 9:129](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR/Untitled?node-id=9-129). Se revisaron su contexto detallado y capturas antes de implementar.

## Qué cambió

El panel web recupera Inter, la fuente de ese Figma, mientras Android y el login conservan JetBrains Mono de sus propias referencias. La marca mantiene Leckerli One y el nombre completo solicitado. No se vuelve al nombre cortado ni a la cabecera alta del boceto antiguo.

El saludo usa 32 px, peso ligero y espaciado medido. Las tarjetas recuperan fondo crema opaco, borde cálido, radio de 24 px y sombra del resumen. El valor aparece antes de su etiqueta, también en el DOM; no se reordena con CSS. Los valores y enlaces siguen proviniendo del contexto autorizado. Cada enlace tiene un nombre accesible con cantidad, indicador y acción traducida.

Se sustituye el carrusel de indicadores por una cuadrícula adaptable. A 1366 px los cinco indicadores del administrador QA se muestran juntos, sin flechas ni puntos ni desplazamiento horizontal. En móvil se apilan y se permite el scroll vertical normal. Los títulos largos aumentan la altura de la tarjeta; no se fijan 116 px si eso recortaría datos. Las secciones de accesos y actividad usan superficie clara, bordes y sombras más suaves, separadas del resumen por 24 px.

La cuadrícula responde al espacio disponible y las columnas de detalle también al contenedor; el CSS anterior conserva la alternativa por viewport. Se mantiene una base sólida en colores forzados y contraste reforzado. El tema oscuro utiliza sus superficies propias.

No se recuperan las tarjetas del prototipo que duplicaban el menú, sus números ilustrativos ni la banda de marketing: se conservan los indicadores reales y el resumen de permisos pedidos después por el usuario. No cambian autorización, consultas, contadores, nombres configurables ni sincronización. La cabecera sigue fija y la navegación plegable.

## Evidencia verificable

- 29 regresiones Django aprobadas en un esquema MySQL de pruebas nuevo, local y aislado; se destruye al finalizar. Cubren relación contador/listado, traducción, navegación configurable y RBAC dinámico. No se repite ni se presenta como nueva la suite histórica de 323.
- Ensayo de navegador con administrador y ciudadana sintéticos: 320, 390, 768, 1366 y 2560 px sin desbordamiento del documento ni de la cuadrícula.
- Texto al 200 % sin pérdida de indicadores; cabecera visible tras scroll; plegar/expandir el menú conserva su estado accesible.
- Axe no detecta infracciones del conjunto probado en ambos dashboards, claro/oscuro, ni en la matriz en inglés. Esto no sustituye revisión manual con lector de pantalla ni certifica toda la aplicación.
- Matriz en inglés revisada a 320, 768 y 1366 px; enlaces de indicadores traducidos. Cero errores JavaScript en las páginas supervisadas.
- Login: una petición inicial del documento y ninguna adicional durante la espera comprobada. No se han añadido fuentes o imágenes externas al login.
- 26 resultados de comprobación en validacion-dashboard-figma-20261119.json, más log de navegador y backend-dashboard-figma-20261119.log en output/adopcion-movil.
- Capturas 21–27 en output/fidelidad-figma-2026-11-19. La referencia anterior se recuperó usando el CSS guardado y el HTML anterior en caché, sin revertir archivos actuales. Las capturas adaptables esperan que termine la transición de la navegación para no registrar posiciones intermedias.

El servidor ASGI local se reinició tras verificar el proceso de este ensayo para invalidar plantillas en caché; no se migró, sembró ni cambió ningún rol. Solo se renovaron sesiones de las cuentas sintéticas del QA, sin utilizar cuentas reales. No hubo cambios en Railway.

## Entrega separada

Sally recibe materiales.css completo e inicio.html completo, con documentación y evidencias, en el módulo 03. Copiar ambos: entregar solo el CSS dejaría el HTML antiguo del carrusel. Los parches de módulos anteriores siguen comprobándose en su contexto. No hay commits ni publicación.

José Carlos conserva backend y permisos; María José conserva Android. El APK y sus 115 pruebas corresponden al bloque móvil anterior; no se recompila Flutter por cambios exclusivamente web.

Pendiente: continuar comparación de listados/formularios y estados, hacer más claras las descripciones de acciones nuevas en actividad/auditoría y revisar rescates móvil. La revisión no declara una copia global de todas las pantallas ni un producto comercial terminado.
