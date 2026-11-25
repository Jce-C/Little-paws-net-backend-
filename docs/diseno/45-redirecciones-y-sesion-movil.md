# Redirecciones HTTP y límites de sesión móvil

Se verifica el transporte real de `package:http` utilizado por `ApiClient`, además de las respuestas simuladas. Una respuesta 302, 307 o 308 debe terminar como error controlado; no debe enviar la credencial de sesión a otro destino ni repetir una solicitud de adopción.

## Ensayo reproducible

Desde `frontend/mobile`:

```sh
flutter test test/api_redirect_boundary_test.dart --reporter expanded
flutter test --reporter expanded
flutter analyze
```

Cada uno de los seis escenarios crea dos servidores efímeros en loopback: el primero responde con la redirección y el segundo cuenta accesos inesperados. Se prueban GET y POST para cada código. La credencial y la mascota del cuerpo son valores sintéticos. No hay conexiones con Django, MySQL ni Railway.

Se comprueba que el primer servidor recibe una sola operación, el destino no recibe ninguna y el cliente comunica el código de respuesta original. Después, una consulta explícita al primer servidor debe funcionar: rechazar la redirección no inutiliza el cliente ni reenvía la operación previa.

El cliente existente ya fija `followRedirects = false`; las pruebas confirman ese comportamiento con sockets reales. No fue necesario modificar el código de ejecución, permisos o API. Una redirección accidental del servidor requerirá corregir la URL o el despliegue; no se debe habilitar su seguimiento indiscriminado para ocultarla.

## Alcance

Esto verifica el transporte IO de escritorio utilizado en las pruebas Flutter, no una captura de red en Android físico ni el transporte Fetch del navegador. No certifica TLS, proxies de red o rendimiento de producción. La demo web independiente utiliza datos ficticios y no sustituye esta integración.

Se mantienen APK y capturas anteriores porque el binario no cambia. Los logs de este ensayo identifican la suite de fuentes posterior; no representan una recompilación ni nuevas capturas.

María José: regresiones Flutter; Sally: documentación y evidencias. José Carlos: backend sin cambios. Pendientes de validación física, TalkBack, firma y contratos de negocio previamente identificados se conservan.
