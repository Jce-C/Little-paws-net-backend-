# V02 — Etiquetas persistentes del acceso

Cierre local: 25 de noviembre de 2026. Se aplicaron TypeUI y los criterios de etiquetas, escala, proximidad y feedback de la guía de 17 vídeos. No se cambió la fotografía, la paleta, la marca, el backend ni la API de autenticación.

## Cambio e integración

`auth/account_screen.dart` mantiene visibles Nombre completo, Correo electrónico, Contraseña y Confirmar contraseña después de escribir, enfocar y salir del campo. Se sustituyeron las pistas que desaparecían por etiquetas nativas de InputDecoration. El nombre completo sigue siendo un único campo; no se altera su contrato ni la validación del servidor.

En tamaño normal se conserva la cápsula, con una etiqueta flotante legible sobre el fondo de la referencia. Con texto ampliado, las etiquetas se muestran encima de su cápsula y pueden ocupar más de una línea. El texto del campo conserva la escala del usuario. No se utilizan puntos suspensivos ni se reduce globalmente la escala para acomodarlas.

`design/access_reference.dart` conserva el nombre completo de la etiqueta en el control editable nativo, aunque su copia visual dentro de la cápsula se oculta en el modo ampliado. El rótulo exterior se excluye de semántica para no anunciarlo dos veces. Las pruebas comprueban que el nodo nombrado sigue siendo un campo editable, no solo un texto decorativo; el botón para mostrar/ocultar contraseña permanece separado. No se reemplaza el control nativo por una imitación de texto.

La prueba con teclado detectó que el pie del acceso quedaba bajo el área ocupada por el teclado. Ahora el botón Ingresar/Crear cuenta incorpora el inset inferior y se mantiene encima; el formulario conserva su scroll. El teclado de las capturas es una región simulada, no un teclado Android real. No se afirma aceptación con TalkBack ni teclado físico por esta prueba.

## Trazabilidad

| Necesidad | Ruta/componente | Verificación |
|---|---|---|
| V02: etiquetas persistentes | `auth/account_screen.dart` | Acceso y registro vacíos/llenos, foco y desenfoque |
| V02: tipografía ampliada | `design/access_reference.dart`, rótulo exterior adaptable | 393×852 normal y 320×640 al 200 %, texto completo sin solaparse con el valor |
| Nombre accesible | InputDecoration y Semantics nativos | Nombre completo del campo y flag de campo editable conservados |
| Acción con teclado | pie compacto del LoginScreen | Extremo inferior del botón <= 440 px en pantalla de 640 con inset de 200 px |
| Consumo | sesión/API existente | Cero llamadas de negocio mientras se completa el formulario sin enviar |
| Lectura | paleta de acceso existente | Etiqueta/fondo y texto de entrada/fondo alcanzan 4,5:1 en la comprobación automática |

## Resultados

- 308 pruebas integrales del cliente aprobadas; nueve optativas de integración/captura omitidas en la ejecución predeterminada.
- Veinte focales del acceso y adaptación aprobadas; incluyen cinco nuevas pruebas de etiquetas, semántica, contraste, escala y teclado.
- Catorce focales aprobadas en cada demo local y web. Los dos archivos de implementación y el test nuevo coinciden byte a byte en las tres copias.
- Análisis sin observaciones en cliente, demo y web; APK debug y web release compilados. Se conserva la advertencia previa de CupertinoIcons para su auditoría global.
- Backend sin cambios: se reutilizan las 468 pruebas aprobadas del cierre anterior. No se volvió a escribir una base ni a repetir la batería Django por un cambio exclusivamente Flutter.

Evidencia: `output/correcciones-app-2026-11-25/etiquetas-acceso`. Las capturas finales tienen prefijos `normal-`, `texto-200-` y `teclado-`; otros archivos corresponden a ensayos intermedios y no se presentan como versión final. `mosaico-etiquetas.png` reúne seis capturas representativas. `docs/evidencias/2026-11-25/v02-etiquetas.json` conserva el resumen sanitizado.

Los paquetes actualizados se encuentran en la subcarpeta `paquetes` de esa evidencia. Reemplazan como versión de trabajo a los del cierre 83-85; se reconstruyen sobre la misma base Git y mantienen el reparto José/backend, Sally/app y Majo/diseño/documentación. No se deben aplicar sobre cambios locales sin revisar primero la base y el parche.

## Estado siguiente

V02 cerrado: **49/57 (86,0 %)**, conteo simple de la guía 75. La próxima ejecución comprueba el cierre solo si hay cambios o evidencias pendientes y retoma Q01/Q02 en lo que pueda automatizarse: orientación, tamaños, foco y adaptación. Los adjuntos y datos sensibles S04/S05/S08/S12 mantienen sus dependencias D02/jurídicas. Q03 y Q10 siguen abiertos para carga/memoria representativas y puertas de publicación.

No hay commits, ramas, publicación, cargos ni cambios productivos. Este avance no convierte la app en un producto comercial ya validado.
