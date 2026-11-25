# 59 · Fotografías públicas de productos y avance global

Fecha: 21 de noviembre de 2026. Implementación local, sin commits ni despliegue oficial.

## Resultado

El catálogo comercial ya tiene un recorrido para publicar, reemplazar y retirar una fotografía autorizada. La tarjeta y el detalle móvil muestran esa imagen, con ajuste que conserva el producto completo. Si falta una foto o sus metadatos son inválidos, la información y la acción del producto siguen disponibles con un marcador explícito. Si falla la carga, aparece una opción de reintento.

No se publica automáticamente ningún `ProductoImagen` ni `ArchivoDigital` existente: pueden contener información privada. `FotoPublicaProducto` guarda una copia pública normalizada y el contexto de la tienda que la autorizó. No se han añadido imágenes comerciales ficticias a registros reales.

## Uso en el panel

1. Entrar con permiso `producto.gestionar` en la tienda correspondiente. Los roles son configurables: no depende del nombre del rol.
2. Ir a **Catálogo y existencias**. Cada fila autorizada ofrece **Fotografía**.
3. Elegir JPEG, PNG o WebP; confirmar la autorización y pulsar **Publicar fotografía**. Seleccionar un archivo o marcar la confirmación no lo publica automáticamente.
4. La pantalla muestra dimensiones y peso. Repetir el proceso reemplaza la copia anterior.
5. Para retirar, pulsar **Retirar fotografía**, confirmar y enviar. También se puede cancelar y volver al catálogo.

El formulario usa controles nativos, etiquetas, ayuda persistente, protección CSRF y POST explícito. No requiere JavaScript para funcionar. Los textos nuevos de la pantalla y los eventos tienen traducción inglesa.

## Contratos y límites

- `POST /api/catalogo/productos/<id>/foto-publica/`: multipart con `archivo` y `confirmar_publicacion=true`; devuelve 201.
- `DELETE` en esa misma ruta retira la publicación; devuelve 204.
- `GET /api/catalogo/productos/<id>/foto/`: entrega solo WebP autorizado.
- `GET /api/catalogo/productos/`: incluye `foto` opcional con URL relativa versionada, ancho, alto y bytes. Sigue siendo compatible con productos sin foto.
- Entrada: máximo 5 MB, imagen fija JPEG/PNG/WebP, hasta 16 megapíxeles y 6000 px por lado. Salida: hasta 1280 px por lado y 512 KB, sin EXIF, XMP ni ICC del original.
- Una normalización compartida sirve a mascotas y productos; no se cambia la autorización de adopción.
- Se comprueba permiso por tienda antes de procesar y de nuevo dentro de la transacción. Una revocación durante la normalización impide publicar.
- El GET comprueba publicación, tienda actual, disponibilidad del producto, verificación y bajas administrativas. Un traslado a otra tienda no hereda su foto anterior.
- La retirada impide nuevas consultas y elimina la copia después de confirmar la transacción. No puede eliminar copias descargadas previamente. El catálogo debe recargarse para actualizar una vista móvil ya abierta.
- La API pública no acepta rutas de archivos privados ni URL externas. La app valida ruta exacta del producto, versión y límites antes de solicitar una imagen.
- El catálogo obtiene productos y metadatos de fotografías en una consulta SQL en la prueba; no procesa imágenes durante el listado.

## Integración pendiente de publicación

Existe una nueva migración `commerce.0003_fotopublicaproducto`. Solo se ha aplicado en la base aislada de pruebas. Para publicar: revisar el diff, respaldar la base del entorno elegido, integrar código/migración y verificar un volumen persistente para `LPN_PRIVATE_ROOT/product-photos`. Un contenedor efímero no conserva los archivos después de un despliegue. No se ha modificado Railway ni el sitio público de demostración en este bloque.

## Comprobaciones

54 pruebas backend: comercio, fotos comerciales y de mascotas, formularios web y presentación de actividad. Incluyen autorización por tienda, confirmación, CSRF, revocación durante subida, imágenes falsas, retirada, cambio de tienda, indisponibilidad, pérdida de verificación y fallo del almacenamiento.

199 pruebas Flutter y análisis sin incidencias. Las nuevas regresiones comprueban rutas ajenas/privadas/externas, parámetros duplicados y rutas con `..`, límites de metadatos y compatibilidad de la tarjeta sin foto con texto ampliado. Se corrigió la primera prueba que detectó normalización permisiva de `..` antes de aceptar la ruta.

Los resultados y compilación Android están en `output/fotos-productos-2026-11-21/validacion.json`. No equivalen a aceptación con usuarios reales, certificación de accesibilidad ni medición de producción.

## Evaluación del conjunto

Estimación orientativa: **7/10 global**; diseño **8/10**, funcionamiento **7/10**, preparación para uso real **5/10**. No es una certificación ni un porcentaje calculado a partir del número de pruebas. Este bloque resuelve el código de fotos comerciales, pero falta su publicación y validación con datos autorizados.

Pendientes principales del alcance acumulado:

1. Ficha pública administrable de organizaciones: logo, servicios y contactos autorizados explícitamente.
2. Descripción editorial y cuidados particulares por mascota, sin extraer información clínica privada.
3. Actividades concretas de voluntariado y canales oficiales de aportes. Los compromisos registrados no son pagos recibidos.
4. Recuperación de contraseña móvil y mejoras restantes de carga/error.
5. Piloto con datos consentidos, fotos reales de productos y galerías de animales; aceptación con los tres integrantes.
6. Revisión en dispositivo físico, TalkBack, estados móviles y validación operativa de permisos entre sesiones.
7. Integración por integrantes, despliegue controlado, respaldo/restauración y prueba de persistencia de archivos.
8. Cierre de evidencias, versión y entregable académico; sin crear todavía commits o tags por cuenta del grupo.

## Reparto

José Carlos: modelo, migración, normalización, API, RBAC y pruebas. Majo: imagen de tarjeta/ficha móvil y regresiones. Sally: pantalla web, textos, traducciones y guía. Los paquetes se revisan antes de copiar sobre cambios ajenos.
