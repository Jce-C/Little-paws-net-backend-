# Límite de rutas del cliente móvil

## Problema reproducido

El cliente comprobaba el prefijo de la cadena antes de resolverla como URL. Una ruta como `/api/../panel/` pasaba esa comprobación y terminaba consultando `/panel/` en el mismo servidor. Una prueba con MockClient reprodujo la salida del espacio `/api/`; no se enviaron credenciales reales ni se contactó un servidor externo.

No se detectó un flujo de la interfaz que construyera esa ruta. Se corrige la garantía interna del cliente para evitar que futuras rutas dinámicas dependan solo de un prefijo textual. Esto no demuestra una vulnerabilidad explotada en producción ni una evasión de permisos del backend.

## Corrección

Antes de construir la petición, `ApiClient` analiza la ruta, rechaza esquema o autoridad externos, fragmentos y separadores codificados dentro de un segmento. Después resuelve la URL y comprueba que conserva el origen del backend y el prefijo `/api/` de su ruta normalizada. Una ruta inválida produce ArgumentError antes de crear cabeceras o llamar al transporte.

La consulta se conserva: una búsqueda con tildes, `/`, `..`, `#` o `&` dentro del parámetro `q`, correctamente codificado mediante Uri, sigue funcionando. Se mantienen la prohibición de seguir redirecciones, el límite de respuesta y el plazo de cancelación.

## Verificación

Desde `frontend/mobile`:

```sh
flutter test test/api_path_boundary_test.dart test/api_redirect_boundary_test.dart test/api_response_budget_test.dart --reporter expanded
flutter test --reporter expanded
flutter analyze
flutter build apk --debug --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016
```

Se prueban nueve rutas rechazadas sin llamadas al transporte y una búsqueda permitida que preserva sus parámetros. Las 18 pruebas específicas incluyen también redirecciones, cancelación, presupuesto de respuesta y conservación de estados HTTP. `flutter-ruta-api-before-20261120.log` conserva la reproducción previa; los logs posteriores identifican la corrección.

No cambia la autorización del servidor ni el contenido accesible a cada cuenta. Las pruebas de ruta usan exclusivamente MockClient y credenciales sintéticas; las pruebas IO relacionadas usan loopback efímero. No hay Django, MySQL o Railway en este ensayo.

Se entrega un APK candidato separado. No se reemplazan las capturas nativas previas ni se publica una nueva demo desde esta tarea local. La comprobación nativa del candidato y los pendientes funcionales/visuales anteriores continúan registrados en Semana 15.

María José: cliente y pruebas Flutter; Sally: guía y evidencias; José Carlos: backend sin cambios.
