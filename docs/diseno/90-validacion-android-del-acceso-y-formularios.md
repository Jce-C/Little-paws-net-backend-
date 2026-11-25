# 90. Validación Android del acceso y formularios

25 de noviembre de 2026. Estado global **49/57 (86,0 %)**. Este bloque aporta aceptación nativa de recorridos concretos, no de todas las pantallas ni de TalkBack.

## Entorno

AVD Pixel_6a_2, Android 15/API 35, sesión de solo lectura y sin guardar snapshot. Se instaló exclusivamente la variante `net.littlepaws.little_paws_net.visualdemo`. Wi-Fi y datos deshabilitados; HTTP simulado y datos ficticios en memoria. No se utilizó la base productiva ni se procesaron pagos. Las capturas incluyen la banda de demo.

Las pruebas combinan pantalla real emulada, IME Android y jerarquía de accesibilidad nativa. Un XML vacío no se reutiliza como si fuera una captura nueva; los ensayos sin jerarquía válida se identifican en el índice de evidencia. UIAutomator no expone todos los atributos de Android (por ejemplo, hintText); un texto vacío en su XML no demuestra por sí solo que un campo carezca de nombre accesible.

## Problemas y correcciones

1. **Acceso horizontal con teclado alto:** el pie del login ocupaba la escasa altura y ocultaba los campos. Ahora usa `LpnKeyboardSafeArea`, igual que los demás formularios: conserva el pie encima del IME cuando hay espacio y lo oculta temporalmente cuando quedan menos de 180 píxeles lógicos. Cerrar el teclado restaura la acción sin borrar lo escrito.
2. **Teclado del acceso:** nombre y correo usan Siguiente; la contraseña del registro avanza a Confirmar contraseña mediante un foco explícito, sin detenerse en el icono de visibilidad. El correo también dirige explícitamente a Contraseña. La última acción conserva el envío existente con validación.
3. **Error de mascota corregido:** el aviso de Nombre permanecía hasta otro intento de guardar. Los campos de mascota revalidan su propia edición: al corregir Nombre desaparece únicamente ese aviso y permanece el de Especie. No se dispara un envío por escribir.

## Recorridos observados

- Login vacío: error de correo, foco en su campo, IME abierto y botón visible en vertical.
- Última compilación: correo sintético conservado; Siguiente enfoca la contraseña. La jerarquía nativa confirma `focused=true` y `password=true` en el control correspondiente.
- Girar el acceso con teclado: el pie deja espacio a la edición. La banda de demo consume altura adicional; en el caso extremo queda poco espacio. Esto no cierra la aceptación global de orientación.
- Acceso a la demo: se volvió a Inicio sin conectar un backend real.
- Mascota: desplazarse hasta fotografía y guardar con obligatorios vacíos vuelve a Nombre, enfoca y abre IME; no se registra la mascota.
- Corregir Nombre a `LunaQA`: queda un solo error, correspondiente a Especie, sin volver a guardar.
- Texto del sistema ampliado a 2,0: controles visibles, acciones reordenadas y borrador conservado. Android 15 aplica escalado no lineal; no se anuncia como duplicación exacta de cada glifo.
- Cancelar con borrador y texto ampliado: Seguir editando y Descartar son visibles. Se eligió Seguir editando; después de rotar, cerrar IME y volver a vertical se conserva `LunaQA`.
- No se observaron mensajes de RenderFlex overflow en el registro consultado durante estos recorridos. Esto no demuestra que nunca puedan aparecer en otras pantallas o dispositivos.

## Verificación automatizada

Se añadieron cuatro casos al archivo `keyboard_accessibility_test.dart`: login/registro con IME horizontal extremo y recuperación del pie; login/registro con Siguiente al campo correcto. La prueba previa de mascota comprueba ahora que corregir Nombre elimina ese error sin otro envío.

Resultado final: **363 pruebas del cliente aprobadas, nueve optativas omitidas; 29 focales por demo; análisis limpio en tres copias; APK debug y web release compilados**. Backend sin cambios: se reutiliza su evidencia previa de 468 pruebas. Persiste la advertencia anterior sobre CupertinoIcons.

## Evidencia, límites y continuación

Capturas PNG y jerarquías XML en `output/correcciones-app-2026-11-25/validacion-android`. El índice local distingue ensayos, fallos anteriores y capturas finales. Los archivos 29, 30 y 32–38 corresponden a los recorridos finales descritos. No se hizo una nueva escritura a un servidor real.

TalkBack está instalado en el AVD, pero no se declara aceptación auditiva: consultar su instalación o inspeccionar el árbol no equivale a escucharlo y probarlo. Permanecen pendientes la revisión con lector de pantalla y teléfono físico. Q01/Q02 siguen abiertos.

Siguiente: extender la comprobación nativa a reportes y solicitud de adopción; completar aceptación asistiva. Q03 y Q10 conservan carga/memoria/presupuesto y las puertas de publicación. S04/S05/S08/S12 mantienen D02 y revisión jurídica, sin inventar requisitos de documentos o datos personales.

Paquetes acumulados del equipo en `output/correcciones-app-2026-11-25/validacion-android/paquetes`. No aplicar encima de versiones previas. Todo local, sin commits, ramas, push, despliegue ni servicios de pago.
