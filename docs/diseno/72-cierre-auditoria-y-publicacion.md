# Guía 72 · Cierre de auditoría y preparación de publicación

Fecha: 24 de noviembre de 2026. Cambios locales del repositorio oficial, separados para tres integrantes. No se ha migrado ni reactivado Railway.

## Correcciones implementadas

| Hallazgo | Corrección | Prueba de cierre |
|---|---|---|
| A71-01 | Tarjeta común con foto o marcador, estado, ciudad y resumen en listado público, Mis reportes e Historias. | Widget y navegador con API real local. |
| A71-02 | Clave UUID por alta personal; recibo SQL ligado al usuario y operación. Comprobar registro repite la misma operación; acceso a Mis mascotas. | Respuesta perdida antes/después de guardar; misma clave no duplica. |
| A71-03 | Mismo circuito para compromisos; historial privado paginado en Mis compromisos y acceso a cuenta receptora. | Reintento, cambio de datos409, cuenta tras fallo de lectura sin repetir el POST. |
| A71-04 | Edad tipada y normalizada en JSON/multipart de demo; cálculo ajustado al último día del mes. | Alta sin foto y consulta posterior. |
| A71-05 | Mis reportes vuelve a exigir reportes.participar en cada GET. | Revocación devuelve403; sigue filtrando por titular. |
| A71-06 | Mis reportes y Mis compromisos llevan no-store también en errores. | Cabeceras y consultas reales. |
| A71-07 | ReadableText usa texto estático seleccionable; reemplaza SelectableText en datos de consulta. | Sin controles editables deshabilitados; navegador expone números y valores. |

Se corrigieron además los reintentos que devolvían un Future dentro de setState y el nombre de archivo multipart sin extensión. Este último impedía guardar la foto real aunque los mocks y la vista previa funcionaran. La carga desde el navegador ahora se guardó en MySQL y se recuperó como WebP de36118bytes,773×434px y sin EXIF.

## Integrar en orden

1. José: integrar módulo01, revisar core.0017_operacion_ciudadana, modelos/helper y endpoints. Mantener las migraciones anteriores de la guía71. Ejecutar migraciones y pruebas primero en MySQL aislado, sin usar --fake. Publicar backend antes del cliente nuevo.
2. Majo: integrar módulo02, revisar API y pantallas; ejecutar pub get, analyze y test. Configurar LPN_API_BASE_URL con la URL del entorno correcto. La capacidad reintentos_seguros en el perfil evita habilitar reenvíos contra un servidor anterior que ignore la clave.
3. Sally: integrar módulo03, revisar las evidencias y repetir aceptación visual, lectura y dispositivo. Registrar por separado los cambios de documentación, diseño y QA que correspondan al reparto acordado.
4. Crear cada commit/PR después de revisar el diff. No aplicar a ciegas parches acumulados sobre un estado diferente. Los ZIP son una propuesta revisable, no un permiso para sobrescribir trabajo ajeno.

No se han hecho commits en el repositorio oficial. La demo Sites conserva su repositorio independiente y datos ficticios. El entorno HTTP real local es una base separada de prueba, no una nueva versión publicada de Railway.

## Recibos de creación

Idempotency-Key acepta un UUID por operación explícita. El backend verifica autorización antes de consultar el recibo, bloquea la fila del actor mientras crea/consulta el recibo y guarda únicamente huella, ID/respuesta y estadoHTTP. No guarda fotos, credenciales ni cuerpo original en el recibo. Misma clave+actor+operación devuelve la respuesta original. Mismos identificadores con datos diferentes devuelven409. No se reutiliza la clave para una nueva acción.

La migración core.0017 crea una tabla; no modifica registros de negocio existentes. No eliminar recibos sin definir un plazo seguro: reutilizar una clave después de purgarla puede volver a crear datos. La retención de recibos y límites de uso deben acordarse antes de operación masiva.

## Publicación Android

El APK debug sirve para QA. Una publicación comercial necesita firma privada, versión definitiva, URL HTTPS operativa, política de privacidad y pruebas en dispositivo.

Se retiró la firma debug del build release del cliente real. El build falla con un mensaje claro si falta android/key.properties o su almacén privado. Copiar android/key.properties.example como key.properties y completar únicamente en la computadora del responsable. No compartir la clave, no incluirla en ZIP/Git y mantener respaldo privado. No se ha generado una identidad de firma por decisión unilateral.

La aplicación release no permite tráfico HTTP; el permiso de HTTP queda limitado al manifiesto debug para desarrollo local. No distribuir una compilación que apunte a127.0.0.1 ni al dominio antiguo de Railway mientras no esté operativo.

Referencia: https://docs.flutter.dev/deployment/android

## Estado real de Railway

La consulta de metadatos mostró little-paws-panel sin despliegues activos y su último estado FAILED. /api/health/ responde404 Application not found desde el edge. Esto no demuestra que la base o sus volúmenes estén borrados ni que hayan dejado de cobrar. La consulta de uso/facturación no pudo completarse; no se verificó el saldo exacto de7USD.

No se modificaron suscripciones, límites, servicios, facturas ni bases. No se activará un recurso con costo sin un presupuesto acordado. Primero revisar Billing/Usage en la cuenta, respaldar datos y archivos y después decidir continuidad, cancelación o migración. Cancelar no borra una factura ya devengada.

Referencias oficiales: https://docs.railway.com/pricing/faqs y https://docs.railway.com/pricing/understanding-your-bill

## Qué falta para aceptar un producto vendible

| Puerta | Evidencia necesaria | Estado |
|---|---|---|
| Flujos ciudadanos del alcance | Siete hallazgos corregidos, regresión, HTTP y navegador | Implementados; ver resultados de esta revisión |
| Backend en línea | HTTPS, MySQL y almacenamiento persistente operativos | Bloqueado por alojamiento actual |
| Datos y continuidad | Respaldo cifrado y restauración ensayada de BD y fotos; conservar LPN_DATA_KEY | Pendiente |
| Autenticación web duradera | Cookie HttpOnly/Secure, CSRF y origen acordado si se requiere Recordarme persistente | Pendiente; hoy conserva solo la elección |
| Android real | Cámara, galería, permisos denegados, teclado, TalkBack, cambio de cuenta, red lenta y reinicio | Pendiente en dispositivo; no hay equipo conectado |
| Firma y distribución | Clave privada del propietario, AAB firmado, versión y canal de pruebas | Pendiente de clave y aceptación |
| Contenido comercial | Reemplazar toda foto no licenciada/con marca y datos ficticios; organizaciones reales verificadas | Pendiente del propietario y organizaciones |
| Privacidad y soporte | Inventario de datos, consentimiento, eliminación/retención, contacto de soporte y responsables | Pendiente de políticas y validación correspondientes |
| Operación | Alertas, presupuesto máximo, respuesta a incidentes y mantenimiento | Pendiente |
| Aceptación con cliente | Piloto con1organización, alcance firmado, indicadores y respaldo | Pendiente de cliente piloto |

No se presenta como pasarela de pago. Los compromisos y aportes se registran; las transferencias ocurren fuera de la app y necesitan confirmación de la organización.

## Recomendación viable sin dinero ahora

Entregar demo pública ficticia + demostración local con MySQL real + APK de QA + evidencias del repositorio. Para la primera venta, ofrecer instalación, configuración y capacitación de un piloto con alcance reducido. El cliente aporta su servidor o paga el alojamiento directamente; no financiarle infraestructura con la cuenta personal del estudiante. El contrato debe separar implementación, alojamiento y mantenimiento. No prometer disponibilidad24/7 de una computadora personal ni de una demo estática.

Un plan gratuito puede servir a una evaluación temporal, pero hay que comprobar sus restricciones y la base persistente. Render gratuito no aloja sin cambios nuestro MySQL y su PostgreSQL gratuito caduca a30días. PythonAnywhere no incluye MySQL para cuentas gratuitas nuevas. Migrar aPostgreSQL sería otra implementación con pruebas de datos/migraciones, no simplemente cambiar un enlace.

Referencias: https://render.com/docs/free y https://help.pythonanywhere.com/pages/FreeAccountsFeatures/

## Límite de publicación de esta revisión

La actualización web compiló, pero la publicación en Sites no pudo completarse: get_site muestra v20 y el endpoint de credencial de escritura devuelve NOT_FOUND. El enlace conserva v20. Los cambios están preparados en local y en los módulos, sin commits oficiales ni migraciones de Railway.
