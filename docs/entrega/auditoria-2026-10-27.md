> Documento histórico. Los seis bloques ya se integraron. Estado vigente: [auditoría final](auditoria-final.md) y [actualización del equipo](actualizar-equipo.md).

# Auditoría de entrega · 27 de octubre de 2026

Estado: **todavía no presentar como entrega integrada publicada**. El backend RBAC y el panel inicial funcionan en MySQL local; la demo visual pública y el backend antiguo de Railway son piezas distintas.

Esta revisión no creó commits ni hizo push o publicación de código. La inspección inicial de Railway fue de solo lectura; después, el propietario aprobó crear un esquema separado para esta versión. La creación y su resultado se registran en `output/auditoria-entrega/railway-nueva-base.json`. No se cambió la configuración de la API publicada ni las bases anteriores. El punto de partida de este repositorio es `016415b3a70ccf6173dd2d39cf284b6c898fa305`. Se conservaron los cambios locales anteriores.

## Lo que pidió el profesor

Según la definición confirmada en `docs/rbac/01-definicion-de-accesos.md`, se requieren pantallas para administrar usuarios, roles, recursos y permisos, login con suma, y autorización real desde Django. No basta con mostrar perfiles ficticios ni esconder botones.

| Requisito | Estado verificado |
| --- | --- |
| Login con correo, contraseña y captcha aritmético | Funciona en Django; suma consumible, sesión, CSRF y límites compartidos |
| Usuarios | Consulta, alta, edición y activación/desactivación; asignación/revocación global por permiso |
| Roles | Consulta, alta, edición y matriz de permisos; límites de roles estructurales |
| Recursos | Consulta, alta y edición; código estable y protección de recursos esenciales |
| Permisos | Catálogo de acciones reconocidas; asignación a roles y edición de descripción/estado desde el panel |
| Alcance por organización, asignación y autorización | Servicios y API; probado con acceso permitido y denegado |
| Apariencia elegida para bienvenida y login | Integrada en el login auténtico de Django, con fondos originales y animación opcional |
| Formularios completos de operación para todos los perfiles | Bocetados; varias API existen, pero faltan formularios web de transferencias, aprobaciones y otros procesos |
| Panel completo funcionando en Railway | Pendiente de resolver la compatibilidad entre las dos versiones del backend |

La base nueva aprobada `little_paws_panel_v2` ya está creada y migrada en Railway: 91 tablas, 13 roles activos, 20 recursos y 51 permisos. La conexión Django comprobó sin incidencias y con TLS requerido. **La base está preparada; el backend nuevo aún no se ha desplegado.** Las bases anteriores y el código publicado se conservaron. No se crearon cuentas con contraseñas automáticas.

No se ofrece eliminación física general: se revocan roles o desactivan registros para conservar relaciones y auditoría. Crear un nombre de permiso no crea una operación nueva; la acción debe estar implementada y reconocida por el servidor.

## Hallazgos y correcciones

1. **Bloqueante: historias de migración diferentes.** La copia de evaluación de Railway conectó en modo solo lectura: MySQL 8.4.11, 66 tablas y 58 migraciones registradas. La base local usa MySQL 8.0.46 y tiene 91 tablas. Comparando sin diferencias artificiales de mayúsculas Windows/Linux, faltan 25 tablas y 22 columnas de tablas compartidas en evaluación. También hay tres diferencias de tipo/nulabilidad y seis archivos de migración con nombres compartidos y contenido distinto. El backend antiguo usa `adoptions`; este usa `adoption`. No usar `--fake`, importar SQL o ejecutar `migrate` a ciegas sobre Railway.
2. **Diseño integrado; publicación nueva pendiente.** El login real `/panel/login/` ya utiliza la bienvenida, nubes, fondos de escritorio/móvil y tarjetas aprobadas, con formulario POST, suma dinámica, CSRF y sesión de Django. No usa perfiles ficticios ni contraseñas de la demo. El enlace `little-paws-panel-diseno...chatgpt.site` sigue siendo exclusivamente visual; la API antigua de Railway todavía no publica esta versión del panel.
3. **Acceso de evaluación expuesto en la copia cloud anterior.** Su README y reglas de colaboración declaran un `.env` publicado con acceso SQL a una base desechable de evaluación; la conexión sigue siendo utilizable. Este repositorio ignora `.env` y no lo incluye en los paquetes. La credencial anterior debe revocarse/rotarse en su origen; borrar un archivo no revoca una clave. No se modificó esa copia ni su cuenta SQL.
4. **Corregido: acciones de edición visibles sin permiso.** El servidor ahora transmite capacidades de edición y asignación calculadas desde permisos vigentes. El navegador oculta acciones que no corresponden. La matriz de un lector permite consultar y deshabilita los controles de guardado. La API conserva su propia autorización.
5. **Corregido: faltaba editor web del catálogo de permisos.** Se añadió edición de descripción/estado con la API existente. Acción, recurso y alcance permanecen fijados por el servidor. Los permisos esenciales no se pueden desactivar. No hay nueva migración por esta corrección.
6. **Pendiente: cuenta inicial para la presentación real.** En la base local hay 20 cuentas inactivas, cero cuentas activas y ningún administrador activo. La base nueva se inicializa sin cuentas demo. El propietario debe ejecutar `iniciar_seguridad` en la base elegida con su contraseña privada; no reactivar `seed_demo` como atajo.
7. **Configuración pública preparada; despliegue y volumen pendientes.** Se añadieron `settings_railway.py`, requisitos de Gunicorn/WhiteNoise, Dockerfile y exclusiones de secretos. `collectstatic` funciona: 192 recursos, 542 variantes procesadas. `check --deploy` con esta configuración deja solo las recomendaciones de HSTS para subdominios/preload, desactivadas intencionadamente porque no se controlan dominios ajenos. No se compiló la imagen Docker: el motor local está apagado. Antes de publicar hay que comprobarla en Linux y configurar dominio, origen CSRF, secretos y volumen privado persistente; no copiar la configuración cloud antigua ni cambiar su base. Conservar `LPN_DATA_KEY` al trasladar datos cifrados.

## Comprobaciones realizadas

- 107 pruebas existentes y 3 regresiones añadidas: **110 pruebas** aprobadas en MySQL aislado. Incluyen autorización, CSRF, sesiones, captcha, concurrencia y formulario auténtico sin controles ficticios. No tocaron la base de Railway.
- `check` sin incidencias; `makemigrations --check --dry-run` sin cambios; todas las migraciones locales aplicadas.
- Sintaxis de 129 archivos Python y tres entradas JavaScript del backend-panel/herramientas sin errores; `pip check` sin dependencias rotas.
- **121 comprobaciones visuales**: 33 páginas de perfiles a 390, 1366 y 2560 px, bienvenida y tarjetas en 10 tamaños, marca completa y entrada de nubes. Sin errores de JavaScript ni desbordamientos detectados.
- Ventanas de la demo en móvil/portátil y menú de 320 px: tres comprobaciones aprobadas.
- Fondo móvil en seis tamaños, proporción íntegra, carga de imágenes, animación y recorrido ficticio: ocho comprobaciones aprobadas.
- **32 comprobaciones del panel real en navegador**, contra un MySQL aislado con cuentas sintéticas: cinco módulos a cinco tamaños, editor de permisos, matriz editable y lector sin edición/asignación. Sin fallos detectados.
- **22 comprobaciones del login conectado**: ocho tamaños, nubes, fondos sin imágenes rotas, error con suma nueva, contraseña sin reflejar en HTML, ayuda, entrada real, salida y animación con movimiento reducido. Sin fallos detectados.

Evidencias locales en `output/auditoria-entrega/`, `output/responsive-panel/` y `output/fondo-movil/`. Los informes generados y los paquetes se excluyen de Git. Son comprobaciones acotadas; no equivalen a garantizar ausencia total de errores, a una auditoría WCAG completa o a una prueba de carga de producción.

## Orden para cerrar la entrega

1. Verificar el cierre de la migración a la base nueva aprobada en Railway siguiendo `railway.md`.
2. Integrar los paquetes del grupo sobre la base correcta; ejecutar las pruebas antes de publicar.
3. Revisar el login conectado ya implementado; su generador es `frontend/panel-design/build-login-django.py`.
4. Crear el administrador inicial e invitar/configurar las cuentas necesarias con permisos mínimos.
5. Verificar sobre el servidor elegido: login, alta de usuario, rol, asignación, operación permitida, operación denegada, revocación y cierre de sesión.
6. Presentar el panel funcional y distinguir los procesos operativos que siguen como boceto. Si el profesor evalúa todos esos procesos, completar sus formularios antes de declarar la entrega terminada.
