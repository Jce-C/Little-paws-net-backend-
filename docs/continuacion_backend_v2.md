# Continuación profesional de Little Paws Net V2

Estado al 7 de octubre de 2026. Esta es una **base nueva**; la base y los scripts SQL de la versión anterior permanecen intactos y no se ejecutan.

## Decisiones adoptadas

1. **Fuente de verdad:** requisitos funcionales aprobados para el comportamiento; modelos Django y migraciones versionadas para el esquema físico; Lucid V.2 como representación que debe mantenerse sincronizada. MySQL Workbench es para administración e inspección, no para editar manualmente tablas gestionadas por Django.
2. **Autenticación y autorización:** correo y contraseña con usuario personalizado de Django. Los roles de negocio son registros de `Rol`, los permisos son registros de `Permiso`, y las membresías de entidad se representan mediante `EntidadMiembro` y `EntidadMiembroRol`. `ADMIN_PLATAFORMA` es un rol global, no una tabla; `is_superuser` queda reservado para administración técnica de Django.
3. **Integridad:** las tablas puente usan PK simple más restricciones `UNIQUE` sobre las columnas de negocio. Esto conserva unicidad y permite FK y administración ORM convencionales.
4. **Rescate:** ninguna asignación automática a fundación. Una fundación verificada acepta voluntariamente; se comprueban membresía, permisos, cobertura y capacidad dentro de una transacción. Cupos agotados requieren justificación registrada para una excepción urgente.
5. **Apadrinamiento y fondo:** la aplicación solo intermedia. Una declaración de transferencia del padrino no acredita recepción; la fundación registra la confirmación. No hay pasarela ni saldo bancario interno.
6. **Expediente y QR:** el QR identifica el expediente, pero no da derecho de escritura. Se exige veterinario verificado, autorización específica vigente y custodia inequívoca. El QR expira y puede revocarse; el veterinario externo no verificado no escribe directamente.
7. **Seguridad:** archivos privados con acceso autorizado; contraseña y códigos secretos solo como hash; tokens móviles de corta duración y renovación revocable; auditoría de cambios sensibles; geolocalización espacial indexada en MySQL 8.
8. **Alcance:** MVP completo reporte → aceptación → rescate → expediente. Los demás procesos se implementan de forma incremental, pero no se presentan como funcionales antes de sus pruebas.

## Cambios concretos pendientes en Lucid V.2

Agregar `DocumentoValidacion` con FK a `SolicitudValidacion`, `ArchivoDigital` y `Usuario` cargador. Agregar `DeclaracionTransferencia` con FK a `Apadrinamiento` y, opcionalmente, a evidencia privada `ArchivoDigital`; distinguirla visualmente de `ConfirmacionAporte`. Agregar `CapacidadFundacion` con relación 1:1 a `Fundacion`, cupos totales y ocupados, fecha y usuario actualizador. Agregar `CustodiaMascota` con FK a `Mascota` y `Fundacion`, fechas de inicio y fin, sin dos custodias vigentes simultáneas para una mascota.

En `Fundacion`, agregar `id_ciudad` FK a `Ciudad`. En `FondoExterno`, agregar entidad administradora, tipo y estado. En `EspacioPublicitario`, agregar estado, usuario revisor y fecha de decisión. En `AlianzaVeterinaria`, agregar nivel, tarifa, fechas y estado. En `Reporte`, representar la clave de gestión anónima únicamente mediante su hash. En `ArchivoDigital`, reflejar clave de almacenamiento, MIME, tamaño, visibilidad y usuario cargador.

En `EntidadMiembro`, usar `id_entidad_miembro` como PK y `UNIQUE(id_entidad_verificable, id_usuario)`. En `EntidadMiembroRol`, conectar la FK `id_entidad_miembro` a esa PK y asegurar unicidad de membresía + rol. Mantener `ADMIN_PLATAFORMA` como dato de `Rol` con ámbito `GLOBAL`, no como entidad independiente ni como permiso derivado de la antigua tabla `Administrador`.

Para el primer proceso, agregar `HistorialEstadoReporte` y conectar `Reporte 1:N HistorialEstadoReporte`. `CasoRescate.id_reporte` es FK **única**: un reporte puede originar como máximo un caso; la misma mascota sí puede aparecer en varios reportes a lo largo del tiempo. `CustodiaMascota.id_caso_origen` es FK opcional a `CasoRescate`; evita duplicar un `id_caso_origen` en `Mascota`, porque la procedencia se reconstruye desde reporte/caso/custodia. `ReporteUbicacion` conserva latitud y longitud validadas y MySQL genera `punto POINT SRID 4326` con índice espacial. `ZonaGeografica` conserva WKT y MySQL genera `geometria MULTIPOLYGON SRID 4326` con índice espacial. Las columnas generadas son físicas, pero no se escriben desde Django.

Para cada enlace, dibujar la FK en la entidad hija y marcar 0..1 cuando admita `NULL`. No dar por definitiva ninguna cardinalidad que contradiga una restricción de la migración. Reservar una zona visual para el MVP y otras para adopción/fondo/comercio, sin duplicar entidades compartidas.

## Orden de trabajo restante

1. Sincronizar Lucid con las decisiones de arriba. El conector de Lucid disponible permite leer y generar documentos, pero **no editar figuras de un documento existente**; esta edición de V.2 requiere intervención en Lucid o reconstrucción de un diagrama nuevo.
2. Preparar el esquema MySQL V2 y la cuenta de aplicación; completar `.env` local. No comunicar contraseñas por chat.
3. Para V2 se adoptó MySQL espacial nativo mediante migraciones explícitas: `ReporteUbicacion.punto` y `ZonaGeografica.geometria` son columnas generadas con SRID 4326 e índices espaciales. Se probó la sintaxis en tablas temporales; queda verificar las migraciones en una instalación limpia y las consultas reales. No se requiere GDAL/GEOS para esta implementación; si en el futuro se decide usar GeoDjango, será un cambio técnico separado.
4. Completar modelos compartidos y de procesos, revisar las migraciones iniciales generadas **sin aplicarlas** hasta congelar el esquema. Después ejecutar `migrate` en el esquema vacío.
5. Cargar catálogos y roles por migraciones de datos idempotentes, nunca con IDs mágicos; implementar servicios de negocio, API DRF, permisos, transacciones, auditoría y pruebas de aceptación.
6. Actualizar RF/RNF y diagramas 3FN/BDOR para que describan el esquema y los controles realmente probados; exportar documentación de API y comprobar instalación limpia desde cero.

## Comprobación actual

`manage.py check --database default` y dos pruebas sin base de datos pasan. Django conecta con MySQL 8.0.46 al esquema nuevo `little_paws_net_v2`, que sigue con **0 tablas**. Hay 36 modelos de proyecto (usuario, comunes, animales, rescate y geografía) y migraciones generadas pero **no aplicadas**. Las columnas espaciales se probaron en tablas temporales; faltan pruebas de migración completa, reglas de servicio y API. Por ello, **todavía no hay backend funcional de extremo a extremo**.
