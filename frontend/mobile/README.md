# Little Paws Net para Android

El primer recorrido permite ver mascotas disponibles, crear una cuenta o iniciar sesión, enviar una solicitud y consultar su estado. La fundación toma la decisión en el panel Django. La app usa la paleta, marca y portada del Figma móvil. La ficha se construye con los datos públicos de Django y muestra un marcador cuando el catálogo carece de fotos.

## Ejecutar en local

Se necesita Flutter con Dart 3.13 compatible, el SDK de Android y un emulador o un dispositivo conectado. Desde esta carpeta:

```powershell
flutter pub get
flutter analyze
flutter test test
flutter run -d emulator-5554 --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016
```

La dirección especial del emulador apunta a Django en el equipo. Para un celular por USB, ejecuta `adb reverse tcp:8016 tcp:8016` y pasa `--dart-define=LPN_API_BASE_URL=http://127.0.0.1:8016`. El backend QA debe responder en el puerto 8016. Cada compilación requiere `LPN_API_BASE_URL`: sin ella se muestra un aviso sin crear conexiones de red. No hay una URL de Railway por omisión. Para distribuir, configurar el origen HTTPS del backend elegido y preparar firma/versión; un APK debug no es una publicación comercial.

## Recorrido de aceptación

1. Levantar Django con `config.settings_qa` y MySQL aislado. Aplicar las migraciones a esa base.
2. Ejecutar `python manage.py preparar_adopcion_qa --settings=config.settings_qa`. Anotar las dos cuentas de prueba y la mascota. El comando solicita la contraseña temporal sin mostrarla.
3. En Android, abrir la mascota y enviar una solicitud con la cuenta adoptante. Comprobar el estado **Pendiente**.
4. En el panel web, entrar como gestor de la fundación de prueba, tomar la solicitud y aprobarla.
5. En Android, pulsar **Actualizar solicitudes**. Debe aparecer **Aprobada**. La mascota deja de aparecer en el catálogo público.

`integration_test/adoption_android_test.dart` usa datos sintéticos de un archivo local pasado con `--dart-define-from-file`. En ese ensayo, una segunda sesión del panel toma y aprueba la solicitud. Compila el APK distribuible de prueba con `flutter build apk --debug` y solo la dirección de la API. Los datos de acceso se ingresan desde la pantalla.

## Organización del código

- `lib/core/` valida el origen y comunica errores de la API.
- `lib/auth/` maneja registro, sesión, renovación y cierre. Guarda el token de renovación en el almacenamiento seguro nativo al usar HTTPS.
- `lib/adoption/` consume el catálogo, envía solicitudes y muestra la decisión.
- `test/` comprueba la renovación y restauración de sesión, los cambios de cuenta, las respuestas inválidas y el recorrido de adopción con respuestas controladas.
- `integration_test/` comprueba el recorrido desde Android contra Django local.

### Repetir la integración en Android

Usa un escenario QA nuevo. Guarda un archivo JSON fuera del repositorio con estas variables y los valores que elegiste al crear el escenario:

```json
{
  "LPN_API_BASE_URL": "http://10.0.2.2:8016",
  "LPN_QA_CITIZEN": "adoptante-ejemplo@example.invalid",
  "LPN_QA_PASSWORD": "CONTRASEÑA_TEMPORAL_DE_PRUEBA",
  "LPN_QA_PET_NAME": "NOMBRE_EXACTO_MASCOTA_QA"
}
```

Abre el panel web como gestor antes de iniciar la prueba. Ejecuta desde esta carpeta:

```powershell
flutter test integration_test/adoption_android_test.dart -d emulator-5554 --dart-define-from-file=RUTA_PRIVADA_QA.json
```

Cuando aparezca la solicitud pendiente en el panel, tómala y apruébala. La prueba comprueba el estado en Android. El APK de prueba compartible se compila desde `lib/main.dart` con la URL local, por separado de este ensayo.

## Sesión y recuperación de acceso

Desde **Mi cuenta → Editar perfil** puedes actualizar nombre y teléfono opcional. Guardar envía solo los campos modificados a `PATCH /api/auth/perfil/` y la cuenta muestra la respuesta confirmada por Django. Dejar el teléfono vacío lo elimina explícitamente. Cancelar o volver ofrece descartar el borrador; un fallo conserva lo escrito para reintentar. Las acciones permanecen visibles con texto ampliado.

El servidor actualiza únicamente la cuenta autenticada y rechaza IDs, correos, contraseñas, roles o indicadores de administración dentro de este formulario. No es una pantalla para asignarse permisos. La actualización es transaccional, se auditan los nombres de los campos modificados sin duplicar el teléfono en el evento y las respuestas de perfil llevan `no-store`. Una respuesta tardía después de cerrar sesión no reactiva la cuenta. El cambio/verificación de correo, recuperación de contraseña y cierre de cuenta siguen pendientes en la app.

Si el servidor rechaza también el acceso renovado, la app cierra la sesión local y permite ingresar otra vez. Un error de permisos (403) conserva la cuenta. Las solicitudes simultáneas comparten una renovación; una respuesta atrasada de una cuenta anterior se descarta. Al cerrar la app se conserva únicamente la renovación en almacenamiento seguro cuando la API usa HTTPS. Las pruebas locales sobre HTTP no guardan credenciales de sesión.

## Respuestas incompletas

El catálogo y el seguimiento validan los datos recibidos y permiten reintentar su consulta si el servidor devuelve una estructura incorrecta. Si una creación responde sin confirmación válida, revisa **Mis solicitudes** antes de volver a enviarla. El cliente no repite automáticamente esa creación, porque el servidor pudo haberla registrado.

## Portada optimizada

La portada conserva el recurso de Figma a 1024 × 434 px y se distribuye en WebP (102 376 bytes frente a 848 920 del PNG, 87,9 % menos). Está incluida en la app, por lo que no genera una descarga HTTP al abrir el catálogo. Para regenerarla desde el original: Pillow, formato WEBP, quality=86, method=6, sin redimensionar. El original se conserva en output/adopcion-movil/referencias fuera del módulo distribuible.

## Adaptación al tamaño de texto

La cabecera y la navegación se ajustan al tamaño de letra del sistema. Las pruebas cubren el catálogo y acceso con texto al 200 % en 320 × 640 y 800 × 360. El formulario conserva el desplazamiento vertical para alcanzar sus acciones. Falta validar TalkBack y el teclado en un dispositivo físico antes del piloto externo.

## Rescates y reportes

La pestaña **Rescates** muestra reportes publicados y permite buscar por texto, abrir su detalle y reportar un animal. El formulario solicita situación, ciudad, barrio, referencia y descripción; contacto e indicaciones son opcionales. Escribe al menos dos letras de la ciudad y selecciona el resultado con departamento. Los tipos y ciudades proceden de Django.

- Con cuenta: la confirmación ofrece **Ver mis reportes**, donde se consulta estado y aceptación por una fundación cuando existe un caso.
- Sin cuenta: la confirmación muestra una clave privada una sola vez. Se puede copiar para conservarla; no se guarda ni se registra en logs de la app. Desde Rescates → Gestionar reporte anónimo puedes usar el número y la clave para corregir o cerrar el reporte pendiente.
- Los contactos, direcciones y claves no se añaden al listado público desde estas consultas nuevas.

Consultas nuevas: `GET /api/reportes/opciones/?ciudad=Riohacha` y `GET /api/reportes/mios/` (requiere cuenta). El envío reutiliza `POST /api/reportes/` y el permiso configurable `reportes.participar`. La lista pública usa el endpoint ya existente `GET /api/seguridad/operaciones/reportes-publicos/`.

Referencia visual: Figma `83:2` y `145:1341` del archivo móvil original. La portada de rescates se descargó de ese diseño y se optimizó a WebP. Fotografías reales, carga de evidencias y mapa están pendientes; no se incluyen botones que simulen esas operaciones.

Para probar el recorrido real en Android con cuentas sintéticas locales:

```powershell
flutter test integration_test/rescue_android_test.dart -d emulator-5554 --dart-define-from-file=RUTA_PRIVADA_QA.json
```

## Bandeja de notificaciones

La campana de la cabecera abre los avisos de la cuenta. Permite actualizar, filtrar sin leer y marcar una notificación como leída. La lectura se refleja después de la confirmación de Django; si falla, se conserva sin leer y se puede reintentar. Cambiar de cuenta descarta respuestas anteriores.

No se consulta esta bandeja al iniciar la app ni al abrir el acceso sin cuenta: la consulta empieza al abrirla con una sesión. Reutiliza `GET /api/notificaciones/` y `POST /api/notificaciones/{id}/leer/`. Muestra hasta los 100 avisos que entrega actualmente esa API; no incluye push, correo ni WhatsApp.

El Figma original incluye la campana y no tiene un frame específico de bandeja. La pantalla nueva usa las mismas superficies crema, acento salvia, iconos con texto y controles accesibles. Se conserva el tamaño de letra del sistema y la marca se mide para compartir espacio con la campana.

## Gestionar un reporte sin cuenta

Desde **Rescates → Gestionar reporte anónimo**, ingresa el número y la clave privada del reporte. Puedes reemplazar descripción/contacto, eliminar explícitamente el contacto privado o cerrar el reporte con confirmación. Dejar un campo opcional vacío conserva su valor anterior. La clave permanece oculta, no se guarda y se borra del formulario al confirmar el cambio. La confirmación no vuelve a mostrarla.

La app reutiliza `POST /api/reportes/{id}/gestion-anonima/`. El servidor verifica el hash de la clave y rechaza reportes aceptados o cerrados. No hace falta una sesión de cuenta y esta gestión no usa el token de otra persona. La pantalla tiene acciones visibles y conserva el formulario si falla la operación. Un error de clave indica revisar número y clave, sin confundirlo con permisos de una cuenta.

## Ficha pública de adopción

Al abrir una mascota se consulta `GET /api/adopcion/mascotas/{id}/`. Muestra edad (indicando si es estimada), tamaño/sexo cuando están registrados, organización, ciudad de la organización y fecha de custodia. La ficha se organiza con la foto central, datos y tarjeta de historia de la referencia Figma `128:502`. Cuando no hay una foto pública autorizada se mantiene el marcador; no se utiliza la fotografía de otro animal.

La historia muestra únicamente custodia real y disponibilidad actual. No inventa vacunas, rescates ni fechas ni expone el expediente médico. Una edad desconocida se indica como sin registrar. Una mascota sin nombre tiene una etiqueta de ausencia de nombre, no una identidad ficticia.

Solo se publica si sigue disponible, no tiene dueño y tiene una custodia vigente en una organización verificada y activa. Actualizar una ficha que dejó de estar disponible retira la acción de solicitar. El POST de adopción sigue validando esas condiciones al enviar.

## Mis mascotas y expediente privado

Desde **Mi cuenta → Mis mascotas** se listan las fichas asociadas a la cuenta, incluidas las adopciones aprobadas. **Ver expediente** consulta las últimas 50 atenciones registradas y muestra sus correcciones junto al original. Una historia sin atenciones se presenta vacía, sin ejemplos añadidos. Los archivos adjuntos y escritura clínica no forman parte de esta pantalla todavía.

La lista nueva usa `GET /api/mascotas/mias/` y requiere `mascotas.participar`; no admite elegir otra cuenta mediante parámetros. El expediente reutiliza `GET /api/seguridad/operaciones/registros/expediente/{id}/` y sus permisos vigentes. La lista no contiene notas clínicas. Si hay una custodia vigente que entra en conflicto con la asociación de dueño, se indica para que la organización revise la titularidad.

Los datos clínicos se retiran de la vista al cerrar sesión o recibir una denegación al actualizar. No se almacenan en archivos locales. El backend responde no-store. Referencias del Figma original: perfil `156:1796` y expediente `128:599`; se adaptó a pantallas legibles y permisos reales, sin copiar el QR ni las vacunas de ejemplo.

## QR temporal de identificación

Desde el expediente, **QR de identificación → Generar QR** solicita un código real a `POST /api/mascotas/{id}/qr/`. Abrir la pantalla no genera códigos. El botón permanece visible incluso con texto ampliado. Cada emisión dura 24 horas e invalida el código anterior; reemplazar el código visible requiere confirmación. Si se pierde la respuesta de red, se puede generar otro, que invalida cualquier emisión anterior.

Se dibuja el identificador devuelto por el backend con [qr_flutter](https://pub.dev/packages/qr_flutter), localmente y en blanco/negro para su lectura. No es la imagen de muestra de Figma ni un enlace al historial. Un lector de QR devuelve el identificador que usa el flujo veterinario existente del panel (`/api/qr/{codigo}/atenciones/`); la app ciudadana todavía no incluye lector ni formulario clínico. La consulta del código muestra solo ID/nombre; registrar una atención exige una cuenta veterinaria verificada y autorización vigente. Poseer el QR no concede esos permisos.

El teléfono no persiste ni copia el código. Se retira al vencer, cerrar sesión, dejar la pantalla o pasar la app a segundo plano; una respuesta en vuelo anterior se descarta. Ocultar el código no lo revoca en el servidor: vence o queda invalidado al generar otro o cambiar la titularidad según el flujo existente. Las respuestas de emisión/consulta, incluidas las denegadas, llevan `Cache-Control: no-store`. No compartir capturas de códigos vigentes como evidencia pública.

Las pruebas `pet_qr_test.dart` cubren generación explícita, reemplazo/cancelación, segundo plano, cierre de sesión, denegación, vencimiento y tamaño 320 px con texto al 200 %. `animals.tests_mobile` verifica dueño/ajeno/anonimato, hash, reemplazo, expiración y que el QR no otorgue escritura clínica.


Para comprobar la edición de perfil con una cuenta sintética del escenario local:

```powershell
flutter test integration_test/profile_android_test.dart -d emulator-5554 --dart-define-from-file=RUTA_PRIVADA_QA.json
```

El ensayo cambia nombre/teléfono, vuelve a abrir el formulario para comprobar la persistencia y restaura los valores previos. Compila luego el APK normal desde `lib/main.dart` sin el archivo privado de defines. No distribuyas el APK de integración.


## Identidad y materiales

La entrada normal muestra una bienvenida `#FCF0D3`. Explorar abre el catálogo y los accesos llevan directamente a ingreso/registro. Las pantallas operativas usan `#FFF9EC`. `lib/design/` centraliza colores, tipografía, navegación y material translúcido; las fuentes JetBrains Mono y Leckerli One son locales y conservan sus licencias. No se agregan descargas de fuentes ni una librería de shaders.

La barra inferior de ancho completo y borde superior conserva etiquetas completas y se adapta a dos filas con texto ampliado en teléfonos estrechos. Apariencia → Reducir transparencias conserva la elección localmente; contraste alto y reducción de movimiento usan superficies sólidas automáticamente. Tablas y datos clínicos no reciben filtros ópticos. El icono Android usa el perrito original.

`test/design_test.dart` verifica colores, acceso/registro sin consultas previas, consulta del catálogo solo al explorar, preferencia persistente, contraste alto y bienvenida al 200 % de texto. `integration_test/design_android_test.dart` prueba la entrada normal contra `http://10.0.2.2:8016` sin credenciales ni escrituras de negocio. Consulta `docs/diseno/23-materiales-y-paleta.md` desde la raíz para criterios y evidencias.


## Catálogo por páginas

Adoptar consulta `/api/adopcion/catalogo/`, con hasta 24 mascotas por página. Cargar más conserva los resultados y ofrece reintento si falla. Los filtros por especie consultan el catálogo completo en el servidor. No se presentan los registros descargados como un total mientras quedan páginas.

`test/catalog_pagination_test.dart` cubre el contrato y las carreras de recarga/filtros. `integration_test/catalog_android_test.dart` usa 27 fichas sintéticas preparadas con `preparar_catalogo_qa`; retirar siempre el escenario con `--limpiar`. Ver la guía `docs/diseno/24-catalogo-publico-paginado.md` desde la raíz para los comandos y la barrera de QA local. El APK requiere esta versión del backend; no activar contra una versión antigua sin integrar primero su API.


## Fotos públicas

El catálogo y la ficha muestran únicamente imágenes descritas como publicadas por el backend. Sin foto no se hace una petición de imagen. Las rutas y dimensiones se validan; el error permite reintentar y la decodificación tiene límites. La foto se actualiza por versión y se retira de la vista cuando los datos actualizados ya no la incluyen.

`test/public_pet_image_test.dart` cubre el contrato y consumo de red. `integration_test/photo_android_test.dart` utiliza el patrón temporal creado con `preparar_foto_publica_qa`; retirar siempre mediante `--limpiar`. Ver docs/diseno/26-fotos-publicas-en-android.md desde la raíz. La carga y retirada desde el panel están integradas en la guía 27; no se publican imágenes del expediente ni fotos ficticias en fichas reales.


La revisión de fidelidad usa las medidas y efectos de los frames originales de Figma. Ver docs/diseno/28-fidelidad-figma.md. Las fotografías siguen siendo dinámicas y no se sustituyen por las del mockup.


Los encabezados de sección usan lib/design/lpn_app_bar.dart para medir el texto con la fuente real, conservar el tamaño elegido por la persona y dejar espacio para volver y actualizar. Cuatro regresiones nuevas y el APK normal verifican el comportamiento; ver docs/diseno/31-encabezados-adaptativos-android.md. La revisión de encabezados se validó entonces con 81 pruebas Flutter.


## Envío sin confirmación

Si se pierde la respuesta de una solicitud, la acción pasa a Ver mis solicitudes. Se consulta el resultado real antes de repetir el envío; no se anuncia un éxito ni se reintenta automáticamente. Cancelar permanece disponible. Los errores explícitos corregibles mantienen la nota editable. Ver docs/diseno/32-adopcion-envio-incierto.md y test/adoption_uncertain_test.dart. El fallo de red se valida con HTTP simulado; el APK normal se comprueba contra el catálogo QA local.


## Presupuesto de red JSON

ApiClient acumula como máximo 1 MiB por respuesta JSON y conserva el plazo normal de quince segundos. Comprueba tanto Content-Length como los bytes reales y señala cancelación del transporte al vencer el plazo. No trunca el documento ni repite operaciones automáticamente. Abortar la conexión no revierte una transacción en Django: ante confirmación perdida se consulta el resultado, como en el flujo de adopción. Las fotos tienen límites propios. Ver docs/diseno/33-respuestas-moviles-acotadas.md y test/api_response_budget_test.dart. La revisión de presupuesto se validó entonces con 99 pruebas Flutter.


## Navegación y ficha según Figma

La revisión de navegación y ficha pasó 108 pruebas Flutter. La navegación conserva destinos reales con marca central original; la ficha agrupa edad/tamaño y presenta una historia de custodia con datos públicos verificados. El botón de adopción permanece visible sin bajar al final del contenido. Ver docs/diseno/34-composicion-catalogo-figma.md y docs/diseno/35-navegacion-y-ficha-figma.md desde la raíz para capturas, límites y pendientes.


## Perfil y roles propios

La revisión de perfil pasó 115 pruebas Flutter. Mi cuenta muestra los identificadores reales de roles globales y por organización desde GET /api/seguridad/mis-accesos/, una vez por entrada y mediante actualización explícita. Son de solo lectura; no se derivan privilegios del cliente ni se autoasignan roles. Un error o cierre de sesión retira los datos previos. La pantalla anónima no hace esta consulta. Ver docs/diseno/36-perfil-y-roles-propios.md para la referencia Figma, límites y evidencias.


## Rescates y filtro local

La revisión actual pasa 121 pruebas Flutter. El buscador se integra en la ilustración y filtra situación, estado y descripción de los reportes cargados, sin tildes ni distinción de mayúsculas. Escribir y limpiar no generan consultas. El contrato público limita a 100 registros y no incluye ciudad estructurada ni coordenadas para un mapa. Ver docs/diseno/39-rescates-busqueda-y-composicion.md para la referencia y los límites.


### Revisión integral de composición móvil (local, 19-11-2026)

Se revisaron los 29 frames de Figma. Se recuperaron las tarjetas horizontales y categorías originales de Rescates, etiquetas externas de acceso, registro con confirmación local, solicitud en página con acciones fuera del scroll, mascotas reales dentro del perfil y confirmación de reporte con identidad original. Cabeceras y botones se ajustaron al prototipo. 123 pruebas Flutter pasan y el análisis está limpio. Ver `docs/diseno/40-auditoria-integral-mobile-figma.md` para la matriz de pantallas y diferencias pendientes; mapa, tienda, apadrinamiento y algunos contratos del prototipo siguen pendientes. No se publica ni se declara un calco completo.


Verificación posterior: 126 pruebas Flutter y análisis limpio. Corregido el reintento de mascotas en perfil; se prueba privacidad al cerrar sesión y manejo de 403 sin bucles. Evidencias `flutter-perfil-privacidad-20261119.log`, `analyze-perfil-privacidad-20261119.log` y `build-perfil-privacidad-20261119.log`.


## Formularios e interfaz Inter

Revisión vigente: formularios agrupados, campos sin sombras repetidas, acciones principales en negrita y barras de vidrio recortado. Conserva alternativa sólida y acciones fuera del scroll. 126 pruebas; documentación y alcance en `docs/diseno/41-formularios-legibles-y-glass.md`. La app sigue siendo un piloto QA local, sin publicación ni integración nueva de mapa/tienda/apadrinamiento.


Verificación posterior del catálogo: 128 pruebas; nombres 16, resúmenes 14 y filtros 12, con cuadrícula medida y anuncio accesible único. Evidencias `flutter-catalogo-legible-20261119.log`, `analyze-catalogo-legible-20261119.log` y `build-catalogo-legible-20261119.log`. No se certifica TalkBack físico.


Verificación de privacidad del expediente: 131 pruebas Flutter y análisis limpio. Tres regresiones adicionales cubren logout/respuesta tardía, cambio de cuenta con 403 y reintento explícito sin bucles. No cambia el código del APK; se conserva la compilación QA anterior. Evidencias `flutter-expediente-sesion-20261120.log` y `analyze-expediente-sesion-20261120.log`.


### Reportes paginados (20-11-2026)

Rescates e Historias usan `/api/reportes/publicos/`, páginas de 20 y búsqueda en servidor con espera de 400 ms. Cargar más conserva resultados ante fallos y admite reintento. Requiere integrar primero el backend de la guía 42; no publica ni genera datos de negocio. Suite actual: 138 pruebas, análisis limpio y APK debug QA compilado.


Controles revisados con Figma (20-11-2026): radio 15,5, crema/beige y sombra del campo sin cubrir errores. La barra principal es de ancho completo y cede espacio al teclado inferior. 139 pruebas y análisis limpio; guía 44 y evidencia en controles-figma-2026-11-20. APK QA local, sin publicación.


## Rediseño integral Stitch

La revisión vigente incorpora inicio de servicios, ayudas, red verificada, comunidad real y tienda con pedido sin pago. Adopción admite una galería autorizada de hasta seis fotos. Ejecutar las migraciones de `animals.0008`, `core.0011` y `seguridad.0020` antes de probar las nuevas rutas. Los formularios no confirman pagos ni aceptación de voluntariado. No confundir los registros ficticios de la demo web independiente con la BD real. Detalle, límites y recorrido: [guía 48](../../docs/diseno/48-redisenio-integral-stitch.md).


## Barra contextual y demo visual Android

El botón central sobresale de la cápsula. En Solicitudes abre el catálogo para comenzar una solicitud; en los otros destinos vuelve a Inicio. Login y registro usan el tema anterior aislado. El cliente real no incorpora fotos de stock en registros del backend. Para revisar imágenes ficticias se prepara un simulador Android separado, «LPN · Demo visual», con paquete terminado en `.visualdemo`, sin conexión a la API real. Ver [guía49](../../docs/diseno/49-barra-contextual-y-acceso.md).


## Referencia visual vigente · PDF y replicador (21-11-2026)

La guía56 reemplaza las disposiciones/radios anteriores donde difieran: acceso orgánico salvia, campos14, botones18, tarjetas20–24, tipografía Inter y paleta original. Catálogo compacto con estado de adopción y metadatos fuera de la foto; rescates sin textos superpuestos; sugerencias en formularios que solo rellenan borradores. Conserva cápsula cóncava y acciones reales. Suite canónica191 y demo aislada197 pruebas; no equivalen a pruebas contra Railway. Límites de datos públicos y cobertura: [guía56](../../docs/diseno/56-redisenio-referencias-visuales.md).


## Revisión58 · onda, Inicio y lectura

Acceso con onda a ancho completo y formulario separado, Inicio integrado con texto fuera de la imagen, tarjetas por capas/entrada escalonada con movimiento reducido, formulario de mensajes y aportes agrupados, y perfil que prioriza mascotas. Acceder desde bienvenida lleva a Inicio.197 pruebas canónicas,203 de demo; no certifican producción. Los contratos públicos de fotos de productos/contactos/cuidados y pagos siguen pendientes. Se conserva la marca actual; la propuesta de hocico se entrega aparte.


## Revisión59 · fotografías de productos

La tarjeta y ficha comercial admiten una fotografía pública validada del mismo producto y origen. Las fichas legacy mantienen su marcador. Ver [guía59](../../docs/diseno/59-fotografias-publicas-productos.md) para publicación/retirada, migración requerida y límites.199 pruebas Flutter; backend y almacenamiento deben integrarse antes de probar esta función en Railway. La demo pública no se actualizó en este bloque.


## Revisión60 · círculos y perfiles públicos

Flechas centradas en ambos ejes del círculo decorativo. El directorio admite `perfil_publico` opcional y no infiere contactos desde datos internos.205 pruebas canónicas y análisis limpio. La demo independiente v7 publica únicamente la corrección visual; perfiles requieren integrar core.0012 en el backend. [Guía60](../../docs/diseno/60-flechas-y-fichas-publicas.md).


## Revisión61 · identidad, marca, bienvenida e Inicio

208 pruebas canónicas. Perro orgánico completo aplicado, bienvenida con propósito explícito y HomeBackdrop independiente del scroll; superficies compartidas respetan modo sólido. Estado de los14 puntos y criterios de cierre: [guía61](../../docs/diseno/61-cierre-identidad-bienvenida-inicio.md). Los pendientes de backend y validación real permanecen identificados.


## Revisión62 · cuidados por mascota

Se muestra `presentacion` pública opcional en tarjeta, ficha y solicitud, con compatibilidad legacy y cuidados sin publicar explícitos.212 pruebas del cliente. Backend requiere integración revisada de animals.0009; no desplegado a Railway. [Guía62](../../docs/diseno/62-descripcion-cuidados-adopcion.md).


### Actividades y canales de ayuda · revisión63

Programa público con RBAC por organización, actividades concretas y canales declarados por la organización. No procesa pagos. Migraciones core.0013/0014 preparadas y verificadas solo en base aislada. Recorrido e integración: `docs/diseno/63-tarjetas-y-programas-ayuda.md`.


### Directorio y logos públicos · revisión64

Identidad de organizaciones con logo autorizado, contacto y servicios públicos; ficha completa y actualización explícita. Publicar/retirar desde Organizaciones → Logo público, con entidades.editar. Migración core.0015 preparada; aplicar primero en base local revisada. Detalles en `docs/diseno/64-directorio-logos-publicos.md`.


### Comunidad y fotos públicas

Mi perfil y Comunidad permiten elegir una foto, autorizar su publicación y retirarla. Ejecutar flutter pub get y reconstruir Android tras añadir image_picker; requiere backend con core.0016 y volumen privado persistente al desplegar. El perrito central abre un reporte; el + de Solicitudes conserva el flujo de adopción. Ver docs/diseno/65-comunidad-fotos-y-rescates.md.


## Cierre tienda y referencias visuales ·22-11-2026

Tienda con fotos autorizadas, importe decimal exacto y comprobante del servidor; bienvenida/login según los SVG del usuario; accesos circulares de Inicio, reporte por etapas y retrato opcional en expediente protegido. Ver docs/diseno/66-tienda-fotos-y-pedido-trazable.md y docs/diseno/67-referencias-acceso-expediente-y-reporte.md. Implementación local; el punto14 conserva la aceptación en dispositivo y entorno real pendiente.

Revisión actual: [34 vistas, navegación de vidrio y validación pendiente](../../docs/diseno/68-revision-pantallas-y-navegacion.md). Las pruebas visuales usan datos ficticios; no son aceptación en dispositivo.

## Correcciones ciudadanas · guía 71

Revisar [la guía de integración y límites](../../docs/diseno/71-correcciones-ciudadanas-y-paleta.md). Se incorporan fotos de reporte, mascotas personales, historial y reserva de adopción y cuentas por destinatario. Requiere integrar el backend y sus migraciones en un entorno de prueba antes de usar el cliente nuevo. No se ha migrado Railway.

## Preparación de publicación · guía72

Consultar [cierre, firma y criterios de entrega](../../docs/diseno/72-cierre-auditoria-y-publicacion.md). No distribuir release con firma debug. El backend debe incorporar core.0017 y anunciar reintentos_seguros antes de habilitar la recuperación automática. El dominio anterior de Railway está sin servicio activo según la revisión de24noviembre; elegir y validar un entorno antes de compilar para clientes.
