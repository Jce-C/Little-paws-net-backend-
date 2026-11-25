# Pedidos y compromisos de aporte: límites de sesión · 21 noviembre 2026

## Problema comprobado

Los formularios de pedido y aporte conservaban su estado mientras cambiaba la cuenta de Session. Eso dejaba una cantidad o un monto redactado por Ana en la pantalla usada después por Bea. Una confirmación anterior también podía seguir visible tras salir. La validación de generación del cliente ya impedía aceptar una respuesta tardía de otro inicio de sesión, pero el formulario conservaba el borrador y sus mensajes anteriores.

Seis regresiones reproducen el problema antes del cambio, con transporte MockClient y cuentas @example.invalid. No se procesó dinero ni se registraron pedidos/aportes reales. El contrato actual sigue representando pedidos e intención de aportar, sin pago.

## Solución

`SessionActionGate` separa la entrada autenticada de los dos formularios. Escucha Session y crea el formulario por identidad. Al salir desmonta tanto el borrador como la confirmación; al entrar con otra cuenta crea un estado nuevo. Cambiar solo nombre o teléfono de la misma cuenta conserva lo que estaba editando.

El catálogo, el detalle de producto y los fondos permanecen públicos. Para escribir un pedido o un compromiso se solicita sesión antes de mostrar el formulario editable. No se trasladan montos/cantidades redactados anónimamente a la siguiente cuenta. Tocar un control de un formulario que acaba de perder la sesión no abre otro acceso y no envía nada; la pantalla pasa al estado de entrada. Los botones conservan su posición visible y las reglas existentes de envío único y resultado incierto.

Se reutilizan Session.authorized y las APIs existentes. No se añaden permisos, modelos o rutas ni se modifica el backend. La revisión visual49 (acceso anterior y botón elevado) permanece vigente.

## Verificación

Seis pruebas nuevas, tres por formulario: confirmación y cierre de sesión; respuesta pendiente al cambiar de cuenta; conservación del borrador al editar el perfil y limpieza al cambiar de identidad. Las seis fallan antes del arreglo y pasan después. Pasan nueve pruebas focalizadas junto al flujo existente de envío único/sin pago, las171 de la suite Flutter y el análisis sin incidencias.

Evidencias: output/adopcion-movil/*formularios-sesion*20261121.log y validacion-formularios-sesion-20261121.json. El candidato Little-Paws-Formularios-Sesion-QA.apk usa únicamente la dirección de API local y se entrega con hash. No se instala en el emulador para conservar la demo visual abierta; no se reutilizan capturas viejas como evidencia de esta compilación. La demo alojada y su clon local permanecen sin cambios y sin publicación.

## Reparto y continuidad

Majo: gate de sesión, integración de formularios y seis regresiones; Sally: guía51, evidencia y continuidad; José Carlos: backend intacto. Paquetes locales actualizados y comprobados sin credenciales, commits, ramas, PR, tags, publicaciones o cambios en Railway.

Siguiente ejecución: continuar una auditoría puntual de estado privado y composición de mensajes, conservando la referencia49 y las barreras de generación. Firma, validación física/TalkBack y autorización de datos de negocio siguen siendo tareas distintas; las pruebas de widgets no las sustituyen.
