# Descarte del compositor: ciclo de vida por identidad · 21 noviembre2026

## Fallo reproducido

Después del aislamiento de borradores de la guía53, el diálogo de descarte seguía viviendo en el Navigator raíz al salir o cambiar de cuenta. El formulario anterior ya se había desmontado, pero la ventana seguía encima del acceso o del compositor de la cuenta nueva. Eso dejaba una confirmación antigua bloqueando una sesión diferente.

Se añaden seis comprobaciones: cierre de sesión con diálogo abierto, cambio de cuenta conservando la ruta del nuevo compositor y edición del perfil de la misma identidad conservando diálogo/borrador. Se repiten para publicaciones/comentarios públicos e intereses de ayuda privados. Antes del arreglo fallan cuatro y pasan las dos de actualización del mismo perfil; después pasan las seis.

## Cambio acotado

El compositor guarda una referencia a su propio DialogRoute antes de abrirlo. Reutilizar esa referencia evita abrir confirmaciones duplicadas. Al desmontarse el formulario elimina únicamente esa ruta, después del frame para no modificar el Navigator durante la reconstrucción del árbol. No se usa un pop genérico que pudiera cerrar otra ruta de la cuenta nueva. Se conservan el tema, los textos, las acciones y la confirmación explícita para salir con borrador. Cancelar continúa editando.

No cambia los permisos, endpoints ni el backend. No se rehace el diseño o el documento Figma; el cambio es de ciclo de vida del diálogo existente. La guía52 sigue definiendo la apariencia y la54 el documento editable.

## Verificación

Quince pruebas focalizadas junto a comunidad,186 pruebas completas y análisis sin incidencias. Las pruebas nuevas usan MockClient e identidades sintéticas; no escriben en ninguna BD. La suite conserva sus pruebas previas de transporte en loopback. El harness aplica un frame después de redactar para que PopScope reciba el estado dirty antes de pulsar Atrás; el log definitivo antes/después usa ese harness corregido.

Se compila Little-Paws-Dialogo-Sesion-QA.apk con API local10.0.2.2:8016; no se instala. La demo visual, el emulador abierto y las publicaciones permanecen intactos. No se atribuyen a este APK capturas de versiones anteriores. Evidencia: *dialogo-sesion*20261121.log y validacion-dialogo-sesion-20261121.json, que registra el hash del APK y de las fuentes.

## Reparto y pendientes

Majo: propiedad de la ruta y seis pruebas. Sally: documentación y evidencia. José Carlos: sin cambios de backend. Paquetes separados, comprobados y sin secretos, commits, ramas, PR, tags o publicación.

Siguiente bloque: revisar con una reproducción acotada el diálogo de descarte del editor de perfil al salir/cambiar de cuenta; no se da por corregido por este cambio del compositor. Si se confirma el mismo patrón en varios formularios, evaluar una utilidad compartida con pruebas antes de sustituirlos. No rehacer la UI ni publicar desde la recurrencia. Firma de distribución, TalkBack/dispositivo físico, permisos/datos operativos consentidos y pruebas reales del piloto siguen siendo pasos distintos.
