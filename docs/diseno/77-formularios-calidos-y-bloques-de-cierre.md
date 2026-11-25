# Formularios cálidos y bloques de cierre

24 de noviembre de 2026. Fuente: texto adjunto c5bb7c3c-91ed-4062-9fa7-eedc153515ed y referencia visual de progreso/resumen. Complementa la guía 75 y el contrato de la 76. Aplica jerarquía, proximidad, claridad de controles y contraste de TypeUI y los 17 vídeos.

## Ajuste implementado

- Cinco etapas, mismas preguntas, valores, condiciones, validaciones, autorización y envío. No hay cambios de modelo, API, cifrado ni permisos.
- Color suave estable por grupo: azul, verde, amarillo, rosa y lila; panel de revisión reutiliza los cuatro grupos y sus iconos. Separadores delicados y título de sección reconocible.
- Progreso compacto con iconos, etapas anteriores marcadas y descripción semántica. Los indicadores no son pasos interactivos que permitan eludir validaciones.
- Opciones cortas, incluida vivienda y Sí/No, en botones al ancho de su contenido, con borde, icono y selección semántica. Las largas conservan desplegable de altura natural, mínimo 48; sin lista abierta para cada respuesta corta.
- Campos con etiquetas persistentes, márgenes menores y ancho de lectura limitado en pantallas grandes. No se comprimen áreas táctiles ni se fija altura que corte texto ampliado.
- Resumen por grupos, títulos e iconos, valores legibles y Editar; confirmaciones sin preselección y acciones fuera del scroll.
- Tema compartido: relleno horizontal de botones 18→12, radios 18→14; chips con esquinas de 12 en vez de cápsula completa, etiqueta más contenida; relleno vertical de campos 12→10. Se conserva mínimo táctil de 48. FormCard y LpnFormSection pasan de relleno 20 a 16 y radio 24 a 20; separación label/campo 8→6 y barra de acciones más compacta.
- No se rediseñan arbitrariamente login, navegación elevada ni componentes decorativos especializados. Sus estilos propios pueden prevalecer; su revisión total forma parte de Q01/Q07. La propagación del tema no equivale a inspección visual completa de todas las rutas.

## Trazabilidad y validación

Implementación: `design/adoption_form_style.dart`, `adoption/questionnaire_screen.dart`, `design/lpn_theme.dart`, `design/form_surfaces.dart`, `design/refined_surfaces.dart` del cliente canónico. Copias locales sincronizadas en demo Android y demo web; sin publicación.

Se mantienen pruebas del recorrido, valores condicionales eliminados, envío único, cancelación, respuesta incierta, cierre/cambio de sesión y recorridos a 320 px con texto al 200 %. La prueba de contraste incorpora los cinco nuevos fondos y exige 4,5:1 para textos ink/muted/sage. No se añaden dependencias, imágenes, peticiones ni servicios de pago.

Capturas de las cinco etapas: `output/correcciones-app-2026-11-24/formulario-visual` del workspace, junto con logs y mosaico. Son renderizados Flutter con datos ficticios, no capturas físicas ni certificación de producción.

## Bloques reformulados para continuar

1. **Refinamiento del formulario de adopción y densidad compartida:** implementación descrita arriba. Mantener abiertos adjuntos privados/D02, datos sensibles de terceros, condiciones jurídicas y deprecación del endpoint anterior.
2. **Detalle y edición de reportes:** R01/R02/R08. Jerarquizar estado, situación, fotos y ubicación; comprobar titularidad/clave, edición real, cancelación y respuesta perdida. Revisar la densidad de sus controles personalizados al mismo tiempo.
3. **Creación de reportes:** R09/R10. Flujo por temas, datos/foto preservados, controles condicionales y un solo envío; sin duplicación ni scroll anidado.
4. **Pantallas restantes:** O01-O06, C03 y base visual V01-V04/V06-V08. Notificaciones, solicitudes, cuenta, mascotas, ayudas y rutas restantes; registrar componentes personalizados que no heredan el tema para ajustarlos uno a uno.
5. **Integración transversal:** Q01-Q08. Recorrido real y dos sesiones/RBAC, accesibilidad, todos los estados, teléfono físico, métricas de red/SQL/memoria y comparación de capturas; no cerrar por mocks.
6. **Paquetes y publicación responsable:** Q09/Q10. Separación para los tres integrantes; privacidad/licencias/retención/exportación/borrado, respaldo/restauración, seguridad y security-audit por identificar, firma Android y presupuesto medido gratuito/VPS. Sin commits/despliegues automáticos.

El refinamiento actual no añade diez puntos funcionales ni cierra Q globales: se mantiene 24/57 (42,1 %) de la guía 75. Los bloques son agrupaciones operativas, no otro porcentaje ni una afirmación de producto terminado. Siguiente ejecución: bloque 2.


## Pruebas del refinamiento

- Cliente canónico: 268 pruebas aprobadas, 5 optativas omitidas. Ocho pruebas específicas del formulario ejecutadas adicionalmente con capturas de cinco etapas; incluyen todo el recorrido a 320 px y texto al 200 %.
- Demo Android local: 342 pruebas aprobadas, 4 visuales optativas omitidas. Demo web local: 10 focales aprobadas (cuestionario, evaluación simulada y contraste).
- Análisis estático sin observaciones en las tres copias. Evidencia de regresión y análisis en la carpeta `formulario-visual`.
- No se repite la prueba MySQL por modificar únicamente presentación; sigue vigente la evidencia funcional de la guía 76. Las pruebas del cliente comprueban el contrato y un envío final, no sustituyen la aceptación física ni una medición de producción.


Compilaciones finales: APK Android debug y demo web release correctas, solo locales. La compilación web conserva el aviso previo de la familia CupertinoIcons no empaquetada, ya registrado en la guía 76; no es un error del análisis estático ni se da por resuelta su auditoría. El enlace publicado no cambia.
