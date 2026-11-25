# Respuestas JSON móviles acotadas y cancelación de transporte

## Hallazgo

ApiClient esperaba una respuesta de hasta quince segundos, pero utilizaba Response.fromStream sin un presupuesto de bytes. Un servidor mal configurado podía enviar un documento excesivo y agotar memoria antes de que los modelos validaran los datos. Future.timeout por sí solo tampoco enviaba una señal de cancelación al transporte.

## Cambio

El cliente acumula hasta 1 MiB de cuerpo recibido antes de decodificar JSON. Rechaza una longitud declarada superior y comprueba además cada bloque real, incluso sin Content-Length o con un valor inferior al cuerpo. Cancela la lectura al superar el presupuesto. No trunca el documento ni lo presenta como información válida parcial.

Se utiliza AbortableRequest de la dependencia http 1.6.0 ya fijada en pubspec.lock. El plazo normal sigue siendo quince segundos: al vencer se emite una señal de aborto al transporte compatible, en vez de limitarse a abandonar la espera. No se cierra el cliente completo ni se reenvía automáticamente la operación. La compatibilidad se revisó en el código local de http 1.6.0 (request.dart, abortable.dart e io_client.dart); los clientes personalizados pueden tener otras capacidades de cancelación.

Los códigos HTTP de error, incluidos 401, 403 y 429, se conservan si el documento excede el límite para no alterar renovación de sesión, denegación o control de intentos. Una respuesta 2xx excesiva queda sin confirmación válida; el flujo de adopción puede dirigir a consultar el resultado, como se documenta en la guía 32.

Abortar una conexión no demuestra que el servidor haya revertido una transacción. No se anuncia éxito o fallo de negocio a partir de ese hecho ni se repite un POST automáticamente. El plazo no es una medición de rendimiento ni se reduce para ocultar lentitud.

## Alcance

Se aplica a JSON de ApiClient. Las fotografías usan su componente y límites propios; esta revisión no cambia imágenes, CSS, API del servidor, permisos ni migraciones. Si un contrato legítimo necesita más datos, debe paginarse o revisarse explícitamente. El presupuesto limita la acumulación del cuerpo; no significa que todo el consumo de RAM de la app sea de 1 MiB.

## Pruebas

Diez regresiones verifican longitud declarada excesiva, longitud ausente o falsa, límite exacto con JSON válido, cancelación antes de cabeceras y durante lectura, reutilización del cliente, ausencia de reenvío, plazo inválido y conservación de estados HTTP. Un ensayo adicional dentro de esas diez pruebas usa el transporte IO predeterminado contra un HttpServer real de loopback: recibe parte del cuerpo, agota un plazo corto controlado y después consulta otra ruta con el mismo cliente. No usa Django, datos reales ni Railway.

La suite móvil completa comprueba que continúan funcionando catálogo, sesión, perfil, reportes, QR, fotos y adopciones. La compilación normal usa exclusivamente el backend QA local. Se conservan los límites de validación física/TalkBack, carga real, firma y publicación.

## Reparto

María José: lib/core/api_client.dart y test/api_response_budget_test.dart. Sally: guía y evidencias. José Carlos: revisión de contratos y futura paginación si hace falta; backend sin cambios en este bloque.
