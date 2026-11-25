# 64 · Directorio: logos, contacto y servicios

22 de noviembre de 2026. Punto7 de la tabla. Trabajo local en el repositorio oficial, sin commits, ramas ni despliegue en Railway. La demo pública independiente utiliza datos ficticios.

## Resultado y recorrido

La tarjeta del directorio presenta una identidad reconocible: logo64, nombre completo, tipo y ciudad, resumen público de tres líneas y servicios de dos líneas. El botón **Ver contacto y servicios** abre una pantalla completa con los textos sin recortar, teléfono, correo, sitio y dirección públicos. Hay controles para copiar los datos. Abrir el detalle reutiliza el registro público recibido; no consulta miembros ni contactos internos. El botón **Actualizar directorio** solicita datos solo al pulsarlo, bloquea envíos repetidos mientras carga y permite ver cambios publicados desde otra cuenta sin polling.

En anchuras pequeñas y al ampliar texto, el logo queda arriba y el nombre debajo. El nombre completo no se oculta con puntos suspensivos. El logo usa `contain`: conserva su relación rectangular o cuadrada dentro de un espacio reservado y no salta la tarjeta durante la carga. Si no existe, es inválido o falla la descarga, aparece el icono del tipo de organización. Ese icono es un marcador, no una marca inventada.

### Publicar desde el panel

1. Abrir **Organizaciones** con una cuenta que tenga el permiso configurable `entidades.editar`.
2. Elegir **Logo público** en la fila de la organización, o **Gestionar logo público** desde su ficha editorial.
3. Seleccionar JPEG, PNG o WebP, revisar la autorización y pulsar **Publicar logo**. La organización debe estar activa, verificada y registrada como fundación, clínica o tienda.
4. Para reemplazarlo, repetir con otro archivo. La URL versionada cambia y la copia anterior se elimina después de confirmar la transacción.
5. Para retirarlo, elegir **Retirar logo**, confirmar y enviar. Deja de servirse; la retirada repetida no duplica el evento. Los contactos tienen su propia publicación/retirada independiente.
6. En la app, abrir **Inicio → Organizaciones y veterinarias**, o volver al directorio y pulsar **Actualizar**.

La edición mantiene etiquetas, consentimiento y acciones fijas. Usa POST multipart y CSRF y funciona sin JavaScript. La vista previa reserva128×128px, conserva proporción y utiliza la prioridad normal del navegador. Cancelar conserva la publicación anterior y vuelve a organizaciones.

## Contrato y protección

- `core.LogoPublicoEntidad`, una copia autorizada por organización: clave aleatoria, dimensiones, bytes, estado de publicación, publicador y fecha. La clave y el publicador no se incluyen en la respuesta pública.
- Migración `core.0015_logo_publico_entidad`, probada solo en la BD aislada. No se modificó la base real.
- POST/DELETE `/api/red/organizaciones/<id>/logo-publico/`: permiso `entidades.editar`, sin identificar roles por nombre. El mismo permiso puede concederse a cualquier rol, incluido Ciudadano, y retirarse. No se amplían los permisos de ningún rol por defecto.
- GET `/api/red/organizaciones/<id>/logo/`: consulta pública que vuelve a comprobar organización activa/verificada y logo publicado. Respuesta WebP con `no-store`, `nosniff` y CSP. No usa una URL de documentos privados ni descarga imágenes de terceros.
- El directorio añade `logo` opcional `{url, ancho, alto, bytes}`; organizaciones anteriores siguen devolviendo `null`. El cliente acepta solo la ruta relativa de esa misma organización, dimensiones de hasta512px y hasta96KB; ignora URLs ajenas, rutas privadas o metadatos inválidos.
- Entrada máxima5MB/imagen fija. Se reutiliza `core.public_images.normalizar`, ahora con límites internos opcionales: logos512px/96KB; fotografías de mascotas/productos conservan1280px/512KB. El archivo se verifica por contenido, no por nombre, se reencodifica y pierde EXIF/XMP/ICC y el nombre original. SVG y animaciones se rechazan.
- El permiso se comprueba antes de procesar y de nuevo bajo el bloqueo compartido de seguridad, antes de escribir. Los errores de almacenamiento no crean una publicación. Las claves se limitan aUUID `.webp` dentro del directorio dedicado.
- Se registran publicación, reemplazo y retirada en auditoría con descripción legible y dimensiones, sin incluir la ruta del almacenamiento. La retirada no puede borrar copias que alguien ya descargó.

## Lectura pública y presentación

Los contactos y servicios proceden exclusivamente de `perfil_publico` autorizado. Un WhatsApp interno no se usa como sustituto del teléfono público. El directorio conserva los filtros de tipos y la comprobación de verificación; la consulta sigue teniendo tres consultas SQL, sin una consulta adicional por logo. Las imágenes se solicitan al renderizar su tarjeta, sin precargar todo el directorio.

La demo adapta un logo de muestra a un recurso vectorial local del proyecto; el refugio y los contactos son explícitamente ficticios y usan dominios `example.invalid`. No se atribuyen identidades ni contactos a organizaciones reales. El backend real de logos se validó por separado con archivos sintéticos y respuestasWebP.

## Validación

El bloque cubre normalización, eliminación de metadatos, tamaño/proporción, rutas, autorización configurable/revocación durante la normalización, reemplazo, retirada/idempotencia, verificación/baja, almacenamiento inaccesible, campos adicionales rechazados, POST/CSRF del panel y la consulta sinN+1. También se repiten regresiones de fotos de productos, mascotas, galería, ayudas, perfil público y auditoría.

Flutter comprueba el contrato, organizaciones sin logo, nombre completo, anchuras320/430/720 con escala1/2, detalle sin segunda consulta de datos, actualización bajo clic explícito y copia del contacto público. La aceptación visual integral, el entorno real y TalkBack siguen en el punto14. Los logs y `validacion.json` registran los recuentos finales y el alcance de la revisión visual; no se dan por realizadas pruebas manuales que no se hayan podido ejecutar.

Criterio de cierre: punto7 completo en implementación =11/14=78,57%. Después quedan8 (fotografías de perfil en comunidad),9 (tienda) y14 (validación integral).
