# 62 · Descripción y cuidados individualizados para adopción

22 de noviembre de2026. Cierre técnico del punto5 de la tabla. Entorno real y aceptación integral siguen registrados en14.

## Resultado visible

- Tarjeta: descripción breve publicada y atributos de edad/sexo/tamaño fuera de la foto, sobre una etiqueta suave. La altura se mide con texto ampliado y hasta dos líneas por dato; el detalle mantiene el texto completo.
- Ficha: sección **Sobre esta mascota** y requisitos con **espacio** y **cuidados publicados para esa mascota**. No se sustituye descripción por especie/raza.
- Solicitud: repite esos requisitos individualizados antes del formulario. Responsabilidad y recursos siguen explicados. Enviar/cancelar permanecen en el área fija, incluso con texto ampliado.
- Si faltan cuidados publicados, se indica que deben consultarse: no significa que la mascota no los necesite. No se inventan diagnóstico, tratamiento, vacunación o esterilización.
- Fotos, galería, estado de adopción, límites de sesión y envío de solicitudes se conservan. La prueba de galería existente cubre varias imágenes; faltan datos consentidos y piloto real en14.

## Cómo administrar la presentación

1. Entrar con permiso **`mascotas.publicar_adopcion`** en la fundación que tenga la custodia vigente.
2. Abrir **Mascotas → Fichas autorizadas → Presentación para adopción**.
3. Escribir personalidad/descripción, cuidados públicos y espacio recomendado. La descripción admite1000 caracteres, cuidados2000 y espacio600.
4. Guardar sin marcar publicación conserva un borrador privado para esa fundación.
5. Para publicar, marcar publicación y autorización. La mascota debe estar disponible para adopción.
6. Para retirar los textos, desmarcar publicación y guardar. La mascota puede continuar disponible; sus textos dejan de devolverse públicamente.
7. Cancelar vuelve al listado; el mecanismo compartido de cambios sin guardar permanece activo.

Se deben escribir textos revisados y autorizados para el público. El servicio no lee ni copia el expediente veterinario, documentos privados o datos de personas. La autorización no convierte automáticamente cualquier contenido clínico en información publicable.

## Contrato y trazabilidad

Modelo **PresentacionPublicaMascota** separado, ligado a mascota y fundación autorizante. Migración **animals.0009_presentacionpublicamascota** aplicada solo en la base aislada de pruebas. Depende de animals.0008 y core.0012.

`GET/PUT /api/mascotas/<id>/presentacion-publica/` permite gestionar la presentación bajo el permiso de custodia. El PUT reemplaza los campos completos, exige un booleano de publicación y confirmación explícita para publicar.

La ficha pública y el catálogo paginado añaden `presentacion`, con tres campos editoriales (`descripcion`, `cuidados`, `espacio`) o `null`. No incluye editor, borrador, permisos ni información clínica privada. Los clientes y fichas anteriores sin este campo siguen siendo compatibles.

La consulta comprueba publicación y fundación actual; cambiar de organización no publica ni revela el borrador de la anterior. El guardado vuelve a comprobar permisos bajo transacción y bloqueo compartido de seguridad. La revocación de un cargo impide la siguiente edición. Si la mascota deja de estar disponible, su ficha pública deja de servirse.

La auditoría distingue publicar, actualizar, retirar y guardar borrador, con actor, fecha, organización y valores anteriores/nuevos. Se añadieron traducciones inglesas de formulario y eventos. El panel usa POST con CSRF y validación de servidor; no necesita JavaScript para publicar.

El catálogo incorpora la relación editorial mediante join. La prueba compara uno y dos registros: añadir una presentación no añade una consulta por mascota. Las respuestas siguen con no-store. La ficha requiere un GET de datos, sin descargar el expediente.

## Pruebas y evidencia

**212 pruebas Flutter canónicas**, análisis limpio; **214 de demo**, análisis limpio. Cuatro regresiones nuevas cubren campos/longitudes/compatibilidad, descripción y cuidados en el detalle con un solo GET, y cuidados en la solicitud a320px/texto2× sin peticiones antes del envío explícito. Los límites Unicode se cuentan por puntos de código, compatibles con el backend. La cuarta regresión comprueba que «Ver detalles» queda alineado entre tarjetas con y sin descripción.

**76 pruebas backend de regresión**: presentación, ficha, paginación, fotos, galería, formulario web y actividad. Incluyen borrador/retirada, consentimiento, campos extra privados rechazados, permiso por fundación, revocación y traslado de custodia. Las expectativas de whitelist se actualizan solo para el campo editorial nuevo.

Los logs iniciales se conservan. Se corrigieron una puntuación semántica añadida a fichas legacy sin descripción y dos problemas de fixtures (codificación UTF-8 y selección del scroll vertical en pruebas). La descripción individual se anuncia sin cambiar el nombre accesible de registros legacy.

Publicación, hashes y capturas definitivas están en `output/adopcion-editorial-2026-11-22/validacion.json`. La demo contiene una presentación **explícitamente ficticia** para Max y conserva otras mascotas sin presentación para comprobar el estado vacío. No se publican datos de mascotas reales ni se conecta la demo a escrituras reales. El backend productivo y su migración continúan pendientes de integración revisada.

## Porcentaje y siguiente punto

Al cerrar5 quedan implementados **1,2,3,4,5,10,11,12 y13: 9/14 =64,3 %**. El registro porcentual definitivo está en `estado-tabla.json`. Pendientes6,7,8,9 y14. El siguiente bloque es actividades de ayuda y canales oficiales administrables, sin inventar cuentas ni cobrar dinero.

## Reparto

José Carlos: modelo, migración, servicio, API, autorización y pruebas. Majo: datos del cliente, tarjetas, detalle, solicitud y regresiones. Sally: formulario web, mensajes, traducciones, guía y evidencia visual. Paquetes locales separados; sin commits/ramas oficiales, sin Railway ni sobrescritura del Figma manual.
