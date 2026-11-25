# Rediseño integral móvil · referencia Stitch · 20 noviembre 2026

## Alcance y referencia vigente

Se revisaron las 14 secciones del documento del usuario y los dos HTML del ZIP `stitch_interface_clone_system.zip`. El ZIP aporta referencias visuales, no una aplicación completa. La implementación sigue en Flutter (`frontend/mobile`) y Django/DRF (`backend-panel`), con los contratos existentes de sesión, custodia, solicitudes, reportes y pedidos.

La petición nueva sustituye la navegación rectangular y los radios 15,5 de la guía 44: ahora se usan controles de radio 28, tarjetas orgánicas de 32, tipografía Inter local, titulares de 30–38 y barra inferior oscura flotante. Se conservan los fondos #FCF0D3 de bienvenida y #FFF9EC de operación. Las formas onduladas se dibujan en Canvas, sin archivos raster adicionales. El vidrio queda limitado a navegación y acciones; la lectura conserva superficies claras. No se afirma usar APIs de Liquid Glass de Apple en Android.

## Recorrido de los 14 puntos

| Punto | Implementación | Verificación / límite |
|---|---|---|
| 1. Identidad y distribución | Tokens, superficies orgánicas, jerarquía, tarjetas y controles compartidos | Flutter, tamaños pequeños y texto ampliado; revisión nativa |
| 2. Marca e iconos | Perro completo en encabezado, acceso y medallón; iconografía Material consistente | Se conserva la marca original. La exploración alternativa se entrega como SVG separado, no como una sustitución de marca aprobada |
| 3. Bienvenida | Propósito, entrada directa, explorar y registro; CTA principal distinguido | No consulta el catálogo al abrir bienvenida/login |
| 4. Imagen superior | Arte en contenedor propio; título, datos y filtros fuera de la ilustración | Reflujo de texto; sin botones superpuestos al arte |
| 5. Adopción | Fotos autorizadas: portada + hasta 5 adicionales; swipe, controles e indicador; edad/sexo/tamaño reales; requisitos explicados | Consentimiento, custodia actual, retirada y disponibilidad revisados en backend. Sin foto se muestra un marcador honesto |
| 6. Ayudas | Aporte monetario sin pago, interés de voluntariado/especie, ofrecimientos propios y gestión de convocatoria por organización | Registro real, RBAC, trazabilidad, aviso interno al responsable, control de duplicados y conflicto de versiones. No cobra ni confirma una entrega |
| 7. Red de organizaciones | Fundaciones, veterinarias y tiendas verificadas/activas; filtros locales | Solo campos públicos; no inventa contactos, servicios o registros |
| 8. Comunidad | Publicaciones, autores, fechas, comentarios, respuestas de un nivel, reacciones y retirada propia/moderación | BD real; permisos configurables; moderación ajena exige motivo; paginación acotada y límites de frecuencia |
| 9. Tienda | Productos reales, descripción, categoría, precio, existencias, detalle y pedido sin pago | Se reutiliza `/api/pedidos/`; excluye productos retirados. Sin fotos de producto autorizadas aparece un marcador |
| 10. Casos activos | Encabezado «Animales que necesitan ayuda» | Conserva consulta y creación de reportes |
| 11. Navegación | Inicio, Adoptar, Solicitudes y Mi cuenta; el inicio ofrece rescates, ayudas, red, comunidad y tienda | Conserva acceso directo a solicitudes y cuenta; no añade siete pestañas comprimidas |
| 12. Movimiento | Entrada sutil de 280 ms, transiciones de ruta, estados de pulsación, galería manual | Respeta reducción de movimiento; sin autoplay ni animaciones continuas |
| 13. Integración | APIs existentes reutilizadas; nuevos modelos y rutas solo donde no existía soporte | No sustituye datos reales por ejemplos; demo pública separada con MockClient |
| 14. Pruebas | Suite móvil completa, regresiones de backend/RBAC, análisis, compilación Android y revisión visual | No equivale a certificación de TalkBack, prueba física o lanzamiento comercial |

## Archivos principales

- `frontend/mobile/lib/design/`: tema, bienvenida, navegación, hero, superficies y entradas orgánicas.
- `frontend/mobile/lib/explore/`: inicio, red, ayudas, comunidad, escritura, convocatoria, pedidos y compromisos.
- `frontend/mobile/lib/adoption/`: metadatos, galería y requisitos; autorización de imágenes conservada.
- `backend-panel/core/community_api.py`, `mobile_directory.py`, `models.py`, `urls.py`: conversación, ayuda y directorio.
- `backend-panel/animals/public_photos.py`, `photo_views.py`, `models.py`, `urls.py`: galería pública autorizada.
- `backend-panel/commerce/api.py`, `adoption/mobile_views.py`: DTO de catálogo real y exclusión de bajas.
- `backend-panel/seguridad/web/foto_mascota.py` y su plantilla: portada/galería desde el panel existente.

## Migraciones y permisos

Nuevas migraciones `animals.0008_galeria_publica`, `core.0011_comunidad_y_ayudas` y `seguridad.0020_comunidad_y_ayudas`. Los permisos `comunidad.participar`, `comunidad.moderar`, `ayudas.participar` y `ayudas.gestionar` se registran en el mismo RBAC configurable. Gestionar ayudas exige alcance de la entidad; no concede acceso global por ser responsable de una sola organización. Publicar es texto plano, sin HTML interpretado. Las respuestas privadas llevan `no-store`.

Convocatorias usan un identificador de versión para impedir que dos responsables se sobrescriban silenciosamente. Un guardado con versión antigua devuelve 409. Los intereses repetidos idénticos no duplican registros ni avisos; textos diferentes en la misma modalidad devuelven conflicto. Los formularios conservan el borrador y evitan repetir envíos de resultado incierto.

## Cómo probar

1. En una BD local aislada, instalar requisitos y ejecutar `python manage.py migrate`. No copiar variables privadas al repositorio.
2. Ejecutar `python manage.py test core.tests_community core.tests_mobile_directory animals.tests_gallery adoption.tests_mobile seguridad.tests_foto_web --settings=config.settings_test_mysql --noinput` y las regresiones `seguridad.tests`.
3. En `frontend/mobile`: `flutter pub get`, `flutter analyze`, `flutter test`.
4. Para el emulador: `flutter run --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016`. La variable debe llamarse **LPN_API_BASE_URL**; otra variable no cambia la API.
5. Recorrer bienvenida, entrada, catálogo, ficha, requisitos, inicio, ayudas, red, comunidad y tienda. En privado probar cambios, salida con borrador y retirada de permiso.
6. Desde la gestión web de foto, publicar solo imágenes propias/autorizadas; activar «Añadir a galería» para conservar portada. Retirar cada foto y comprobar que deja de servirla la API.

## Evidencia y separación de entornos

Los logs y las capturas de esta revisión están en `output/redisenio-stitch-2026-11-20/` y `output/adopcion-movil/*stitch*20261120.log`. El APK QA contiene únicamente la dirección local, no credenciales. La BD local de aceptación conserva datos sintéticos; no se migró Railway. Los ZIP locales no crean commits ni prueban un despliegue de producción.

La demo alojada comparte componentes pero usa registros ficticios en memoria y fotografías de ejemplo de Unsplash, con créditos y licencia en `assets/demo-photos/`. Esas fotos nunca se convierten en fotografías de animales reales en la BD. Reiniciar borra las acciones simuladas. La app real usa exclusivamente DTOs autorizados del backend.

## Pendientes reales para publicar

Datos y fotos consentidas de organizaciones/animales/productos; configuración operativa de soporte y moderación; aceptación de voluntariado/entregas (hoy se registra el interés); medio oficial de aportes o integración de pagos con conciliación (hoy no hay cobro); pruebas físicas y TalkBack; revisión de políticas/consentimientos; firma y distribución del APK; aprobación de migración y despliegue revisado. El prototipo no demuestra ventas ni atención médica real.


## Validación registrada

159 pruebas Flutter, análisis sin incidencias, compilación Android QA correcta; 56 pruebas funcionales Django y 61 regresiones RBAC en MySQL aislado, todas aprobadas. Dos pruebas adicionales de la demo verifican sus rutas ficticias y la UI con fotos locales. La captura 200 % se realiza tras reiniciar con escala del sistema 2,0, restaurándola a 1,0 al terminar. No se equipara esta comprobación con una auditoría completa de accesibilidad.

El estudio de logo `recursos/logo-organico-estudio.svg` conserva orejas y hocico con curvas continuas. Es una alternativa vectorial separada para revisión; la aplicación conserva el logo original completo, sin cambiar de marca silenciosamente.


Demo independiente actualizada, versión 2: https://little-paws-mobile-demo.e-rios48.chatgpt.site/ . El enlace conserva datos ficticios en memoria; no es el despliegue de Railway. Se verificaron widgets, transporte simulado, compilación y publicación. La inspección visual se realizó en Android; el recorrido manual multinavegador y la QA física siguen pendientes.
