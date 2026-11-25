# Fotografías públicas en Android

Revisión local del 19 de noviembre de 2026. Android consume fotos publicadas con autorización desde el catálogo y la ficha; el formulario de carga/retirada del panel se completó en la guía 27. No se usaron fotos reales para validar el recorrido ni se desplegó esta versión.

## Contrato y economía de recursos

El catálogo paginado y la ficha pública incorporan `foto`, nulo cuando no hay una publicación vigente de la fundación con custodia actual. Un descriptor válido contiene únicamente `url`, `ancho`, `alto` y `bytes`. La URL es relativa al endpoint público de esa misma mascota y lleva una versión numérica de publicación. No se exponen claves de almacenamiento, rutas del disco, originales, usuarios ni documentos del expediente.

El catálogo carga la relación en su consulta y obtiene la custodia mediante una subconsulta, evitando una consulta de foto por cada mascota. Una regresión comprueba el listado de 11 mascotas con un máximo de tres consultas. No se busca cada archivo en disco al construir el listado: una imagen ausente o ilegible se resuelve en el GET y el cliente ofrece una alternativa.

La mascota sin descriptor no crea ninguna petición de imagen. La ficha conserva la imagen completa sin recortarla y retira el aviso de foto no disponible cuando existe un descriptor. Las tarjetas se construyen al desplazarse por la cuadrícula; no se precargan todas las fotos del catálogo. Las imágenes tienen tamaño de presentación fijo, un estado de carga y decodificación acotada (hasta 640 px de ancho en tarjetas y 1280 en ficha, sin superar el ancho original).

Las URLs externas, rutas de documentos, IDs diferentes, parámetros adicionales, versiones inválidas o dimensiones/pesos fuera del contrato se rechazan. La foto se pide al origen configurado sin credenciales. Un fallo muestra el marcador y permite Reintentar fotografía; no se repite automáticamente en bucle. Al recibir un descriptor nulo se retira la imagen de la vista. Una versión distinta evita reutilizar la foto anterior en la caché de memoria.

La visibilidad se vuelve a comprobar en el GET. El descriptor no sustituye la autorización del servidor. La retirada se refleja al volver a consultar el catálogo/ficha; no se promete borrar una copia pública ya descargada. El GET entrega un cuerpo binario limitado a 512 KiB y comprueba su tamaño; se evitó así la advertencia de adaptación de FileResponse síncrono bajo ASGI.

## Código y verificación

- Django: animals/public_photos.py, animals/photo_views.py y adoption/mobile_views.py.
- Flutter: PublicPetPhoto en adoption_api.dart, public_pet_image.dart y su integración en adoption_screens.dart.
- 77 pruebas Flutter y análisis limpio. Las cuatro nuevas cubren descriptor opcional, URLs/dimensiones inválidas, cero peticiones sin foto, reintento explícito y retirada del widget.
- 306 pruebas Django en esquema MySQL aislado recreado y eliminado. Se conserva el diagnóstico del esquema reutilizado de DT-07.
- La integración Android decodifica píxeles reales de WebP en catálogo y ficha; no se limita a comprobar que exista un widget Image.

Los registros se guardan en output/adopcion-movil: flutter-fotos-movil-20261119.log, analyze-fotos-movil-20261119.log, backend-fotos-movil-20261119.log y android-fotos-movil-20261119.log.

## Reproducción de la prueba sintética

Con servidor y variables de QA local ya configurados, desde backend-panel:

```powershell
python manage.py preparar_foto_publica_qa --settings=config.settings_qa
```

El comando exige MySQL local lpn_panel_qa_29 y un gestor sintético ya autorizado. Crea una ficha temporal QA Foto Publica y un patrón de colores rotulado IMAGEN SINTETICA. Publica únicamente ese patrón mediante el servicio real, sin crear usuarios ni conceder permisos. Guarda los IDs de limpieza en un manifiesto temporal fuera del repositorio.

Desde frontend/mobile:

```powershell
flutter test integration_test/photo_android_test.dart -d emulator-5554 --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016
```

Después, incluso ante un fallo, retirar el escenario desde backend-panel:

```powershell
python manage.py preparar_foto_publica_qa --limpiar --settings=config.settings_qa
```

La limpieza comprueba IDs/nombre/publicador, revoca mediante el servicio autorizado y elimina únicamente la ficha y archivo temporales. No convertir esta prueba en una foto de una mascota real. El APK de integración no se comparte: compilar luego el APK normal con el backend local y sin defines privados.

## Reparto y continuidad

José Carlos: descriptores, consulta acotada, respuesta binaria y comando QA. María José: modelo, componente, integración y pruebas móviles. Sally: guía y evidencias; pantalla de carga/retirada completada en la guía 27, con permiso y confirmación explícita. Quedan almacenamiento persistente/restauración antes de admitir fotos reales, validación física/TalkBack y rendimiento. No se cambió el RBAC ni el esquema en esta integración, ni se hicieron commits o publicaciones.

Actualización: la carga/retirada visual del panel se completó en la guía 27; las notas anteriores describen el corte de esa etapa. La publicación productiva permanece pendiente.
