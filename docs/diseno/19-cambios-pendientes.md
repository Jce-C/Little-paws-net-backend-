# Aviso de cambios pendientes

Fecha: 2026-11-04.

Al cerrar un formulario con cambios, cambiar de pantalla o contexto, o cerrar sesión, aparece un diálogo centrado: **Seguir editando**, **Descartar cambios**, **Guardar y continuar**. Escape equivale a seguir editando. El foco permanece dentro del diálogo y regresa al control anterior al cerrarlo.

Guardar y continuar valida el formulario y espera la confirmación del servidor antes de continuar. Un error de validación o de conexión conserva los datos y la condición de cambios pendientes. Descartar restablece el formulario antes de continuar. No se modifica la autorización del backend.

Las operaciones sensibles (eliminar, revocar, transferir, aprobar o rechazar) deben confirmarse desde su propio formulario. El aviso ofrece seguir editando o descartar y explica esta condición.

Al cerrar la pestaña o recargar el navegador se conserva el aviso nativo: el navegador no permite sustituirlo por un diálogo personalizado con guardado asíncrono.

Verificación: 12 comprobaciones de interfaz, incluyendo borradores, guardado local real, rechazo del servidor, teclado y móvil. Sin incidencias WCAG detectadas por axe en el diálogo claro/oscuro. Pasan las 28 pruebas Django de acceso web. Los guardados de aceptación se realizan únicamente en la base local.

Despliegue Railway 2114c62d-2b38-4771-9b56-2ec773a6567b: SUCCESS. La revisión autenticada de producción quedó bloqueada por el filtro local FortiGuard (Access Blocked); no se alteraron datos de negocio en producción. La aceptación completa se verificó localmente.
