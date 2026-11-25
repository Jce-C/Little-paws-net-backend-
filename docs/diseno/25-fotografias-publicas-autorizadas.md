# Fotografías públicas autorizadas · backend

Revisión local del 19 de noviembre de 2026. La API y el almacenamiento están implementados; la carga/retirada del panel y el consumo móvil ya están integrados, según las guías 26 y 27. El APK sigue mostrando marcadores cuando no hay una foto publicada. No se publicaron fotografías reales ni se desplegó este bloque.

## Autorización y trazabilidad

Una foto tiene una relación explícita con la mascota y la fundación que confirmó su publicación, mediante FotoPublicaMascota. No se reutiliza DocumentoPrivado, DocumentoAdjunto ni ArchivoDigital del expediente. El operador debe confirmar que tiene autorización para publicar; el servidor no infiere esa autorización por tener un archivo.

Se reutiliza el permiso `mascotas.publicar_adopcion`, en el contexto de la organización con custodia actual. No se exige un nombre de rol específico: se comprueba el permiso efectivo y la pertenencia/contexto con el motor RBAC existente. La mascota debe continuar disponible según disponibles_adopcion(). Se registra quién publica o retira, la mascota, organización, fecha y dimensiones/peso; no se copian los bytes ni metadatos personales a auditoría.

La autorización se comprueba antes de procesar una imagen y se repite bajo bloqueo de seguridad antes de escribir, para respetar una revocación que ocurra durante la normalización. Una publicación retirada, una mascota que deja de estar disponible, una organización no verificada/desactivada o un cambio de custodia hacen que una nueva consulta de la foto devuelva 404. Esto no elimina copias que alguien ya haya descargado de una fotografía pública.

## Rutas

| Método y ruta | Comportamiento |
| --- | --- |
| POST /api/mascotas/{id}/foto-publica/ | Multipart con archivo y confirmar_publicacion=true. Requiere cuenta y permiso/contexto. Devuelve URL relativa, ancho, alto y bytes. |
| DELETE /api/mascotas/{id}/foto-publica/ | Retira la publicación actual y agenda el borrado del archivo tras confirmar la transacción. |
| GET /api/adopcion/mascotas/{id}/foto/ | Consulta pública solo si siguen cumpliéndose las reglas de publicación y custodia. |

Las cargas se limitan a 10 intentos/minuto por usuario con un scope propio; la retirada no consume ese cupo. El limitador de DRF usa la caché configurada: un despliegue con varias réplicas necesitará una caché compartida para coordinar el límite.

## Imágenes y almacenamiento

Se incorpora Pillow 13.0.0 fijado en requirements.txt. Se comprueban los bytes, no solo extensión o MIME declarado: JPEG, PNG o WebP fijos, hasta 5 MB, 16 megapíxeles y 6000 px por lado. Se rechazan animaciones, SVG/PDF, contenido truncado y advertencias de descompresión. Se verifica, decodifica, corrige orientación y crea una imagen nueva de píxeles, sin EXIF, XMP ni perfil ICC del original.

La salida es WebP de hasta 1280 px por lado y 512 KiB. El original no se almacena. Se usan claves aleatorias, sin nombres ni rutas aportados por el usuario, bajo `LPN_PRIVATE_ROOT/pet-photos`. El GET no expone esa ubicación y responde con image/webp, no-store y nosniff. También los errores 404 del GET llevan no-store.

El archivo nuevo y sus metadatos se coordinan con la auditoría: si falla, se revierte la fila y se retira el archivo recién escrito. Al reemplazar se elimina el anterior tras el commit. Si el disco impide limpiar un archivo obsoleto, se registra un aviso; deja de ser accesible por la ruta pública, pero requiere limpieza de almacenamiento.

Referencias primarias: [verificación y límites de Pillow](https://pillow.readthedocs.io/en/stable/reference/Image.html), [seguridad de Pillow](https://pillow.readthedocs.io/en/stable/handbook/security.html).

## Instalación y evidencia

José Carlos debe integrar el parche de modelo/configuración/dependencia y la migración `animals.0007_foto_publica_mascota`, junto con las rutas y archivos nuevos. Instalar requirements.txt y ejecutar migrate en su base local revisada. La migración agrega una tabla vacía y no convierte archivos anteriores en fotografías públicas. Se aplicó exclusivamente a MySQL QA local.

La regresión completa pasa 303 pruebas Django; 13 son específicas de fotos. Cubren autorización, otro contexto, revocación durante procesamiento, confirmación, formato/peso/dimensiones/animación, eliminación de metadatos, disponibilidad/custodia, retirada, sustitución, rollback de auditoría límite de cargas y errores de disco con respuesta 503 sin revelar rutas. No hay migraciones pendientes por generar. Evidencias en output/adopcion-movil: backend-fotos-publicas-20261119.log, backend-fotos-regresion-20261119.log y validacion-fotos-publicas-20261119.json. Los ensayos usan fichas sintéticas e imágenes de colores en directorios temporales que se eliminan.

## Continuidad y publicación

1. Sally: formulario de publicación/retirada en una pantalla del panel, con confirmación clara, vista previa y permiso efectivo. No usar una casilla premarcada como autorización.
2. María José: integración de catálogo/ficha completada en la guía 26; conservar carga diferida, validación y alternativa al error. Las mascotas sin descriptor no generan peticiones de foto.
3. José Carlos: integrar/regresar los cambios y verificar almacenamiento persistente, respaldo y restauración antes de admitir fotos reales. LPN_PRIVATE_ROOT permite configurar una ruta privada del volumen; si se omite o está vacío conserva .private-data. No alojarla en static ni en un directorio servido directamente. Railway no se modificó.
4. Verificar comportamiento de caché/retirada en móvil y consumo de red con fotos autorizadas de una organización piloto. No se insertan imágenes ficticias en fichas reales para aparentar este recorrido.

El permiso existente mantiene su alcance; no se agregan concesiones por defecto ni se cambia el modelo de roles. Los tres módulos siguen separados, sin commits, ramas ni publicación.


### Aislamiento del ensayo

Un reintento con la base conservada encontró registros residuales de otros escenarios (recuentos y nombres duplicados); no se atribuye la causa al flag sin investigarla. Se conserva backend-fotos-regresion-contaminada-20261119.log como diagnóstico local. La aceptación completa se realiza recreando y eliminando exclusivamente el esquema de tests MySQL aislado mediante `test --noinput`, después de comprobar que no haya otro runner activo. No se borró el esquema QA de aceptación ni una base real. Sigue pendiente investigar la limpieza entre suites que reutilizan esquema.

Actualización: la carga/retirada visual del panel se completó en la guía 27; las notas anteriores describen el corte de esa etapa. La publicación productiva permanece pendiente.
