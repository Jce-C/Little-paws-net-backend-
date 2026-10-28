# Auditoría final — 28 de octubre de 2026

## Alcance y resultado

Revisión de la rama integrada `entrega-panel` después de los seis bloques del equipo. Se conservaron las aportaciones y la historia Git. Panel publicado en https://little-paws-panel-production.up.railway.app/panel/login/, con base separada `little_paws_panel_v2` y volumen privado. El servicio antiguo se conserva por compatibilidad: eliminarlo ahora rompería otro despliegue y no resolvería sus diferencias de migraciones.

## Correcciones

- Retirado `backend/.env` del seguimiento y eliminada toda excepción para publicar secretos. Rotada la contraseña del usuario SQL expuesto, verificado rechazo de la anterior. El usuario rotado solo tenía permisos sobre evaluación, distinto del de la API antigua. Las claves Django y Fernet publicadas tampoco coincidían con las de la API anterior. No se reescribió el historial público: la clave vieja permanece allí, pero ya no autentica en SQL.
- README y CONTRIBUTING reescritos: panel vigente, demo estática y backend anterior diferenciados; eliminadas instrucciones de usar el .env público. Guía para actualizar las PCs sin sobreescribir trabajos ni recuperar un stash a ciegas.
- Retirados nueve recursos/generador obsoletos (9.981.375 bytes) del paisaje anterior. Respaldo local fuera de Git. Fondos SVG, nubes, ilustraciones, fuentes e iconos vigentes conservados con sus licencias.
- Entrada raíz redirige al login real. Configuración de healthcheck, HTTPS, hosts, tiempos/conexiones de base y detección del cliente detrás del edge de Railway. Cabeceras de cliente ignoradas fuera de esa configuración.
- CI en Linux/MySQL 8.4; reglas de finales de línea y configuración de despliegue reproducible. Runtime Docker separado del compilador y servidor ejecutado como usuario app.
- Cambio de contraseña con validación de la actual, CSRF, límites, rotación del hash de sesión y auditoría. Cuentas temporales bloqueadas para panel/API/JWT hasta cambiar su clave. La nueva columna se añadió mediante migración propia.
- Tres cuentas individuales con `ADMIN_SEGURIDAD`, mismo nivel por instrucción del propietario. Dos cuentas nuevas con claves temporales privadas; cuenta existente de José conservada. Sin claves en Git, logs o archivos públicos.

## Evidencia

- 116 pruebas Django aprobadas en MySQL aislado; configuración sin errores y sin migraciones sin generar.
- 32 comprobaciones de panel real (roles de administrador y lector, cinco módulos, cinco tamaños) y 22 del login: sin errores JavaScript, imágenes rotas o desbordamientos detectados.
- 14 comprobaciones públicas adicionales de las cuentas nuevas: login, cambio obligatorio, adaptación 320–2560 px, bloqueo API/JWT y cierre de sesión. No se cambiaron sus contraseñas temporales durante la prueba.
- Auditoría de dependencias directas fijadas de Python, incluyendo despliegue: sin vulnerabilidades conocidas reportadas; npm audit sin hallazgos. No sustituye una revisión completa de cadena de suministro/transitivas.
- Imagen construida en Linux por Railway; despliegue SUCCESS, health/login/estáticos responden con HTTPS. `collectstatic` y `check --deploy` aprobados; permanecen solo advertencias de HSTS subdominios/preload, deliberadamente desactivados para un dominio compartido que no se controla.

Evidencia detallada y capturas en `output/auditoria-final/` y `output/entrega-repositorio-oficial/`, excluidos de Git. Las pruebas son acotadas, no una certificación WCAG ni garantía de ausencia de errores.

## Lo listo para el requisito académico

Login auténtico con suma dinámica; administración de usuarios, roles, recursos y permisos; asignación/revocación, autorización de servidor por alcance y auditoría. El usuario ve capacidades vigentes; desactivar o revocar conserva relaciones. La demo de diseño no se usa como autenticación.

## Trabajo pendiente para producción profesional

1. Ensayar restauración de respaldos de MySQL y documentos privados; política de retención, RPO/RTO y pruebas de recuperación. Tener un volumen no equivale a disponer de backups.
2. Correo transaccional, recuperación segura y MFA para administradores. El cambio autenticado implementado no es recuperación de una contraseña olvidada.
3. Monitoreo continuo de disponibilidad/base, alertas, manejo de incidencias y mantenimiento periódico de sesiones, desafíos y límites. No borrar auditoría sin política de retención.
4. Completar formularios de transferencias, aprobaciones, adopciones y demás operación donde solo existe API/listado o boceto. No prometer cobertura completa de esos procesos por tener las pantallas de seguridad.
5. Pruebas de carga y accesibilidad manual con teclado/lector de pantalla; revisión independiente de permisos y del riesgo aceptado de tres administradores equivalentes.
6. Migración planificada de datos y contratos si se decide consolidar backend anterior y V2; después retirar el servicio anterior. Mantener las dos carpetas ahora es una transición explícita.
7. Vincular el servicio nuevo a despliegue automático desde GitHub si se desea, con CI obligatorio antes de publicar, y política de dependencias/hashes/actualizaciones.

## Actualización del equipo

Seguir [actualizar-equipo.md](actualizar-equipo.md). Entrar a la web publicada no requiere instalar herramientas ni conocer la contraseña SQL. Las credenciales individuales se comparten por separado y se sustituyen al primer ingreso.

## Ampliación: idioma y accesibilidad

Se incorporaron español/inglés mediante los catálogos de Django y preferencias de texto, contraste y movimiento. La validación ampliada comprende 122 pruebas Django y 18 comprobaciones de navegador, sin errores detectados. Axe-core revisó siete estados A/AA sin infracciones detectadas. El proceso y los límites, incluidas las pruebas manuales aún necesarias, se documentan en [idiomas-y-accesibilidad.md](../diseno/idiomas-y-accesibilidad.md). No equivale a una certificación WCAG.
