# Little Paws Net V2: decisiones previas al backend

Estado: decisiones de diseño cerradas el 7 de octubre de 2026 para continuar la implementación. Fuente visual: Lucid «Little Paws Net — BDOR ampliado (referencia 3FN) V.2» (54 entidades antes de las ampliaciones). Fuentes de requisitos: «Little Paws Net - Revisado segun retroalimentacion E1.docx» e «Informe y Seguimiento - Little Paws Net actualizado.docx». La base SQL antigua no se reutiliza.

## Autoridad de cada artefacto

1. Los RF/RNF aprobados describen el comportamiento esperado.
2. Lucid V.2 describe la estructura objetivo, pero debe corregirse si no soporta un RF o una restricción real de Django/MySQL.
3. Los modelos Django y las migraciones versionadas crean una base MySQL nueva y vacía.
4. Las pruebas de aceptación verifican que la API cumpla los RF. Workbench solo inspecciona la base; no modifica tablas gestionadas por Django.

Ningún documento anterior que mencione la tabla `Administrador`, un único `id_usuario_responsable` por entidad o QR sin expiración se considera esquema vigente.

## Decisiones de negocio adoptadas

| RF | Regla aprobada para implementar | Cambio de modelo o control |
| --- | --- | --- |
| RF-03 y RF-04 | La validación de fundaciones, clínicas y veterinarios se sustenta en documentos privados; un profesional no opera hasta que su identidad y matrícula estén verificadas. | Crear `DocumentoValidacion` ligado a `SolicitudValidacion`, `ArchivoDigital` y usuario cargador. No reutilizar `DocumentoAdjunto`, que pertenece a mascotas. |
| RF-08 | El QR identifica el expediente, pero no autoriza escribir. Puede regenerarse, expirar y revocarse. Solo un veterinario verificado y autorizado para esa mascota escribe directamente. | Mantener `AutorizacionExpediente`; agregar custodia vigente para saber quién puede otorgar acceso. Un profesional externo sin cuenta verificada no escribe: un usuario autorizado registra su atención y la verificación. |
| RF-10 y RF-13 | El anónimo recibe una clave privada de gestión mostrada una sola vez. La API guarda únicamente su hash, no la clave en claro. Editar/cerrar requiere esa clave o moderación administrativa. | Añadir credencial de gestión al reporte, separada del ID público; limitar intentos y no exponer la clave en URL, registros ni respuestas posteriores. |
| RF-15A | La referencia externa es una declaración opcional del padrino; no confirma recepción. Se permiten varias declaraciones para aportes parciales. | Crear `DeclaracionTransferencia` ligada a `Apadrinamiento`; referencia cifrada o protegida, fecha, monto declarado y evidencia privada opcional. `ConfirmacionAporte` seguirá siendo una acción exclusiva de la fundación receptora. |
| RF-16 a RF-18 | La fundación declara cupos totales y ocupados; el radar muestra cobertura y capacidad. No hay asignación automática. Una aceptación voluntaria con cupos agotados requiere justificación registrada, en vez de bloquear un rescate urgente. | Crear `CapacidadFundacion` 1:1 con `Fundacion`; validar 0 ≤ ocupados ≤ totales y registrar actor/fecha. La aceptación usa transacción y comprobación de permisos. |
| RF-20 y RF-21 | La ubicación del animal en adopción es la de la fundación que tiene la custodia vigente, no la zona de cobertura ni una ciudad supuesta. | Añadir `Fundacion.id_ciudad` y `CustodiaMascota` con inicio/fin, mascota y fundación. Si no hay custodia vigente, la ciudad figura como desconocida y no aparece en filtros por ciudad. |
| RF-26 | El fondo externo tiene entidad administradora, tipo y estado explícitos. Little Paws Net no administra saldos ni confirma movimientos bancarios. | Añadir `entidad_administradora`, `id_tipo_fondo` e `id_estado_fondo` a `FondoExterno`. |
| RF-27 y RF-27A | Cada solicitud publicitaria tiene estado y revisión administrativa; solo una pieza aprobada se publica. Las alianzas clínicas guardan nivel, tarifa, vigencia y estado. | Ampliar `EspacioPublicitario` con estado, revisor y fecha de decisión; ampliar `AlianzaVeterinaria` con nivel, tarifa, fechas y estado. |
| RNF-07 | La notificación interna se crea al registrar el evento; la entrega externa es asíncrona y se mide por separado. La meta inicial medible es que el 95 % de notificaciones internas sea consultable en 30 segundos bajo carga de prueba definida. | Usar transacción más cola/outbox para canales externos; no prometer WhatsApp/correo como envío sin integraciones configuradas. |

La custodia vigente corresponde al dueño registrado cuando la mascota está bajo su cuidado, o a la fundación con un periodo de `CustodiaMascota` abierto cuando está bajo rescate. Si hay un conflicto entre ambos registros, el sistema bloquea la autorización médica hasta resolver la custodia; no concede acceso por simple posesión del QR.

## Seguridad y alcance técnico

- Los endpoints Android usarán tokens de acceso de vida corta y renovación revocable; el correo y la contraseña son las credenciales iniciales. No se usarán sesiones del administrador para autenticar la aplicación móvil.
- Los documentos legales, datos médicos y referencias de transferencias serán privados. `ArchivoDigital` deberá registrar clave de almacenamiento, tipo MIME, tamaño, visibilidad y cargador; la API entregará acceso controlado, no URL pública permanente.
- Las cuentas bancarias y referencias externas se cifrarán con una clave de aplicación fuera del repositorio y de la base de datos. Las pantallas públicas no mostrarán esos campos.
- El MVP implementa el proceso completo reporte → aceptación voluntaria → rescate → expediente, con cobertura/capacidad. Adopción, fondo externo, publicidad y comercio se modelan y se implementan después por procesos; no se declaran funcionales antes de sus pruebas.

## Ajustes técnicos para Django que deben reflejarse en Lucid

- `Usuario` será un modelo personalizado definido antes de la primera migración. Django almacenará y verificará su hash de contraseña; no habrá un segundo campo gestionado manualmente para autenticación.
- El usuario técnico `is_superuser` sirve solo para mantenimiento del sitio interno de Django. Los permisos de los procesos de Little Paws Net dependerán de `Rol`, `Permiso`, `UsuarioRol` y `EntidadMiembroRol`; no se usarán `auth.Group` ni `auth.Permission` como una segunda fuente de autorización de negocio.
- Para conservar integridad con ORM estándar, `EntidadMiembro` tendrá una PK simple `id_entidad_miembro` y restricción única sobre `(id_entidad_verificable, id_usuario)`. `EntidadMiembroRol` referenciará la membresía por esa PK. El diagrama se actualizará antes de darlo por definitivo.
- Las tablas puente restantes usarán PK simples y restricciones únicas equivalentes, salvo una justificación para conservar una PK compuesta. Esto evita limitaciones de Django admin y relaciones hacia PK compuestas.
- `Fundacion`, `Clinica`, `Veterinario`, `Tienda` y `Anunciante` mantendrán relación 1:0..1 con `EntidadVerificable`; se elegirá una implementación explícita y comprobable, no herencia Python automática sin revisar el SQL producido.
- Para V2 sobre MySQL 8.0 se eligieron columnas espaciales nativas en migraciones `RunSQL`, derivadas de coordenadas y WKT administrados por Django. Así no se bloquea el MVP por GDAL/GEOS; GeoDjango queda como alternativa si se cambia la infraestructura. Las columnas generadas usan SRID 4326 e índices espaciales.
- Comprobación local posterior: MySQL 8.0.46 aceptó `POINT` y `MULTIPOLYGON` generados con SRID 4326 e índices espaciales. La primera prueba integrada encontró que `POINT(latitud,longitud)` no intersectaba un polígono esperado; se corrigió con una migración adicional a `POINT(longitud,latitud)`, comprobando `ST_Intersects=1`. El WKT de zona sigue importándose con `axis-order=long-lat`. Las migraciones sí se aplicaron al esquema nuevo V2; la base antigua no se tocó.
- Valores monetarios usarán Decimal; eventos se registrarán con zona horaria; estados tendrán validación de transiciones además de integridad referencial.

## Orden de construcción

1. Cerrar decisiones de negocio anteriores y actualizar RF/RNF.
2. Congelar inventario de modelos, FK, restricciones y responsables.
3. Preparar proyecto, entorno, configuración y base MySQL nueva vacía.
4. Crear usuario personalizado y modelos compartidos; revisar migración inicial.
5. Implementar reporte → aceptación voluntaria → caso → expediente (MVP).
6. Implementar apadrinamiento, adopción, fondo externo y comercio por procesos completos.
7. Añadir endpoints DRF, permisos, transacciones, pruebas y documentación de API.
8. Probar instalación desde cero con migraciones y contrastar esquema real con Lucid.

## Criterio de no reutilización

No ejecutar `database/little_paws_net_mysql.sql`, scripts demo antiguos ni `inspectdb` para construir V2. No ejecutar `migrate --fake-initial` sobre la base anterior. Los datos existentes permanecen intactos, pero no forman parte del backend nuevo.
