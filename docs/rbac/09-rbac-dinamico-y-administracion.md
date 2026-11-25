# RBAC dinámico y administración del negocio

Edición: 29 de octubre de 2026. Complementa y sustituye las restricciones antiguas de roles del sistema descritas en las etapas previas. Trabajo sin commits nuevos.

## Evaluación única de acceso

La identidad activa se comprueba primero. Un superusuario técnico activo tiene precedencia administrativa en las operaciones conocidas; las cuentas normales combinan roles vigentes y excepciones individuales. DENEGAR prevalece sobre roles y PERMITIR. HEREDAR elimina la excepción, no elimina el rol.

Un permiso no elimina requisitos de membresía, organización, asignación, autorización clínica, vigencia o integridad del proceso. Un Ciudadano puede recibir usuarios.ver y consultar Usuarios sin convertirse en administrador ni superusuario. Si solo recibe consultar, la API de edición sigue devolviendo 403.

El catálogo de seguridad es canónico. AbstractBaseUser conserva su modelo actual; has_perm y has_module_perms utilizan una correspondencia explícita con el motor del proyecto. No hay un user_permissions paralelo que ignore las denegaciones. Se ocultó el editor nativo de grupos, que no participa en este Usuario, para evitar una configuración sin efecto.

Las cuentas del equipo conservan sus asignaciones: esta entrega no las convierte en superusuarios. El administrador técnico de Django permite consultar modelos y administrar cuentas; las transiciones del negocio se realizan en el panel para conservar validaciones y auditoría.

## Pantallas

- /panel/seguridad/?tab=roles: nombres y creación de roles; los códigos son estables.
- ?tab=recursos: nombres y descripciones del menú. Crear metadatos no crea endpoints.
- ?tab=permisos: matriz de recursos y acciones implementadas, filtro y selección entre switches y checks. Un guion indica que no existe esa operación. Guardado explícito del conjunto y detección de edición concurrente.
- ?tab=usuarios: varios roles de plataforma o del contexto de una organización. La responsabilidad principal se transfiere mediante su procedimiento y aceptación, no mediante un check ordinario.
- ?tab=excepciones: HEREDAR/PERMITIR/DENEGAR por persona y contexto, motivo obligatorio y caducidad opcional.
- /panel/usuarios/: lista, búsqueda, roles vigentes, alta y edición de cuenta; contraseñas iniciales temporales.

## Demostración del profesor

1. Abrir una cuenta administradora y otra ciudadana en perfiles de navegador distintos.
2. En Permisos por rol, seleccionar Ciudadano; filtrar Usuarios; activar Consultar y guardar.
3. Verificar que aparece Usuarios en la otra sesión y abre el listado.
4. Retirar Consultar, guardar y verificar que desaparece y la URL protegida devuelve 403.
5. Repetir mediante Excepciones individuales sobre Robert: PERMITIR usuarios.ver sin afectar a otros ciudadanos.
6. Para bloquear un permiso heredado, seleccionar DENEGAR sobre el permiso exacto. Quitar una concesión adicional no bloquea lo que sigue heredándose de otro rol.
7. Para adopciones distinguir participación propia (adopcion.participar) de consulta administrativa asignada (adopcion.ver). Esta última exige organización y registro asignado. Seleccionar el contexto correcto.
8. Volver a HEREDAR y comprobar el resultado en Tus accesos actuales.
9. Renombrar el recurso Usuarios y observar el menú y encabezado de la otra sesión; restaurar el nombre al terminar.

## Áreas del negocio y formularios

Las pantallas /panel/areas/<área>/ muestran registros disponibles, búsqueda, acciones y formularios. Los formularios utilizan los serializers y endpoints existentes con el actor actual; no aceptan rutas suministradas por el navegador ni sustituyen la autorización del servidor.

| Área | Operaciones principales |
| --- | --- |
| organizaciones | Alta y edición de fundaciones, tiendas, clínicas y profesionales; integrantes, cargos, principal, transferencias, verificación y cuentas receptoras |
| mascotas y reportes | Fichas propias, edición administrativa, reportes, correcciones, aceptación para rescate y moderación |
| rescates | Consulta en la organización y transiciones de estado |
| adopciones | Solicitudes, respuestas, retiro, toma/devolución, decisión y seguimiento posterior autorizado |
| aportes | Compromisos, declaración de transferencia y confirmación de recepción |
| fondos | Alta, edición, compromiso, solicitud de emergencia, asignación y distribución informativa |
| catalogo y pedidos | Productos, disponibilidad, existencias, pedido con varias líneas y estados |
| expedientes | Autorización vigente, QR, atención clínica, enmienda y revocación; documentos privados |
| publicidad | Versiones y vigencia de anuncios; revisión separada |
| verificaciones y reclamaciones | Documentos, toma, resolución; reclamación favorable y ejecución de titularidad en dos pasos |

Las operaciones financieras registran información: no cobran ni ejecutan transferencias. Los historiales y seguimientos no se sobrescriben. No se salta una aprobación ni se permite resolver un conflicto propio por cambiar un check.

## Menú, sesiones y rendimiento

El motor se reutiliza durante cada petición para evitar reconstruir permisos por cada fila del menú. Las operaciones siguientes leen el estado actualizado. Las modificaciones de modelos de seguridad y operaciones de negocio incrementan una revisión transaccional.

ASGI y Server-Sent Events notifican cambios a sesiones autenticadas. Hay un lector compartido de revisión por proceso, aproximadamente una consulta por segundo mientras existen clientes; cada cambio requiere además que los clientes recuperen su estado. Es un coste explícito, no un sistema sin consultas. No se inicia esta conexión en el login.

En la prueba local con dos sesiones, la revocación llegó aproximadamente en un segundo; no es una garantía universal de latencia. El servidor rechaza inmediatamente la siguiente operación no autorizada, aunque la red de notificaciones esté interrumpida. Las expiraciones tienen temporizadores y las reconexiones vuelven a comprobar el estado. Consultar un detalle se audita sin generar bucles de recarga.

## Landing, login y preferencias

/ es informativa y conserva animación e identidad. /panel/login/ contiene datos, contraseña, suma y envío directo. CSS, JS, tipografía, logo, iconos y fondo están integrados en su HTML: la prueba de navegador observó una petición inicial y ninguna adicional automática. Una imagen inline también consume bytes y se contabiliza dentro del documento.

Se conservan CSRF, cookies seguras de producción, caducidad de desafío y límites de intentos. La suma no constituye protección DDoS por sí sola.

El menú se pliega en escritorio y se cierra en móvil. Tema, contraste, texto y movimiento se aplican al seleccionarlos. La landing conserva su ubicación. El color se guarda por usuario y no modifica permisos. El modo oscuro tiene base neutra. Los ajustes conservan alternativa sin JavaScript.

## Datos y despliegue

Migraciones aditivas seguridad 0008-0012: excepciones, revisión, perfil visual, textos configurables, seguimiento y catálogo complementario. Se hizo respaldo privado antes de migrar exclusivamente little_paws_panel_v2. No se ejecutó seed_demo en producción ni se tocó la base anterior.

Docker ejecuta Uvicorn ASGI con dos procesos. En desarrollo usar python -m uvicorn config.asgi:application --reload con DEBUG=true; ASGI sirve los recursos estáticos locales. El runserver WSGI tradicional no sirve SSE y responde 503 explícito en ese endpoint en lugar de quedar bloqueado. CONN_MAX_AGE=0 para las conexiones ORM del despliegue ASGI. Los documentos se conservan en el volumen privado; .env, SQL, sesiones y respaldos no forman parte del repositorio.

## Verificación y límites

- 155 pruebas Django aprobadas en MySQL aislado, incluida autorización, integridad, concurrencia y formularios de negocio.
- Construcción de todos los formularios del catálogo y recorridos HTTP de organización, mascota, producto, pedido y anuncio.
- Demostración de concesión y revocación por rol e individual, aislamiento entre ciudadanos y renombrado entre sesiones.
- Superusuario con acceso a las 14 áreas; cuenta de consulta sin edición.
- Revisión automática axe de cinco vistas en claro y oscuro sin infracciones detectadas; sin desbordamiento horizontal de página en móvil. No sustituye una revisión manual completa de accesibilidad.
- Sin errores JavaScript en los recorridos de navegador registrados.

Antes de una explotación pública amplia se necesita una prueba de carga con concurrencia real, política operativa de respaldo/restauración y alertas, revisión del equipo con datos representativos y completar la revisión lingüística de formularios y mensajes de negocio. No se ha medido capacidad máxima ni certificado cumplimiento completo WCAG.

## Organización del código

- seguridad/autorizacion.py: evaluación efectiva compartida y contexto de petición.
- seguridad/excepciones.py y rbac_api.py: guardar y consultar excepciones, con auditoría.
- seguridad/signals.py y realtime.py: revisión transaccional y notificación SSE.
- seguridad/web/administracion.py: matrices y edición en pantalla.
- seguridad/web/usuarios.py: cuentas sin ventanas emergentes.
- seguridad/web/negocio.py y procesos.py: formularios y rutas de cada proceso.
- seguridad/negocio_api.py: administración complementaria y seguimiento.
- seguridad/web/dashboard.py: indicadores, auditoría y configuración de textos.
- seguridad/admin.py, accounts/admin.py y django_permisos.py: integración técnica de Django.
- seguridad/templatetags/publicos.py: recursos permitidos e integrados del login.
- seguridad/tests_rbac_dinamico.py y tests_negocio_web.py: aceptación del comportamiento nuevo.
