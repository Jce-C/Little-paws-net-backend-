# Ofrecimientos de ayuda y aislamiento de sesión · 20 noviembre 2026

## Fallo reproducido

«Mis ofrecimientos» reutilizaba un listado que conservaba su Future y el resultado cargado. No escuchaba Session, por lo que cerrar sesión podía dejar visible un ofrecimiento de la cuenta anterior. Cambiar de cuenta tampoco obligaba a consultar de nuevo el permiso de esa persona. La API seguía autorizando cada petición; el defecto estaba en el estado privado conservado por la interfaz.

Se reprodujo antes del arreglo con datos sintéticos y MockClient. Tres de las cuatro regresiones nuevas fallaban: cierre de sesión con datos ya cargados, cambio de cuenta con respuesta anterior pendiente y acceso a la ruta sin sesión. No se usó MySQL, producción, usuarios reales o datos privados.

## Cambio

PublicListScreen ahora separa el contenedor de sesión del cuerpo del listado. Solo la modalidad privada offers escucha Session. Al salir de la cuenta desmonta el cuerpo anterior y muestra la entrada; al cambiar de identidad crea otro cuerpo con clave de correo y vuelve a consultar el backend. Las respuestas tardías del cuerpo desmontado no pueden restaurar información. Session.authorized conserva su comprobación de generación existente.

Sin sesión configurada no se inicia una lectura ni se ofrece un reintento inválido. Una edición de nombre/teléfono que conserve la identidad mantiene la carga existente y no añade peticiones. Catálogos públicos, directorio, tienda, navegación, acceso restaurado y tema de las guías48/49 conservan su comportamiento y composición.

## Verificación

- Cuatro regresiones nuevas: cierre de sesión, respuesta tardía/cambio de cuenta con403, ausencia de sesión y actualización del perfil de la misma persona sin recarga.
- Nueve pruebas focalizadas aprobadas junto con exploración y gestión de ayudas.
- Suite Flutter:165 pruebas aprobadas; análisis sin incidencias.
- APK candidato QA separado, con LPN_API_BASE_URL local y sin credenciales embebidas. Consultar el hash y estado de compilación en validacion-ayudas-sesion-20261120.json.

Logs antes/después: output/adopcion-movil/*ayudas-sesion*20261120.log. No se atribuyen las capturas de161 pruebas ni los APK instalados anteriores a este cambio. El candidato no se instala para conservar la demo visible que el usuario acaba de revisar. No se modifica ni publica Sites/Railway, no se cambian permisos/migraciones y no se crean commits o ramas oficiales.

## Reparto y continuidad

Majo: contenedor de sesión y regresiones; Sally: esta guía y evidencia; José Carlos: backend intacto. Los paquetes locales se actualizan con las fuentes probadas. Siguiente bloque: continuar una revisión acotada de respuestas privadas y formularios pendientes, sin sustituir la referencia visual49 ni poblar fichas reales con ejemplos. La comprobación física de accesibilidad, firma y datos operativos consentidos sigue separada.
