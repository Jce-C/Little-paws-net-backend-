# 88. Formularios restantes y accesibilidad

Continuación local de Q01/Q02, 25 de noviembre de 2026. Se conserva el estado global **49/57 (86,0 %)**. La aceptación con TalkBack y teléfono físico sigue abierta.

## Recorrido cubierto

Se amplió la matriz a los ocho destinos pendientes del bloque 87: convocatoria de voluntariado, ayudas de organización, producto, pedido, aporte, foto de perfil, apadrinamiento y detalle de reporte. Las pantallas que no contienen campos de texto también reciben insets simulados para comprobar el comportamiento de la barra compartida; esto no significa que abran un teclado por sí solas.

Cada destino tiene tres escenarios: móvil estrecho 320×640 y texto al 200 %, horizontal 800×360 y tablet 800×1280 con texto al 200 %. Las acciones deben caber en la pantalla y situarse sobre el inset. Las comprobaciones de nombres accesibles, área táctil Android y contraste se ejecutan además en 393×852 con fuentes reales Inter y MaterialIcons, sobre los elementos expuestos en esa ventana. No certifican todos los estados o el contenido fuera de pantalla.

## Cambios reales

1. **Gestión de ayudas:** al recibir la organización, `_load` actualizaba `_loaded` sin reconstruir el padre. El cuerpo podía mostrarse mientras el pie Cancelar/Guardar seguía ausente, hasta otra interacción. Ahora la respuesta actualiza el estado y reconstruye las acciones. La regresión comprueba que aparecen sin escribir ni tocar el formulario.
2. **Producto:** el aviso sobre pagos y existencias usa un tono explícito de tinta de la paleta y peso medio, mejorando su contraste renderizado.
3. **Reporte:** el rótulo de fotografía ausente recibe el mismo tratamiento de legibilidad, conservando el fondo azul del proyecto.
4. **Operación con teclado:** se prueba que Tab llega a Aumentar cantidad y Espacio incrementa la cantidad sin enviar el pedido. No se cambian cantidades, permisos o datos automáticamente al abrir una pantalla.

El primer ensayo tuvo también un fallo en el cierre del manejador semántico de la propia prueba. Se corrigió con `try/finally`; ese fallo no justificaba rediseñar controles que ya cumplían el tamaño táctil.

## Pruebas y límites

`test/remaining_forms_accessibility_test.dart` incorpora **34 casos**: 24 de adaptación, ocho de semántica/área táctil/contraste y dos de interacción/carga. El cliente y las dos demos comparten esta prueba y los tres archivos de implementación modificados.

La prueba previa `help_management_test.dart` recorre ahora la lista antes de comprobar el ofrecimiento privado y regresa al campo antes de editar. Con el pie ya visible, la altura útil del cuerpo es menor y ese contenido puede construirse únicamente al desplazarse; no se agrandó artificialmente la pantalla ni se eliminó la comprobación de revocación.

Resultado final: **351 pruebas del cliente aprobadas, nueve optativas omitidas; 55 focales por demo; análisis limpio en las tres copias; Android debug y web release compilados**. La advertencia previa sobre CupertinoIcons permanece pendiente.

La evidencia y los registros finales están en `output/correcciones-app-2026-11-25/formularios-restantes`. No se vuelve a ejecutar el backend: estos cambios no alteran endpoints, permisos, consultas ni modelos, y conserva su evidencia previa de 468 pruebas. Las capturas nativas del bloque 87 siguen siendo evidencia de aquel recorrido; este bloque añade comprobaciones automatizadas, no una nueva aceptación en dispositivo.

Las pruebas emplean exclusivamente HTTP simulado y datos sintéticos. Cargar o inspeccionar las pantallas, cambiar cantidad y recorrer controles no envía una escritura de negocio.

## Continuación e integración

Siguiente: revisar etiquetas de campos y anuncios duplicados, errores de validación y acceso con teclado en estados posteriores a editar/guardar. Mantener abiertos los criterios integrales Q01/Q02 y las puertas de publicación Q10. No cerrar D02 ni inventar requisitos legales o de adjuntos.

Los paquetes nuevos de José, Sally y Majo se generan en `output/correcciones-app-2026-11-25/formularios-restantes/paquetes`, acumulando el estado local sobre la base Git indicada. Los anteriores conservan valor histórico y no se deben aplicar encima de estos. Sin commits, ramas, push, despliegue, cambios productivos ni servicios de pago.
