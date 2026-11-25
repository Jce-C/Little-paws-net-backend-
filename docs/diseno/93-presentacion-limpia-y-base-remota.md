# Presentación limpia y base remota

Se añadió `preparar_presentacion`: exige habilitación explícita, nombre exacto de base terminado en `_demo` y ausencia de cuentas/datos de negocio. Carga ciudades y razas, crea relaciones mediante `seed_demo`, personaliza nombres y textos y valida sus operaciones mediante `verify_demo --presentacion`. Un fallo revierte la carga. No ofrece borrado ni sobrescritura.

Los verificadores reutilizan los tokens por cuenta en cada ejecución: no necesitan repetir el login al alternar actores. Los límites reales de autenticación permanecen activos.

Validación del 25 de noviembre de 2026: 25 pruebas focales; suite completa de 479 pruebas Django aprobada en MySQL aislado. La base local nueva usa PBKDF2 normal, cuenta SQL limitada al esquema y claves privadas propias. Se comprobaron por HTTP real el documento login, tres cuentas por función, 15 productos paginados y rechazo 403 del ciudadano al listado de seguridad. No se conservaron escrituras de negocio desde ese chequeo HTTP.

Se respaldó la base QA anterior y se restauró en un esquema temporal independiente: los conteos de sus 105 tablas coincidieron. Se eliminó solo el esquema temporal de restauración; la base anterior se conserva. La nueva demostración no comparte esos registros.

La inspección remota detectó que `main` sigue en `016415b3a70ccf6173dd2d39cf284b6c898fa305`, ancestro de la base local `795c413`. Los paquetes de entrega se deben regenerar contra ese `main`; no aplicar directamente los anteriores. Se mantiene la separación por José/backend, Sally/app y Majo/diseño-documentación y se comprueba el conjunto sin modificar el índice real.

Se añadieron cinco ilustraciones originales de mascotas y quince de alimentos, identificadas como ejemplos y publicadas por los servicios reales. La carga conserva cualquier imagen anterior. Se corrigió la distribución del escenario: diez mascotas en rescate, cinco con solicitudes pendientes y otras cinco realmente solicitables. El verificador comprueba que el catálogo público devuelve cinco y que los archivos WebP responden por HTTP.

Pendientes explícitos: validación visual de la app conectada, teléfono real, licencias/privacidad, alojamiento/HTTPS/costos y firma Android. No se declara completada la publicación comercial. Guía operativa: [Presentación y commits](../entrega/presentacion-y-commits.md).
