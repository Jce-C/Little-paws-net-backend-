# Tercera fase: operatividad del negocio y administración

30 de octubre de 2026. Se trabajó sobre el panel Django existente. No se crearon commits ni ramas. Se conservan autenticación, sesiones, RBAC, relaciones e información histórica. El servicio y la base anteriores de Railway no se modifican.

## Diagnóstico que motivó esta fase

La base del panel tenía cero mascotas, razas y ciudades. El gráfico «Mascotas 4» representaba permisos efectivos y podía confundirse con animales registrados. Los valores maestros de estados y categorías sí existían. La existencia de endpoints y pruebas de RBAC no garantizaba que los formularios pudieran completarse con esa configuración de producción.

## Cambios funcionales

### Catálogos de producción

Se agrega Catálogos del sistema, con ciudades, especies y razas; búsqueda y paginación; creación y edición autorizadas; disponibilidad para nuevos registros; control de versión y auditoría. Desactivar no borra relaciones históricas. Las nuevas mascotas rechazan razas o especies inactivas y los nuevos reportes y organizaciones requieren ciudades activas. La edición de una mascota permite conservar su referencia histórica aunque después se haya desactivado esa raza.

`cargar_catalogos_produccion` carga una instantánea de 1.122 referencias territoriales del conjunto DIVIPOLA de Datos Abiertos Colombia, proveedor DANE. Fuente: https://www.datos.gov.co/resource/gdxc-w37w.json ; consulta 2026-10-30. Se almacenan códigos, nombres y departamentos, no se toman sus coordenadas para inventar direcciones de reportes. El archivo se incluye en `core/data/ciudades_divipola.json`, por lo que el formulario no depende de una consulta externa en cada uso. Se conservan referencias locales existentes; una coincidencia normalizada puede recibir su código oficial sin alterar sus relaciones. No se mezclan o borran automáticamente duplicados históricos.

Incluye dos especies iniciales, Perro y Gato, y 22 referencias de raza, entre ellas Mestizo y Raza no determinada. Es un catálogo inicial mantenible, no una lista exhaustiva de todas las razas. La carga es idempotente y respeta valores ya existentes e inactivos. No crea personas, mascotas, organizaciones, reportes ni transacciones.

`verificar_operatividad --estricto` verifica la existencia de catálogos activos y valores maestros necesarios, sin confundir la ausencia normal de transacciones con un error de configuración. Los formularios explican sus opciones obligatorias vacías y bloquean el envío hasta completar los datos previos. Los selectores de ciudad y raza disponen de búsqueda local; las ciudades no se limitan a las primeras 200 referencias.

### Ubicación de reportes

Nuevos datos obligatorios: `ciudad_id`, `barrio`, `direccion`. Opcional: `indicaciones`. El panel no solicita coordenadas. La API admite opcionalmente una pareja válida de coordenadas reales, pero nunca las genera desde el texto.

Las columnas nuevas admiten vacío/nulo para preservar reportes antiguos. La tabla espacial existente no se altera ni se elimina; solo se crea su registro si hay coordenadas reales. El detalle autorizado permite consultar tanto la dirección nueva como las coordenadas históricas. Los clientes que creen reportes deben actualizar su payload para incluir la dirección; la compatibilidad histórica no significa que un reporte nuevo pueda omitirla.

Para aceptar rescates sin coordenadas, una fundación declara cobertura por ciudad mediante una operación autorizada y auditada. Los reportes con coordenadas conservan la validación espacial anterior. No se supone que una dirección escrita pertenece a un polígono ni se habilita cobertura automáticamente.

### Recorrido de rescate y adopción

Se incorpora Registrar mascota rescatada sobre un caso abierto: valida permiso, fundación verificada y raza activa; crea una mascota sin dueño particular, su custodia y la relación del reporte/caso. Un reporte que ya tiene mascota no se puede sobrescribir ni utilizar para cambiar titularidad.

Disponibilidad para adopción requiere una custodia única vigente, una fundación verificada, el permiso correspondiente y confirmación de revisión de la ficha. Permite ofrecerla o retirarla de adopción. Rechaza mascotas con dueño particular y mascotas ya adoptadas. Las solicitudes, asignaciones y resolución utilizan los servicios existentes, con sus controles de ámbito, asignación y conflicto de interés. No se evita el procedimiento de reclamación de titularidad ni se certifica automáticamente una condición sanitaria.

### Desactivación y eliminación

Desactivar y restaurar muestran identificación, consecuencias breves y Cancelar/Confirmar. No solicitan motivo escrito ni transcripción de nombre. La acción se registra con motivo técnico descriptivo. Permanecen CSRF, autorización, confirmación firmada con caducidad, comprobación del estado revisado, bloqueos transaccionales, idempotencia y protección de cuentas/roles esenciales.

Eliminar o archivar conserva revisión de dependencias, motivo y confirmación explícita. El borrado físico se bloquea cuando afectaría relaciones o registros históricos. Los controles adicionales no se muestran en una simple desactivación.

### Contextos y roles

Plataforma sigue siendo el contexto global. El selector obtiene organizaciones activas reales: administración total puede gestionarlas; un asignador limitado solo ve aquellas en las que tiene autoridad de equipo. Una organización nueva aparece en la siguiente consulta. Si la persona no pertenece a la seleccionada, se solicita confirmar su incorporación antes de guardar roles; se crean membresía y asignaciones dentro de la misma transacción. No se crean membresías al consultar ni se muestran contextos ficticios.

La edición de roles agrupa permisos por recurso, con categorías desplegables, búsqueda que abre coincidencias, contador de seleccionados/total, switches alineados y estado Activo/Inactivo. Los campos y firmas de guardado, las validaciones de autorización y la sincronización permanecen conectados a los servicios previos.

## Cambios visuales

Las operaciones principales de cada área se muestran como tarjetas con iconos y enlaces reales. Cancelar, guardar y acciones pequeñas siguen siendo controles compactos. Se conserva la paleta, la barra superior y el lateral con categorías. Se retiraron flechas decorativas del login, landing y enlaces/botones del panel, manteniendo controles funcionales de desplazamiento, desplegables y acordeones.

La auditoría tiene descripción breve, búsqueda, aplicar/limpiar, filtros avanzados alineados, total y exportación discreta, tabla con resultado identificable y detalle completo. Agrupar por usuario/sesión crea grupos expandibles con número de operaciones, periodo y resultados. **La agrupación resume la página actual**, no el historial completo del actor; se indica expresamente y no se modifica ningún evento histórico. Se conservan filtros, exportación, detalles y paginación. Las nuevas operaciones tienen descripciones legibles.

El dashboard muestra «N permisos» en los gráficos de accesos. La cifra de mascotas disponibles usa la consulta de visibilidad compartida y enlaza al listado con el mismo estado cuando la cuenta puede abrirlo.

## Archivos y componentes

- Modelos y migraciones: `core/models.py`, `animals/models.py`, `rescue/models.py`, `geography/models.py`; dos migraciones de permisos en `seguridad/migrations/0017…` y `0018…`.
- Datos y comandos: `core/data/ciudades_divipola.json`, `cargar_catalogos_produccion.py`, `verificar_operatividad.py`; `verify_demo.py` usa el nuevo contrato de dirección en sus pruebas reversibles.
- Catálogos: `seguridad/catalogos.py`, `catalogos_api.py`, `web/catalogos.py`, `templates/seguridad/web/catalogos.html`.
- Negocio: `consultas_negocio.py`, `negocio_api.py`, `flujos_serializers.py`, `web/negocio.py`, `web/procesos.py`, `rescue/serializers.py`, `rescue/views.py`, `rescue/services.py`.
- Administración: `administracion_segura.py`, `bajas_api.py`, `web/bajas.py`, `web/administracion.py`, `web/contexto.py`, `web/dashboard.py`, URLs.
- Plantillas reutilizables: `opciones_rol.html`, `auditoria_fila.html`, `auditoria_tabla.html`, `auditoria.html`, `baja.html`, `negocio.html`, `inicio.html` y botones públicos.
- Recursos: `compacto.css`, `interacciones.js`, `navegacion.js`, catálogos de idioma `.po/.mo`.
- Pruebas nuevas: `seguridad/tests_fase_tres.py`; el generador de referencias de pruebas incorpora los permisos nuevos.

## Base de datos y endpoints

Seis migraciones aditivas:

1. `core.0009`: disponibilidad y código DIVIPOLA de Ciudad.
2. `animals.0005`: disponibilidad de Especie y Raza.
3. `rescue.0003`: ciudad, barrio, dirección e indicaciones del reporte.
4. `geography.0004`: cobertura única por fundación y ciudad.
5. `seguridad.0017`: permisos `catalogos.ver/crear/editar`, `caso.cobertura`.
6. `seguridad.0018`: `caso.registrar_mascota`, `mascotas.publicar_adopcion`.

Los permisos de catálogos se conceden a la administración de seguridad. Cobertura se añade a los responsables principal/secundario y administración. Registrar rescatadas se añade a gestores de rescate y publicar a gestores de adopción, además del catálogo administrativo existente. Los alcances de organización continúan exigiendo contexto/membresía salvo la precedencia del superusuario técnico ya existente. No se amplía el rol Ciudadano por esta migración.

- `GET /panel/catalogos/`: mantenimiento autorizado.
- `GET/POST /api/seguridad/catalogos/<tipo>/`; `GET/PATCH/POST /api/seguridad/catalogos/<tipo>/<id>/`: validaciones y versión de edición compartidas.
- `GET/POST /api/seguridad/organizaciones/<id>/cobertura/`: ciudades de atención de una fundación.
- `POST /api/seguridad/casos/<id>/mascota/`: ingreso bajo custodia.
- `POST /api/seguridad/mascotas-administrar/<id>/disponibilidad/`: revisión y publicación/retiro de adopción.
- `POST /api/reportes/`: nuevo contrato de dirección, coordenadas reales opcionales.
- Las rutas previas de bajas, roles, adopciones y reportes se conservan.

## Cómo iniciar una operación real

1. Administración comprueba Catálogos del sistema.
2. Registra la organización real y designa al responsable; completa su verificación por el procedimiento vigente.
3. Incorpora las cuentas individuales y sus roles de trabajo. Ser administrador de seguridad no sustituye automáticamente una responsabilidad de negocio.
4. La fundación configura cobertura y capacidad; recibe un reporte real con ubicación.
5. El gestor autorizado acepta el reporte y registra la mascota rescatada bajo custodia.
6. El gestor de adopciones revisa la ficha y su disponibilidad; el ciudadano presenta la solicitud.
7. El gestor toma y resuelve la solicitud según las reglas existentes; se conservan resultados e historial.

No deben añadirse mascotas, cuentas bancarias, verificaciones o casos ficticios a producción para aparentar actividad. Si faltan los requisitos reales, la interfaz debe explicarlos.

## Pruebas y límites

Se aprobaron 215 pruebas del backend, incluyendo un recorrido por endpoints desde reporte escrito y cobertura hasta resolución de adopción, conservación de coordenadas históricas, carga idempotente sin transacciones ficticias, desactivación simple, eliminación protegida, contextos/membresía explícita, rechazo entre ámbitos, versión de catálogo, raza inactiva, indicadores y grupos de auditoría.

En navegador local aprobaron 13 comprobaciones de catálogos, creación y consulta de mascota/reporte, campos de ubicación, permisos agrupados, búsqueda sin bloquear el formulario, confirmación simple, contextos reales, tarjetas, auditoría expandible y móvil. Se revisaron ocho vistas en claro/oscuro con axe y sin desbordamiento de página a 390 px; se conserva la landing al cambiar tema. Las pruebas de creación y adopción usan exclusivamente datos sintéticos locales.

Pendientes externos a esta entrega: revisión manual integral con lector de pantalla y prueba de carga concurrente. Las ciudades son una instantánea con fuente y fecha, no una sincronización externa permanente. Las razas iniciales son ampliables; la cobertura por ciudad es una declaración explícita y no una geocodificación ni una garantía de ubicación exacta. El procedimiento sanitario y la verificación institucional requieren revisión humana real.

## Cierre de producción

Publicación Railway `8af0c58d-42fc-4a30-a22d-3baa337702c4`, estado SUCCESS. Se respaldó `little_paws_panel_v2` antes de migrar: 271.767 bytes, SHA-256 `c6c6eb4b7d52fa10e34f9e7a6617f5e778f8f52455e13ad3c7d63d54ac1a137d`. Las seis migraciones se aplicaron correctamente. No se modificó la base anterior.

La carga de producción creó 1.122 ciudades, dos especies y 22 razas. La comprobación estricta no encontró catálogos faltantes. Mascotas y reportes permanecieron en cero antes y después de la carga: no se añadieron ejemplos ni transacciones ficticias. La preparación se registró en auditoría con fuente y hash del archivo de referencia.

Aprobaron 12 comprobaciones de la aplicación publicada: login con una petición del documento y sin flechas decorativas, catálogo de 1.122 ciudades, 22 razas seleccionables, formulario de mascota habilitado, ciudades en organizaciones, reporte con dirección y sin campos manuales de coordenadas, contextos reales en asignación, editor de permisos agrupado, confirmación de desactivación sin ejecutarla, grupos expandibles/detalle de auditoría y ausencia de desbordamiento móvil. No se observaron errores JavaScript. La sesión temporal se cerró y se eliminó su archivo local.

La revisión de idioma recorrió 14 vistas y conservó borradores, barra contraída y controles compactos. Ocho vistas revisadas con axe en claro y oscuro no presentaron infracciones de las reglas WCAG comprobadas; esta evidencia automática no implica certificación integral de accesibilidad ni prueba de carga.
