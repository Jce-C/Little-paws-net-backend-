# Bloque 2 — Integración real, RBAC y consumo observado

Fecha: 25 de noviembre de 2026. Solo ASGI/HTTP en loopback y MySQL aislado, con cuentas `.invalid` y datos sintéticos. Servidor QA detenido al terminar. Sin despliegue ni servicios de pago.

## Comunidad y tienda

Se comprobó por HTTP la publicación, comentario, reacción repetida sin duplicar el contador, retirada de la reacción y de la publicación propia. Una cuenta distinta no puede retirar el mensaje ajeno; después de retirar, deja de estar en el feed. El cliente conserva pruebas de paginación, errores, respuesta incierta sin reenvío automático, permisos y contadores provenientes del servidor.

En tienda se inició un pedido, se consultó como titular y se rechazó la consulta de otra cuenta. El precio de referencia quedó conservado y `cobrado=false`. No se simuló una pasarela de pago ni una reserva de stock.

## Dos sesiones simultáneas y RBAC

Dos sesiones web autenticadas mantuvieron abiertas sus conexiones SSE con Uvicorn/ASGI. Mediante una tercera cuenta de gestión se concedió `usuarios.ver` a Ciudadano, se verificó el acceso con los tokens ya emitidos y se cambió el nombre del recurso. `/panel/estado/` reflejó el nombre nuevo. Después se retiró el permiso y ambas cuentas recibieron 403 sin renovar el login; el módulo desapareció del estado de navegación.

Ambas conexiones recibieron los eventos de revisión: aproximadamente 937 ms al conceder y 850 ms al revocar, en esta muestra local. El hub conserva un lector de revisión por proceso conectado, no una consulta por cada cliente SSE. Estas cifras no son un SLA ni una garantía de latencia en otro servidor.

La validación verifica transporte y estado de menú del servidor, además de las operaciones. La aceptación manual del renderizado en navegadores/dispositivos, el foco y el lector de pantalla siguen en Q01/Q02. La app comprueba los permisos en cada operación; no se afirma que todas las pantallas móviles mantengan SSE en segundo plano ni que los datos privados se sincronicen mediante sondeo.

## Regresión integral

**468 pruebas backend aprobadas** en MySQL aislado. Incluyen autorización, revocaciones, varias organizaciones, excepciones, auditoría, reintentos, APIs móviles, admin Django, tienda y recorridos HTTP.

La ampliación de pruebas detectó y corrigió:

1. `verify_demo` intentaba solicitar una mascota demo que ya tenía una solicitud pendiente. Ahora crea una mascota disponible controlada, dentro de la transacción reversible, conservando las reglas públicas de disponibilidad.
2. Una prueba del dashboard esperaba el carrusel de métricas retirado. Ahora verifica la cuadrícula visible y su número real de indicadores.
3. La prueba de tienda suponía cero pedidos en toda la base. Ahora comprueba que un intento inválido no cambia el número de pedidos existente.

El verificador de demo pasó con rollback; no se rebajaron las reglas de adopción para hacer pasar la prueba.

## Consumo medido y límites

Se conservan peticiones, códigos, bytes y tiempos en `docs/evidencias/2026-11-25/http-mediciones.json`, sin credenciales ni tokens. Cinco lecturas HTTP locales del catálogo móvil: mediana 29 ms, máximo 32,3 ms, respuesta sintética de 251 bytes. Tienda: mediana 21,93 ms; directorio: 17,61 ms. Login del panel: documento de aproximadamente 232 KB y mediana de 43,36 ms. Los volúmenes de muestra son pequeños; no representan una carga de usuarios real.

Se midieron seis rutas con SQL y asignaciones Python: acceso, catálogo móvil, comunidad, directorio, tienda y mascotas propias. Al pasar de uno a 21 productos, el catálogo conservó una consulta SQL. Los recursos gráficos empaquetados de la app suman 737398 bytes; fuentes, motor Flutter, compilados y recursos del panel se contabilizan aparte. No se equipara el total de imágenes con la descarga inicial ni con el coste mensual.

Los tiempos con `tracemalloc` incluyen instrumentación; su pico es de asignaciones Python por petición, no RSS ni memoria de Android/browser. Las pruebas del cliente comprueban que reconstruir/cargar un estado no crea bucles y que el acceso en reposo no añade llamadas de negocio.

**Q03 permanece abierto:** faltan cargas representativas, memoria/perfilado de la app en dispositivo, redes móviles y presupuesto con métricas del alojamiento elegido. Estas mediciones sirven de base y no permiten prometer coste cero o miles de usuarios simultáneos.

## Trazabilidad

| ID | Ruta/componente | Permiso/garantía | Prueba/evidencia |
|---|---|---|---|
| C03 | comunidad y `community_screen.dart` | `comunidad.participar`, propiedad y moderación | `core.tests_community`, `community_test.dart`, HTTP ASGI |
| Q04 | matriz, recursos, `/panel/estado/`, `/panel/eventos/` | permiso en cada operación, alcance, revisión y dos sesiones | `tests_rbac_dinamico`, `tests_roles_abiertos`, `commerce.tests_acceptance_http`, eventos reales |
| Q05 | app/demos/backend | fixtures diferenciados; persistencia MySQL real | pruebas 76-82, HTTP actual y evidencia sanitizada |
| O06 | expediente/QR/solicitud compatible | cambio de generación de sesión y borrador | `medical_session_boundaries`, `pet_qr`, `legacy_request_boundaries` |
| Q03 parcial | APIs y recursos | consumo observado y comparación de consultas | `sql-memoria-recursos.json`, `http-mediciones.json` |

Se cierran C03, Q04 y Q05: **44/57 (77,2 %)** de la lista. No se habilitan adjuntos sensibles, pagos ni producción por este cierre.
