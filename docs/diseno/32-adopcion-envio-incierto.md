# Adopción móvil ante una respuesta perdida

## Problema real

Si el servidor creaba la solicitud pero su respuesta se perdía o llegaba tarde, el formulario mostraba un error genérico y volvía a habilitar Enviar solicitud. Esto podía llevar a otro POST innecesario y a la confusión de ver después una solicitud pendiente. El backend ya rechaza una segunda solicitud pendiente para la misma persona y mascota, pero eso no resolvía la experiencia del primer envío.

## Comportamiento

Ante timeout, respuesta 5xx o confirmación de éxito que el cliente no puede interpretar, el formulario explica que no se conoce el resultado. Mantiene la nota visible, bloquea su edición y reemplaza la acción principal por Ver mis solicitudes. Ese botón cierra el formulario y la ficha y lleva a la lista real mediante la navegación existente. No anuncia un envío exitoso ni repite el POST automáticamente. Cancelar sigue disponible.

Una denegación explícita o un error de validación no se convierte en éxito ni en una consulta implícita. En los errores corregibles permanece el formulario editable para corregir el dato. Durante un envío en curso se mantienen bloqueados el cierre y los botones; dos pulsaciones rápidas no generan dos peticiones.

Esta mejora no equivale a idempotencia global de todas las operaciones del sistema. Si el primer envío sigue procesándose, la consulta puede tardar en mostrarlo; la lista permite actualizar. El servidor conserva su transacción y la protección contra otra solicitud pendiente. No se crean solicitudes de prueba en producción.

## Verificación

Ocho regresiones en test/adoption_uncertain_test.dart comprueban timeout, 5xx, respuesta 201 malformada, rechazo 400 con corrección, doble pulsación y el recorrido completo catálogo → ficha → acceso → envío con respuesta perdida → solicitud pendiente recuperada. Se valida que la consulta de solicitudes ocurre solo al pulsar el botón y que hay un único POST en la recuperación. Son respuestas HTTP simuladas y cuentas sintéticas; no se interrumpe Railway ni se autentican cuentas reales.

Se comprueba además que recuperación y cancelación permanecen visibles a 320×640 y 800×360 con texto al 200 %. Se ejecuta también la suite Flutter completa, el análisis y la compilación del APK debug normal contra el backend local. El escenario de pérdida se comprueba con HTTP simulado; no se afirma haber provocado el fallo en producción ni en el APK normal. No cambian API, esquema, permisos ni auditoría del backend.

## Reparto

María José: estado del formulario, navegación y pruebas. Sally: guía y evidencias. José Carlos: conserva la API y sus pruebas de duplicado/auditoría previas, sin una migración nueva.
