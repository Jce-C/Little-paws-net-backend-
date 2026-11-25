# Catálogo público paginado

Revisión local del 19 de noviembre de 2026. Integrado en Android; sin commits ni despliegue.

## Contrato y disponibilidad

`GET /api/adopcion/catalogo/` devuelve `results` (máximo 24 fichas), `next`, `previous` y `species`. Las especies proceden de todo el catálogo público disponible, no solo de la página actual. `?especie=Gato` filtra antes de paginar. El cursor utiliza el ID, único e inmutable; el cliente no puede aumentar el límite ni elegir el orden. No se calcula un total global de mascotas. Se usa [CursorPagination de Django REST Framework](https://www.django-rest-framework.org/api-guide/pagination/).

Cada ficha expone únicamente ID, nombre, especie y raza. Se reutiliza `disponibles_adopcion()`: sin dueño, en adopción, custodia vigente de organización verificada y no desactivada. Se vuelve a comprobar la disponibilidad en cada página. `Cache-Control: no-store` evita reutilizar una respuesta almacenada; un cursor inválido devuelve 404. La lista anterior `/api/adopcion/mascotas/` conserva su contrato para otros clientes.

## Android

- Carga 24 como máximo al entrar; solo consulta otra página al pulsar **Cargar más**. El contador dice **cargados** mientras quedan páginas; no presenta ese número como total.
- Los filtros consultan el servidor y reinician el cursor. Encuentran especies que no estaban en la primera página.
- Un fallo al añadir una página conserva lo leído y permite reintentar; los IDs repetidos no duplican tarjetas. Una respuesta tardía no sobrescribe un filtro o una recarga más recientes.
- Se comprueba esquema, host, puerto, ruta, parámetros y filtro del enlace siguiente. Solo se extrae el cursor; se reconstruye una petición pública al origen configurado, sin reenviar credenciales ni seguir URLs externas.
- Se conservan texto ampliado, colores y navegación del bloque anterior.

Código: `lib/adoption/catalog_controller.dart`, `adoption_api.dart` y `adoption_screens.dart`. Los fixtures antiguos de pantallas se presentan mediante un adaptador de pruebas; los tests del contrato paginado usan MockClient directamente para no ocultar respuestas inválidas.

## Verificación y reproducción

Pasan 73 pruebas Flutter, análisis limpio y 39 pruebas de API móvil en MySQL aislado. La integración Android comprueba 24 y 27 resultados al cargar otra página. Se cubren límites, privacidad, disponibilidad entre páginas, filtros globales, enlaces no válidos, errores recuperables, deduplicación y respuestas tardías.

En el entorno QA local ya configurado, con su servidor levantado y las variables locales de pruebas, ejecutar desde backend-panel:

```powershell
python manage.py preparar_catalogo_qa --settings=config.settings_qa
```

El comando exige la base local `lpn_panel_qa_29`, DEBUG y custodia sintética con correo example.invalid. Crea 27 fichas temporales; conserva sus IDs en un manifiesto temporal fuera del repositorio. Rechaza bases diferentes y escenarios duplicados.

Desde frontend/mobile:

```powershell
flutter test integration_test/catalog_android_test.dart -d emulator-5554 --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016
```

Después, incluso si el ensayo falla, retirar las fichas desde backend-panel:

```powershell
python manage.py preparar_catalogo_qa --limpiar --settings=config.settings_qa
```

La limpieza exige que coincidan todos los IDs y nombres sintéticos; no borra fichas arbitrarias. No compartir el APK de integración. Compilar el APK normal desde lib/main.dart, con backend local y sin defines privados.

Evidencia: `output/adopcion-movil/` contiene flutter-paginacion, analyze-paginacion, backend-paginacion, android-paginacion y build-paginacion del 20261119. Las fotos públicas, TalkBack, validación física, medición de rendimiento y publicación siguen pendientes.

## Reparto

José Carlos: API, ruta, comando QA y pruebas Django. María José: cliente, controlador, interfaz y pruebas Android/Flutter. Sally: guía y evidencias. No se modifican permisos, modelos ni migraciones. El parche de rutas de la ficha pública incluye la ruta del catálogo; comprobar el contexto antes de aplicarlo en otra base.
