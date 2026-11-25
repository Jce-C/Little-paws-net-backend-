# 65 · Comunidad, reportes y jerarquía visual

Fecha: 22 de noviembre de 2026. Cierre técnico del punto 8; la aceptación integral continúa en el punto 14.

## Cambios visibles

- El perrito central abre directamente un reporte. El “+” de Solicitudes conserva su función de iniciar una solicitud de adopción mediante la selección del animal.
- Rescates: cabecera redondeada con imagen local optimizada y texto legible; acciones circulares con etiquetas y ayuda; cuadrícula de dos columnas, colores suaves, huellas de fondo y una acción por tarjeta. Texto ampliado pasa a una columna. El historial incluye reportes archivados y conserva la paginación real.
- Ficha del reporte: tipo y estado destacados, ciudad separada, descripción completa seleccionable y seguimiento real. Se retiró el gran bloque vacío de fotografía. No se inventan avances ni diagnósticos.
- Comunidad: encabezado breve, autor/fecha/foto agrupados, separadores discretos y lectura expandible de publicaciones largas. Conversaciones, reacciones, retirada y moderación conservan sus comprobaciones del servidor.
- Nuestra red: filas editoriales con identidad, ciudad/tipo en líneas separadas y acceso directo a contacto y servicios. Sin repetir descripciones extensas en el listado.
- Tienda: fotografía a la izquierda y datos a la derecha, precio destacado y una sola acción. Aumentar el texto reorganiza el contenido verticalmente. La ausencia de foto tiene un estado compacto y accesible.

## Foto pública de perfil

1. Iniciar sesión y abrir Mi perfil → icono de cámara, o Comunidad → cámara.
2. Elegir una imagen de la galería. Seleccionarla solo muestra una vista previa local.
3. Marcar la autorización para mostrarla públicamente; entonces se habilita Publicar foto.
4. Puede retirarse con confirmación. Las publicaciones pasan a mostrar la inicial al volver a consultar el feed.

La foto es opcional. No se publican teléfono, correo, nombre de archivo original ni identificadores de cuenta. Solo la persona autenticada puede editar su propia fotografía. Si hay datos privados del perfil sin guardar, el acceso a la cámara permanece deshabilitado.

Backend: POST/GET/DELETE `/api/auth/foto-publica/`; lectura pública por UUID `/api/comunidad/perfiles/<uuid>/foto/`. Entrada máxima 5 MB; JPEG/PNG/WebP normalizados a WebP de hasta 256 px y 64 KB, sin EXIF. Al reemplazar se rota la URL; retirar o desactivar la cuenta impide servirla. Los cambios quedan auditados. El almacenamiento privado necesita volumen persistente al integrar en producción.

La consulta de Comunidad incorpora la foto con select_related; no hace una consulta SQL por autor. No se añadieron sondeos, consultas al login ni cargas de imágenes externas de referencia.

## Demo compartida y código de producción

La demo utiliza transporte en memoria y datos ficticios. Su selección de foto se convierte localmente a una miniatura PNG y se borra al reiniciar; no envía la imagen a un servidor. Esta simulación es distinta de la normalización WebP del backend real.

Se usa image_picker del equipo Flutter para Android y navegador: https://pub.dev/packages/image_picker. Se abre la galería, sin añadir una solicitud de cámara. La selección interrumpida de Android no se recupera automáticamente para otra cuenta. La validación física de galería/recuperación sigue pendiente en el punto 14.

## Referencia y criterios

El ZIP de referencia se inspeccionó como HTML e imagen, sin ejecutar su contenido ni descargar sus fotografías remotas. Se conservaron imagen principal, círculos de acción y cuadrícula de color; se adaptaron al contenido y a los permisos existentes. Del resumen de los 17 vídeos se aplicaron jerarquía, proximidad, menos texto repetido, datos separados por nivel y una acción principal. El texto de detalle no se elimina por razones estéticas.

## Integración por integrantes

1. José: módulo 01; revisar modelo, API y migración core.0016 en la base local, junto con migraciones previas. Ejecutar pruebas antes de integrar. No migrar Railway directamente desde el ZIP.
2. Majo: módulo 02; flutter pub get, análisis y pruebas. El selector requiere reconstruir la app; una recarga en caliente no incorpora un nuevo plugin nativo.
3. Sally: módulo 03; guía, documentación y presentación de auditoría. Revisar los parches antes de aplicarlos sobre modificaciones ajenas.

Se conservan los cambios locales, sin commits, ramas ni publicaciones del repositorio oficial. La publicación separada corresponde únicamente a la demo Sites.

## Verificación y límites

Consultar validacion.json y los registros de este bloque para los resultados definitivos. Navegador CUA desconectado; no se afirma revisión visual manual, instalación del APK ni prueba física de TalkBack. Un intento de render aislado se interrumpió al no completar; no se presenta como captura del emulador.

## Estado de la tabla

12 de 14 puntos cerrados en implementación = 85,71 %. Pendientes: 9 (fotografías comerciales autorizadas y aceptación de la composición de tienda) y 14 (aceptación visual integral, dispositivo físico, accesibilidad y entorno real). La composición horizontal de tienda se adelantó en este bloque, sin declarar completas sus fotografías.
