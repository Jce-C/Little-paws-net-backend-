# Medición HTTP local reproducible

19 de noviembre de 2026. Servidor QA ASGI de este proyecto en 127.0.0.1:8016, MySQL aislado, DEBUG activo, cinco fichas sintéticas publicables. No se consultó Railway ni se utilizaron credenciales o cuentas reales.

## Resultado observado

| Ruta | Mediana secuencial | p95 secuencial | p95 con cuatro clientes | Cuerpo sin compresión |
| --- | ---: | ---: | ---: | ---: |
| Catálogo | 29,08 ms | 35,48 ms | 62,35 ms | 521 bytes |
| Ficha | 27,77 ms | 34,53 ms | 54,59 ms | 282 bytes |
| Documento de login | 35,85 ms | 48,84 ms | 71,10 ms | 228.045 bytes |

Son veinte peticiones por ruta y modalidad, tras calentamiento. El p95 de una muestra tan pequeña es orientativo. La primera consulta registrada tampoco constituye una medición de arranque en frío: el servidor ya estaba ejecutándose.

No se midieron TLS, red móvil, latencia de Internet, Railway, renderizado, tiempo hasta interacción, subida de fotos ni cientos de usuarios. Estos números no prueban el tiempo de producción ni equivalen a una certificación de carga. El documento de login integra recursos para mantener una petición inicial; su tamaño se mide además del número de peticiones.

## Reproducción

1. Levantar exclusivamente el backend de aceptación con config.settings_qa y una base MySQL local propia que supere sus barreras. El puerto esperado es 8016. No redirigirlo a una base de producción.
2. Verificar que hay una ficha sintética publicable. El script no crea ni modifica mascotas y no autentica usuarios.
3. Desde la raíz del repositorio, ejecutar con Python: `python scripts/medir_rendimiento_local.py`.
4. El informe se guarda en output/rendimiento-local.json. No registrar ese resultado variable como una prueba universal de rendimiento.
5. Conservar condiciones del equipo, volumen de datos, versión y configuración al comparar muestras.

El script restringe el origen al servicio HTTP local y usa solo las rutas públicas de catálogo, ficha y login. Las aperturas del login pueden crear desafíos/sesiones exclusivamente en QA. No se cambia configuración de infraestructura.

## Cómo revisarlo en el navegador

Abrir herramientas de desarrollador → Network/Red. Limpiar el registro y recargar el login: debe aparecer el documento inicial, sin solicitudes adicionales mientras permanece abierto sin interacción. Para una operación, limpiar de nuevo, realizarla y abrir la petición: revisar Status, Size y Timing, separando Waiting/TTFB de descarga. Comparar con y sin caché y registrar si se aplicó limitación de red. Iniciar sesión y enviar formularios sí debe producir peticiones. No compartir HAR autenticados sin eliminar cookies, cabeceras, tokens y cuerpos privados.

## Pendiente antes de comercializar

Ensayar un entorno de preproducción autorizado con volumen representativo, múltiples perfiles, escrituras, imágenes, métricas p50/p95/p99 y errores, recursos de servidor y consultas SQL. Acordar el objetivo por operación antes de exigir un umbral universal. Evaluar equipos físicos modestos y redes reales sin sobrecargar producción.
