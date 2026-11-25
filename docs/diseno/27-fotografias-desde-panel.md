# Publicar y retirar fotografías desde el panel

Revisión local del 19 de noviembre de 2026. Flujo completo: Mascotas → Fotografía → archivo y confirmación → Publicar. La misma publicación se consulta en Android. Sin commits ni despliegue.

## Interacción y permisos

El enlace Fotografía aparece en las fichas donde el permiso efectivo mascotas.publicar_adopcion y su contexto lo permiten. La ruta propia /panel/mascotas/{id}/fotografia/ vuelve a comprobar autorización y estado. No se usa un diálogo emergente para la tarea principal ni se duplican servicios de imagen: se llama al backend de fotografías existente.

Seleccionar archivo crea una vista previa local con URL temporal y no hace un POST. Se validan tamaño, firma y dimensiones como ayuda; Django sigue siendo la validación autoritativa. El consentimiento no se premarca y se restablece si cambia el archivo. Un archivo inválido se puede quitar sin salir de la pantalla. La URL temporal se libera al reemplazar, limpiar o descartar/navegar.

Publicar requiere un envío explícito. Al cancelar con cambios se puede seguir editando o descartar; no se ofrece publicar implícitamente como Guardar y continuar. Se incorporó un atributo específico data-explicit-submit para esa regla, separado de los formularios de bajas con motivo/aceptación. Esto evita que la lógica de eliminación intente leer campos inexistentes en la pantalla de fotos.

La publicación actual permanece visible hasta un guardado correcto. Los errores conservan su estado en el servidor, tienen mensajes legibles y un formulario de reintento. La retirada tiene una pantalla de confirmación propia, también disponible cuando la mascota sale del catálogo. Se comprueban CSRF, permisos revocados y el límite de cargas compartido con la API. No se cambian roles, concesiones ni esquema.

## Diseño y guías

Dos columnas en escritorio y una en móvil, con formulario primero, jerarquía de acción primaria, controles nativos etiquetados y estados claro/oscuro. Las nuevas etiquetas, ayudas y validaciones se tradujeron al inglés.

Modern Web Guidance aplicado: html, con dimensiones declaradas para las imágenes y acciones/navegación semánticas ("DO specify width and height on all <img> tags"); brand-consistent-forms, con accent-color y alternativa @supports not que conserva foco/estado del checkbox. Se mantuvo el sistema de TypeUI y la paleta existente; no se agregaron librerías ni peticiones de assets nuevas: estilos y mejora progresiva usan los recursos ya cargados del panel.

## Validación

316 pruebas Django en esquema MySQL aislado recreado y eliminado; diez nuevas pruebas web cubren formulario/consentimiento, servicio compartido, errores, acceso/contexto, revocación, CSRF, retirada fuera del catálogo, inglés cuota y retorno con el nombre configurado del recurso. El APK conserva sus 77 pruebas Flutter y no necesitó recompilarse.

En navegador: vista previa sin POST, publicación con un único POST, archivo falso bloqueado y limpiable, seguir editando conserva selección, descartar libera la URL, retirada deja GET público en 404 y cero errores JS. Se comprobaron 320, 390, 1366 y 2560 px sin desbordes; Axe no detectó infracciones en esta pantalla en claro y oscuro. No equivale a certificar todo el proyecto.

Se publicó un patrón QA explícitamente sintético en una ficha temporal. Android mostró ese mismo patrón, verificado con controles y captura reales del emulador. Después se retiró desde el panel y se eliminaron ficha, metadatos y archivo mediante el comando QA. No se publicaron fotos reales ni se tocaron cuentas reales.

Evidencias: output/adopcion-movil/panel-fotos-*.log y *.json; capturas web foto-panel-* y Android 14-foto-publicada-desde-panel.png en output/diseno-materiales-2026-11-19.

## Reparto y siguientes pasos

Sally: vista/formulario, plantilla, enlace contextual, estilos, JS, traducciones, pruebas web y guía. José Carlos: revisión de los servicios existentes y regresión. María José: verificación de lectura en Android. El paquete 03 incluye un parche específico del panel; aplicar después de los parches previos y comprobar el contexto de cada archivo. Las traducciones de este bloque quedan separadas del arreglo de recurso inexistente para evitar insertar las mismas entradas dos veces.

Antes de fotos reales en producción siguen pendientes volumen privado persistente, respaldo/restauración, caché compartida para el límite en varias réplicas y un piloto con fotografías autorizadas. Continúan TalkBack/dispositivo físico y rendimiento. Railway no se modificó.
