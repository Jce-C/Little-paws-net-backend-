# Reportes públicos: contrato paginado y búsqueda del servidor

Estado: API e integración Android locales implementadas el 20 de noviembre de 2026. Rescates e Historias consumen páginas de 20 y ofrecen continuación explícita; la búsqueda se realiza en el servidor. Se conserva compatibilidad con la ruta legacy para clientes anteriores.

## Problema y cambio

La lista pública anterior devuelve como máximo 100 reportes. Buscar únicamente en esa descarga puede decir que no hay resultados aunque exista una coincidencia más antigua. Descargar todos los reportes en una petición tampoco es adecuado para una comunidad grande.

`GET /api/reportes/publicos/` entrega hasta 20 filas y un cursor para continuar, sin contar ni descargar toda la tabla. La búsqueda se aplica antes de limitar la página. Comparte la regla de ocultación con el endpoint anterior, cuya respuesta continúa siendo una lista de hasta 100 elementos.

## Uso del contrato

1. Solicitar `/api/reportes/publicos/` para la primera página.
2. Leer `results`. Cada fila contiene exclusivamente `id_reporte`, `descripcion`, `tipo_reporte__nombre` y `estado_reporte__nombre`.
3. Si `next_cursor` no es nulo, solicitar `/api/reportes/publicos/?antes=CURSOR`.
4. Para buscar, enviar `buscar=texto` desde la primera página. Conservar el mismo texto en las páginas siguientes; cambiarlo requiere reiniciar el cursor.
5. Al actualizar la lista, empezar otra vez sin cursor.

Ejemplo de estructura, sin representar animales ni historias reales:

```json
{"results": [], "next_cursor": null}
```

No se añaden contactos, direcciones, identidades de reportantes, claves anónimas, fotografías ni coordenadas a la información pública existente. El servicio es de lectura; POST devuelve 405. Los procesos de creación, corrección, moderación y cierre conservan sus permisos y rutas.

## Límites y comportamiento

- `buscar`: máximo 100 caracteres; filtra descripción, tipo y estado. No es búsqueda geográfica ni un motor de relevancia.
- `antes`: identificador positivo decimal ASCII, con longitud/rango acotados; los parámetros inválidos devuelven 400.
- Orden descendente por identificador. Las nuevas publicaciones se ven al actualizar la primera página y no se insertan en medio del recorrido.
- La ocultación se vuelve a comprobar en cada consulta. Una página ya entregada no se puede retirar de la memoria del cliente mediante este endpoint; la sincronización en vivo de publicaciones sigue pendiente.
- Es paginación sobre datos actuales, no una instantánea transaccional. Las modificaciones concurrentes de descripciones/estados pueden cambiar coincidencias.
- Lectura anónima: presupuesto independiente de 60 peticiones/minuto por dirección IP. Paginar no consume las 20 peticiones/hora del scope anónimo general usado por otras rutas. No se modifican sus límites.
- Se prueban páginas de 20 mediante una consulta SQL de lectura. Esto no equivale a una medición de latencia de producción.
- La búsqueda `icontains` puede recorrer muchas filas; índices de búsqueda especializada y ensayos de carga siguen pendientes antes de escala comercial.

## Verificación y reproducción

Con las variables de la instancia MySQL aislada configuradas, ejecutar desde `backend-panel`:

```powershell
python manage.py test rescue.tests_public_reports rescue.tests_mobile seguridad.tests_flujos.FlujosTests.test_reporte_oculto_correccion_aprobada_no_republica seguridad.tests_flujos.FlujosTests.test_reporte_pendiente_solo_propietario_edita_y_cierra --settings=config.settings_test_mysql --noinput -v 2
```

`settings_test_mysql` exige host local y puerto distinto del habitual. No utilizar las variables de Railway. El ensayo crea y destruye `test_lpn_rbac_sandbox`; no reutiliza la base de la aplicación.

Pasan 17 pruebas: siete de paginación/visibilidad/privacidad/coste de consulta/presupuesto de lectura, ocho de reporte móvil y dos de moderación y titularidad de edición. Se recorren 105 reportes sintéticos sin duplicados, se encuentra una coincidencia anterior a los 100 recientes y se prueba una ocultación entre páginas. Log: `output/adopcion-movil/backend-reportes-paginados-20261120.log`.

## Integración Android

PublicReportsController consume el contrato con carga por página y descarte de respuestas de consultas anteriores. La búsqueda espera 400 ms tras la última edición y reinicia el cursor; se ocultan resultados de la consulta previa mientras espera. Cargar más bloquea clics duplicados, elimina IDs repetidos y conserva las filas anteriores si una página falla. El reintento es explícito. Se rechazan cursores inválidos/no progresivos y sobres de más de 20 filas. No se realizan envíos de negocio.

Rescates conserva los casos activos y sus tarjetas; si una página solo contiene casos cerrados y aún hay cursor, explica que se puede continuar. Historias comparte la consulta y los datos ya descargados, muestra los casos archivados y permite cargar más sin una descarga adicional al abrir. Si existe búsqueda, indica su texto; editarla se hace al volver al buscador del banner. Es una limitación de interacción documentada, no un segundo buscador ficticio.

No hacen falta migraciones ni cambios de permisos. Para consumir la API nueva se necesita el APK actualizado; debe integrarse la parte de backend primero. No hay fallback silencioso al límite de 100 si se utiliza un servidor antiguo. No se modificó el diseño tras revisar la referencia de expediente de Figma: sus datos de ejemplo, carnet y QR no sustituyen registros clínicos autorizados.

## Reparto

- José Carlos: `rescue/public_reports.py`, vista/ruta, regresiones y parche `01-reportes-publicos-paginados.patch` que reutiliza el selector en la ruta anterior.
- María José: parser, controlador, pantallas de Rescates/Historias, regresiones y APK actualizado.
- Sally: guía, alcance y evidencias del ensayo.

Todo permanece local, sin commits ni despliegue.


### Verificación Android

Pasan 138 pruebas Flutter y el análisis está limpio. Siete regresiones nuevas comprueban temporización, respuestas fuera de orden, recuperación de páginas, cursores, doble clic, búsqueda durante otra página, sobres inválidos y continuación de casos archivados. Las pruebas anteriores de búsqueda se adaptan al contrato de servidor; ya no afirman que toda búsqueda sea local o que limpiar no consulte la red. Logs `flutter-reportes-paginados-20261120.log`, `analyze-reportes-paginados-20261120.log` y `build-reportes-paginados-20261120.log`.


### Recorrido nativo reproducible

Con el backend QA y el APK identificados, abrir Rescates, buscar una descripción sintética conocida y comprobar que coincide con la API. Limpiar, pulsar Cargar más y abrir Historias; buscar una fila de la segunda página. No enviar formularios ni emitir QR. El ensayo guardó dos capturas nativas y validacion.json con SHA-256 en output/reportes-paginados-2026-11-20. El mosaico tiene 25 capturas nuevas del APK actual y la sesión sintética se cerró al terminar.

Para repetir las regresiones sin conexiones externas: `flutter test test/public_reports_pagination_test.dart`; suite completa: `flutter test`. La caché de throttling de Django debe ser compartida al ejecutar varias instancias; esa configuración y una evaluación de carga quedan fuera de este piloto local. El arranque frío del emulador requirió recuperar un ANR de System UI antes del recorrido; no se certifica rendimiento de un teléfono físico.
