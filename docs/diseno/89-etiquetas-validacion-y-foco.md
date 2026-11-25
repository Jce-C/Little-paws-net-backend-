# 89. Etiquetas, validación y foco

Bloque local del 25 de noviembre de 2026. Continúa Q01/Q02; **49/57 (86,0 %)**, sin cerrar aceptación integral ni publicación.

## Problemas comprobados

- El rótulo exterior de `LpnFieldLabel` se anunciaba dos veces: como texto independiente y como nombre del control. La prueba del árbol semántico reproducía dos nodos con «Ciudad».
- Validar desde el pie podía dejar los errores lejos del punto visible o mantener el foco en Guardar/Continuar.
- En el registro de mascota, desplazarse hasta la fotografía desmontaba los campos iniciales de una lista perezosa. Estos dejaban de participar en la validación local; una prueba reprodujo un intento HTTP con los obligatorios vacíos. Se empleó un cliente simulado: no hubo escritura real ni se afirma que el backend aceptara esos datos.

## Implementación

`LpnFieldLabel` conserva el rótulo visual, lo excluye de su anuncio independiente y asocia un solo nombre al control. No se fusionan los botones de opciones en una acción: conservan sus etiquetas y selección individual.

`validateLpnForm` ejecuta la validación y, cuando falla, espera al siguiente frame para enfocar y revelar el primer control inválido. Funciona con texto, selectores y grupos de opciones. Si el formulario desapareció, no toca controles destruidos. Respeta la reducción de movimiento y conserva las respuestas válidas.

Se utiliza en acceso/registro, perfil, solicitud de adopción, registro de mascota, convocatoria de ayuda, reporte de animal, gestión de reporte anónimo y el formulario de moderación de comunidad. No se envían datos al fallar la validación ni se modifican reglas de autorización.

`LpnFormScrollView` mantiene montados los campos de formularios acotados: mascota, cuestionario de adopción, convocatoria, asistente de reporte, perfil y gestión anónima. Así participan en la validación aunque estén fuera de pantalla. Conserva un solo desplazamiento y los controladores existentes. Los catálogos y listas de registros siguen usando listas perezosas. La convocatoria conserva sus límites de ocho actividades y cuatro canales; no se sustituye una lista ilimitada por una columna ilimitada.

## Evidencia

Ocho pruebas nuevas en `test/field_labels_validation_test.dart`:

1. Salir antes de la recuperación del foco sin acceder a controles destruidos.
2. Intentar registrar una mascota desde el final: cero escrituras, errores visibles y foco en Nombre.
3. Nombre accesible único del texto después de escribir.
4. Opciones separadas con selección conservada.
5. Nombre accesible del selector sin repetición.
6. Texto inválido: desplazamiento, foco, corrección y datos previos conservados.
7. Selector inválido: foco, selección y recuperación.
8. Grupo de opciones inválido: foco, teclado y recuperación.

La suite completa y las focales de las demos incluyen los recorridos previos de reportes, solicitudes, cancelación, perfiles y recuperación de conflictos. Registros en `output/correcciones-app-2026-11-25/etiquetas-validacion`. HTTP simulado; no se utiliza una base productiva. Backend sin cambios: se conserva su evidencia previa de 468 pruebas.

Resultado: **359 pruebas aprobadas y nueve optativas omitidas en cliente; 63 focales por demo; análisis limpio en tres copias; Android debug y web release compilados**. Persiste la advertencia previa de CupertinoIcons. Tras la suite completa se sustituyó únicamente una API obsoleta de inspección semántica dentro de la prueba, y sus ocho casos se volvieron a ejecutar.

El árbol semántico de Flutter no sustituye una prueba auditiva en TalkBack. Tampoco se declara aceptación de todos los dispositivos por superar pruebas de widgets. Q01/Q02 permanecen abiertos.

## Continuación

Comprobar en Android nativo el recorrido de error → foco → teclado → corrección, incluidos texto ampliado y orientación; continuar la aceptación asistiva. Mantener S04/S05/S08/S12 y D02 sin inventar decisiones jurídicas o hacer obligatorios documentos. Q03 mantiene carga/memoria/presupuesto; Q10 conserva las puertas de publicación.

Paquetes del equipo en `output/correcciones-app-2026-11-25/etiquetas-validacion/paquetes`: cambios locales acumulados por responsable sobre la base indicada, con reconstrucción verificada antes de preparar commits. No superponer con versiones anteriores. Sin commits, ramas, push, despliegue ni servicios de pago.
