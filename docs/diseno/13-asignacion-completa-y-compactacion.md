# Ajustes de asignación y compactación del panel

Fecha: 30 de octubre de 2026. Se conserva la arquitectura Django, el RBAC y las reglas de ámbito. No se crean ramas ni commits.

## Roles por persona y acceso desde Usuarios

Ambas entradas utilizan la misma lista filtrable con **todo el catálogo**, incluidos los roles de organización y los inactivos. Antes se ocultaban los que no correspondían al contexto seleccionado y por eso Plataforma mostraba únicamente tres.

- Plataforma permite cambiar los roles globales.
- Una organización de la persona permite cambiar sus roles de ese ámbito, reutilizables o vinculados a esa organización.
- Los demás roles se muestran con una explicación, sin asignarlos indebidamente en otro ámbito.
- Los inactivos se muestran y deben activarse en Roles antes de asignarse.
- El responsable principal se deriva de la responsabilidad vigente y conserva el procedimiento de transferencia aprobado.
- La lista tiene búsqueda local, altura acotada y controles compactos. Buscar no marca el formulario como modificado ni hace peticiones.
- Descartar cambios restaura la selección cargada y permite navegar nuevamente, sin guardar ni revocar roles.
- La búsqueda de personas no ocupa una tarjeta vacía al tener una persona seleccionada; Cambiar persona permite volver a buscar.
- Los enlaces y formularios relativos de las ventanas se resuelven contra su ruta real. Roles, Excepciones y el cambio de persona funcionan dentro de la ventana, sin modificar accidentalmente la página de fondo.

## Auditoría, tablas y presentación

La auditoría muestra búsqueda y limpieza de filtros. Persona, actividad, fechas, módulo, resultado y agrupación están reunidos en Filtros y agrupación. Los filtros adicionales permanecen abiertos si están aplicados y todos conservan su funcionalidad del backend.

Usuarios y Entidades priorizan las acciones frecuentes con iconos y texto pequeño. Cuando hay más de tres, se muestran dos accesos y un menú de acciones restantes. En pantallas estrechas se agrupan en un menú. Los vínculos principales no necesitan forma de píldora. Las operaciones destructivas conservan su confirmación.

Se ajustó la separación entre contexto y excepciones, y entre el catálogo de acciones y el selector de rol. La barra de guardado se condensa al lado derecho. Las ventanas vuelven a blanco en claro y mantienen una superficie neutra en oscuro. Se conservan los colores de perfil.

Guías consultadas: Carbon Data Table (https://v10.carbondesignsystem.com/components/data-table/usage/) para la jerarquía de búsqueda, filtros y acciones; MoJ Filter (https://design-patterns.service.justice.gov.uk/components/filter/) para agrupar filtros secundarios; principios locales de TypeUI para proximidad, espacios y accesibilidad.

## Cómo usar el Catálogo de acciones

Para **dar un permiso a un rol**, no es necesario entrar aquí:

1. Abre Seguridad → Roles y recursos → Permisos.
2. Elige el rol a configurar.
3. Activa el recurso y las acciones que debe poder realizar.
4. Guarda permisos. Comprueba el resultado con la cuenta afectada.

El botón antes llamado Administrar acciones implementadas ahora se llama **Catálogo de acciones** y tiene una guía dentro. Es una configuración del sistema completo:

1. Selecciona una operación existente, por ejemplo Consultar usuarios (`usuarios.ver`).
2. Revisa o modifica su descripción de catálogo.
3. Decide si la acción debe estar activa para el sistema. Desactivarla afecta a todos los roles que la usan: no es la forma de quitársela a un solo rol.
4. Guarda acción.
5. Regresa a la matriz de Permisos para concederla o retirarla de un rol concreto.

Un código nuevo sin implementación no crea una operación del backend. La pantalla permite mantener el catálogo reconocido por el servidor, no programar endpoints mediante nombres. El identificador técnico estable se muestra como referencia y no sustituye a una etiqueta clara.

## Validación

196 pruebas Django aprobadas. Se añadieron comprobaciones de catálogo completo, conservación del ámbito y rechazo de asignación entre organizaciones, guía del catálogo y filtros aplicados visibles. En navegador se verificaron doce recorridos: lista completa desde las dos entradas, filtro sin bloqueo, descartar y navegar, acciones compactas, navegación interna de ventanas, filtros y guía, y ausencia de desbordamiento móvil. No hubo errores JavaScript.

Se revisaron seis vistas con axe en claro y oscuro, después de estabilizar las transiciones de tema: sin infracciones detectadas en las reglas WCAG A/AA comprobadas. Las seis vistas no presentaron desbordamiento de página en 390 px. La revisión de idioma inglés pasó por once vistas y los controles nuevos se tradujeron. Esta revisión automática no sustituye una evaluación manual integral de accesibilidad.

No se requieren migraciones ni modificaciones de datos para esta actualización.

Publicación verificada: Railway `19c955cb-f67d-4488-8cb4-9c7ec4447a5f`, estado SUCCESS. Aprobaron ocho comprobaciones en producción: login con una petición inicial, acciones compactas, igualdad entre el catálogo de Roles y la lista de asignación desde Usuarios, ventana blanca, descarte sin guardar, navegación dentro de la ventana, filtros simplificados y guía del catálogo. No se guardaron asignaciones ni cambios de permisos durante esta revisión. La sesión temporal se cerró y se eliminó su archivo local.
