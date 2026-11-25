# Jerarquía visual y avisos emergentes

4 de noviembre de 2026.

El login reserva la acción primaria a Iniciar sesión. Volver a la bienvenida queda como enlace de texto secundario, sin borde ni relleno propio. El pie tiene una superficie discreta para conservar legibilidad sobre la ilustración.

El cierre de landing elimina los números de las cápsulas. Los títulos crecen a 23–29 px y el cuerpo a 17 px, con texto de apoyo menor. Entrar a mi espacio se presenta como enlace secundario, conservando las llamadas principales del recorrido y su identidad visual.

Los errores generales se muestran en un aviso emergente cerrable. Permanecen visibles hasta cerrarlos, anuncian el error mediante `role=alert` y no desplazan el formulario ni exigen confirmar un diálogo adicional. Dentro de un diálogo, el aviso se monta en su capa superior para que siga siendo visible y se pueda cerrar. Los mensajes se insertan como texto, sin interpretar HTML recibido.

Las validaciones de campos permanecen junto al campo. Las indicaciones con enlaces o botones de solución conservan su contexto. Los avisos de éxito utilizan `role=status` y se retiran tras unos segundos. La mejora es progresiva: sin JavaScript siguen disponibles los mensajes originales del servidor.

Los dos recursos nuevos están integrados en el documento del login mediante la lista explícita de recursos públicos permitidos. No añaden solicitudes iniciales de CSS/JS ni consultas mientras la pantalla queda inactiva.

Validación local: 28 pruebas de acceso web pasaron; 14 verificaciones de navegador pasaron, incluyendo error real de captcha local, cierre del aviso, conservación del diálogo, jerarquía, ausencia de números, contraste automático en claro/oscuro y ausencia de desbordamiento móvil. El login mantiene una sola petición inicial del documento. No se modificaron contratos RBAC ni modelos, y no se requieren migraciones. Evidencia en `output/jerarquia-2026-11-04/`. No se hicieron commits ni ramas.

Publicación final Railway: `4023b543-3e19-4182-8505-45030185fad0`, SUCCESS. Siete comprobaciones en producción pasaron: petición única de login, regreso secundario, aviso integrado/cerrable, formulario conservado, cápsulas sin números y título mayor, cierre secundario. Sin errores JavaScript. La comprobación pública no intentó acceder con credenciales incorrectas ni envió formularios de negocio; el error real de captcha se verificó en la base local aislada.
