# Inventario de entidades Lucid V2

Instantánea de la copia BDOR V.2 consultada el 6 de octubre de 2026. Son 54 entidades y 117 conexiones entre entidades existentes. **No es todavía un esquema físico aprobado**: los campos con tipo incompleto y las diferencias con RF se corrigen antes de los modelos finales. La agrupación reproduce el color de Lucid, no implica que cada entidad viva necesariamente en una app Django distinta.

## Compartidas y seguridad (21)

| Entidad | Campos visibles en Lucid |
| --- | --- |
| Anunciante | PK/FK id_entidad_verificable (INT); nit_documento (VARCHAR); descripcion (TEXT) |
| ArchivoDigital | PK id_archivo (INT); url_archivo (VARCHAR); fecha_carga (DATE) |
| Ciudad | PK id_ciudad (INT); nombre (VARCHAR); departamento (VARCHAR) |
| Clinica | PK/FK id_entidad_verificable (INT); FK id_ciudad (INT); direccion (VARCHAR) |
| EntidadMiembro | PK/FK id_entidad_verificable (INT); PK/FK id_usuario (INT); fecha_ingreso (DATETIME); fecha_salida (DATETIME) |
| EntidadMiembroRol | PK/FK id_entidad_verificable (INT); PK/FK id_usuario (INT); PK/FK id_rol (INT) |
| EntidadVerificable | PK id_entidad_verificable (INT); nombre (VARCHAR); FK id_estado_verificacion (INT) |
| Fundacion | PK/FK id_entidad_verificable (INT); nit (VARCHAR); descripcion (TEXT) |
| FundacionZona | PK/FK id_fundacion (INT); PK/FK id_zona (INT); activo (BOOLEAN) |
| Notificacion | PK id_notificacion (INT); FK id_usuario (INT); FK id_tipo_notificacion (INT); contenido (TEXT); fecha_creacion (DATETIME); fecha_lectura (DATETIME) |
| Permiso | PK id_permiso (INT); codigo (VARCHAR); descripcion (VARCHAR) |
| Rol | PK id_rol (INT); nombre (VARCHAR); descripcion (VARCHAR); codigo (VARCHAR); ambito (VARCHAR) |
| RolPermiso | PK/FK id_rol (INT); PK/FK id_permiso (INT); descripcion (VARCHAR) |
| Tienda | PK/FK id_entidad_verificable (INT); FK id_ciudad (INT); direccion (VARCHAR); whatsapp  (VARCHAR) |
| TipoMaestro | PK id_tipo_maestro (INT); nombre (VARCHAR); descripcion (VARCHAR); activo (BOOLEAN) |
| Usuario | PK id_usuario (INT); correo (VARCHAR); nombre (VARCHAR); telefono (VARCHAR); fecha_registro  (DATETIME); password_hash  (VARCHAR) |
| UsuarioRol | PK/FK id_usuario (INT); PK/FK id_rol (INT); fecha_asignacion (DATETIME); fecha_revocacion (DATETIME) |
| ValorMaestro | PK id_valor_maestro (INT); FK id_tipo_maestro (INT); nombre (VARCHAR) |
| Veterinario | PK/FK id_entidad_verificable (INT); registro_profesional (VARCHAR); especialidad (VARCHAR); FK id_clinica (INT); FK id_usuario_profesional (INT) |
| Zona | PK id_zona (INT); FK id_ciudad (INT); nombre (VARCHAR) |
| ZonaGeografica | PK/FK id_zona (INT) |

## José Carlos: reporte, rescate y apadrinamiento (10)

| Entidad | Campos visibles en Lucid |
| --- | --- |
| Apadrinamiento | PK id_apadrinamiento (INT); FK id_reporte (INT); FK id_usuario_padrino (INT); FK id_estado_apadrinamiento (INT); monto_comprometido (DECIMAL(12,2)); fecha_compromiso (DATETIME) |
| CasoRescate | PK id_caso (INT); FK id_reporte (INT); FK id_fundacion (INT); FK id_estado_caso (INT); fecha_aceptacion (DATETIME); fecha_cierre (DATETIME); observaciones (TEXT); FK id_usuario_ultimo_cambio (INT) |
| ConfirmacionAporte | PK id_confirmacion (INT); FK id_apadrinamiento (INT); monto_confirmado (DECIMAL(12,2)); fecha_confirmacion (DATETIME) |
| CuentaFundacion | PK id_cuenta (INT); FK id_fundacion (INT); numero_cuenta_cifrado (VARBINARY); numero_cuenta_ultimos4 (CHAR (4)); banco (VARCHAR); tipo_cuenta (VARCHAR); titular (VARCHAR) |
| CuentaRevelada | PK/FK id_apadrinamiento (INT); PK/FK id_cuenta (INT); fecha_revelacion (DATE) |
| EvidenciaCaso | PK/FK id_archivo (INT); FK id_caso (INT); FK id_tipo_evidencia (INT) |
| HistorialEstadoApadrinamiento | PK id_historial_apadrinamiento (INT); FK id_apadrinamiento (INT); FK id_estado_anterior (INT); FK id_estado_nuevo (INT); FK id_usuario_actor (INT); fecha_cambio (DATETIME); observacion (TEXT) |
| HistorialEstadoCaso | PK id_historial (INT); FK id_caso (INT); FK id_estado_anterior (INT); fecha_cambio (DATETIME); FK id_usuario_actor (INT); FK id_estado_nuevo (INT) |
| Reporte | PK id_reporte (INT); FK id_usuario_reportante (INT); FK id_estado_reporte (INT); FK id_mascota (INT); FK id_tipo_reporte (INT); descripcion (TEXT); contacto_reportante (VARCHAR) |
| ReporteUbicacion | PK/FK id_reporte (INT); punto (POINT) |

## María José: mascotas, adopción y fondo externo (14)

| Entidad | Campos visibles en Lucid |
| --- | --- |
| AutorizacionExpediente | PK id_autorizacion (INT); FK id_mascota (INT); FK id_veterinario (INT); FK id_usuario_otorgante (INT); fecha_otorgamiento (DATE); fecha_revocación (DATE) |
| DistribucionReportadaFondo | PK id_distribucion (INT); FK id_fondo_externo (INT); monto_reportado (DECIMAL(12,2)); FK id_estado_distribucion (INT); FK id_fundacion (INT); fecha_distribucion (DATETIME); criterio (TEXT); FK id_usuario_confirmador (INT); FK id_archivo_evidencia (INT) |
| DocumentoAdjunto | PK/FK id_archivo (INT); FK id_mascota (INT); FK id_tipo_documento (INT) |
| DonacionGeneral | PK id_donacion (INT); FK id_fondo_externo (INT); FK id_usuario_donante (INT); FK id_estado_donacion (INT); monto_comprometido (DECIMAL(12,2)); fecha_compromiso (DATETIME) |
| Especie | PK id_especie (INT); nombre (VARCHAR); descripcion (TEXT) |
| FondoExterno | PK id_fondo_externo (INT); nombre (VARCHAR); datos_transferencia_cifrados (BLOB) |
| HistorialEstadoAdopcion | PK id_historial_adopcion (INT); FK id_solicitud_adopcion (INT); FK id_estado_anterior (INT); FK id_estado_nuevo (INT); FK id_usuario_actor (INT); fecha_cambio (DATETIME); observacion (TEXT) |
| HistorialEstadoDonacion | PK id_historial_donacion (INT); FK id_donacion (INT); FK id_estado_anterior (INT); FK id_estado_nuevo (INT); FK id_usuario_actor (INT); fecha_cambio (DATETIME); observacion (TEXT) |
| HistorialMedico | PK id_historial_medico (INT); FK id_mascota (INT); detalle (TEXT); FK id_veterinario (INT); FK id_usuario_registrador (INT); FK id_usuario_verificador (INT); nombre_veterinario_externo (VARCHAR); registro_profesional_externo (VARCHAR); fecha_atencion (DATETIME); fecha_registro (DATETIME) |
| Mascota | PK id_mascota (INT); FK id_dueno (INT); FK id_raza (INT); FK id_estado_mascota (INT); FK id_caso_origen (INT); nombre (VARCHAR); fecha_nacimiento (DATE); es_estimada (BOOLEAN); FK id_sexo (INT); FK id_tamano (INT); fecha_registro (DATETIME) |
| QR | PK id_qr (INT); FK id_mascota (INT); codigo (VARCHAR); fecha_creacion (DATETIME); fecha_expiracion (DATETIME); fecha_revocacion (DATETIME); FK id_usuario_creador (INT) |
| Raza | PK id_raza (INT); FK id_especie (INT); nombre (VARCHAR) |
| SolicitudAdopcion | PK id_solicitud_adopcion (INT); FK id_mascota (INT); FK id_usuario_adoptante (INT); FK id_estado_adopcion (INT); fecha_solicitud (DATETIME); observaciones (TEXT) |
| SolicitudEmergencia | PK id_solicitud_emergencia (INT); FK id_fundacion (INT); FK id_fondo_externo (INT); FK id_estado_emergencia (INT); motivo (TEXT); monto_solicitado (DECIMAL(12,2)); fecha_solicitud (DATETIME) |

## Sally Andrea: comercio, publicidad y validación (9)

| Entidad | Campos visibles en Lucid |
| --- | --- |
| AlianzaVeterinaria | PK id_alianza (INT); FK id_clinica (INT); descripcion (TEXT) |
| DetallePedido | PK/FK id_pedido (INT); PK/FK id_producto (INT); cantidad (INT); precio_referencia (DECIMAL(12,2)) |
| EspacioPublicitario | PK id_espacio (INT); FK id_anunciante (INT); FK id_tipo_publicidad (INT); fecha_inicio  (DATETIME); fecha_fin (DATETIME); url_destino (VARCHAR); FK id_archivo (INT) |
| PedidoIniciado | PK id_pedido (INT); FK id_tienda (INT); FK id_usuario_cliente (INT); FK id_estado_pedido (INT); fecha_inicio (DATETIME) |
| Producto | PK id_producto (INT); FK id_tienda (INT); FK id_categoria_producto (INT); FK id_tipo_producto (INT); nombre (VARCHAR(150)); descripcion (TEXT); precio (DECIMAL(12,2)); existencias (INT); destacado (BOOLEAN); FK id_estado_producto (INT) |
| ProductoImagen | PK/FK id_archivo (INT); FK id_producto (INT); orden (INT) |
| ReporteModerado | PK id_moderacion (INT); FK id_reporte (INT); FK id_usuario_moderador (INT); FK id_resultado_moderacion (INT) |
| SolicitudValidacion | PK id_solicitud_validacion (INT); FK id_entidad_verificable (INT); FK id_usuario_validador (INT); FK id_estado_solicitud (INT); fecha_solicitud (DATETIME) |
| TarifaPublicacion | PK id_tarifa (INT); FK id_tienda (INT); FK id_tipo_tarifa (INT); monto (DECIMAL); fecha_inicio (DATE); fecha_fin (DATE); concepto (VARCHAR) |
