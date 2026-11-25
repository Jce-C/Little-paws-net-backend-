# Modelo V2 del primer proceso: reporte → rescate → expediente

Estado: modelo y migraciones aplicados al esquema nuevo `little_paws_net_v2`. Hay API inicial de reporte y aceptación, pero faltan pruebas completas y endpoints de los demás procesos.

## Relaciones principales

- `Usuario 1:N Reporte`: opcional en el reporte anónimo; para este se exige `codigo_gestion_hash` y nunca se almacena la clave en claro.
- `Reporte 1:0..1 ReporteUbicacion`: latitud/longitud validadas; MySQL deriva `punto POINT SRID 4326` e índice espacial.
- `Zona 1:0..1 ZonaGeografica`: WKT de multipolígono; MySQL deriva geometría SRID 4326 e índice espacial.
- `Fundacion N:M Zona` por `FundacionZona`: cobertura declarada; el servicio deberá comprobar intersección espacial real, no solo pertenencia a una ciudad.
- `Reporte 1:0..1 CasoRescate`: `id_reporte` es FK única. Un caso corresponde a una fundación verificada y tiene historial de estados.
- `Reporte 1:N HistorialEstadoReporte` y `CasoRescate 1:N HistorialEstadoCaso`: estructuras de auditoría; la escritura automática aún debe implementarse en el servicio/transacción.
- `Mascota 1:N Reporte`: un reporte puede no tener mascota registrada al crearse; la fundación podrá identificarla después. La relación caso–mascota se obtiene por `CasoRescate → Reporte → Mascota`.
- `Mascota 1:N CustodiaMascota`, `Fundacion 1:N CustodiaMascota`, `CasoRescate 1:N CustodiaMascota`: conserva periodos de custodia. Una columna generada con índice único impide dos custodias vigentes para la misma mascota.
- `Mascota 1:N AutorizacionExpediente`, `Veterinario 1:N AutorizacionExpediente`: autorización específica con vencimiento y revocación, otorgada por usuario legitimado según custodia vigente.
- `Mascota 1:N CodigoQRExpediente`: tokens regenerables, guardados solo como hash, con vencimiento y revocación. El QR no es permiso de escritura.
- `Mascota 1:N HistorialMedico`: veterinario interno verificado o profesional externo documentado y verificado por usuario interno; ambas modalidades quedan diferenciadas por restricción.
- `EntidadVerificable 1:N SolicitudValidacion 1:N DocumentoValidacion`: documentos privados para verificar fundaciones y profesionales; el estado vigente de verificación vive en `EntidadVerificable`.

## Garantías que ya cubren las migraciones

PK/FK y unicidad de `CasoRescate.id_reporte`; rangos de coordenadas; vigencia temporal de autorización, QR, custodia y caso; una sola custodia abierta por mascota; SRID 4326 e índices espaciales; consistencia básica del veterinario interno/externo; presencia de hash para reporte anónimo.

## Reglas que todavía requieren servicios y pruebas

La base por sí sola no valida que un `ValorMaestro` pertenezca al tipo de catálogo esperado, que la fundación esté verificada y tenga un miembro autorizado, ni que la fundación del caso coincida con la custodia. Un primer servicio transaccional `aceptar_reporte` ya valida reporte pendiente, verificación, membresía/permiso, cobertura y capacidad; crea caso e historiales en una sola transacción. **No está probado aún contra las tablas permanentes ni expuesto por API.** Faltan los servicios de custodia, cambios posteriores de estado y autorización médica.

## Verificaciones realizadas sin alterar el esquema permanente

- `manage.py check --database default`: sin incidencias.
- `makemigrations --check --dry-run`: sin cambios pendientes.
- `sqlmigrate` mostró el DDL espacial y la restricción de custodia esperados.
- MySQL 8.0.46 aceptó `POINT` y `MULTIPOLYGON` generados con SRID 4326 e índices espaciales. Una primera carga demo reveló ejes invertidos en la consulta espacial; la carga se revirtió íntegramente y se corrigió la expresión del punto en una migración nueva. `ST_Intersects` devolvió 1 para la coordenada de Bogotá dentro del polígono demo.
- Dos pruebas existentes sin base de datos pasaron; todavía faltan pruebas de integración y migración en esquema aislado.
