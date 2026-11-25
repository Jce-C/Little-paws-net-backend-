> Actualización del 29 de octubre: las reglas vigentes de RBAC, excepciones, superusuario y pantallas están en [09-rbac-dinamico-y-administracion.md](09-rbac-dinamico-y-administracion.md). Las restricciones históricas de roles del sistema y los diálogos anteriores quedan sustituidos por esa implementación.

# Landing, acceso directo y permisos legibles

Actualización: 28 de octubre de 2026.

## Rutas

- `/`: landing de bienvenida, identidad, nubes y presentación. No crea desafíos de acceso ni consulta módulos o usuarios.
- `/panel/login/`: formulario directo con correo, contraseña y suma. Se conserva CSRF, captcha consumible, límite de intentos y cambio obligatorio de claves temporales.
- `/panel/`: espacio autenticado; navegación según permisos actuales.

El login no carga `panel.js`, `entrada.js`, fondos ilustrados ni `/jsi18n/`. No tiene polling, prefetch ni llamadas Fetch/XHR. La petición HTML, sus recursos estáticos, el envío del formulario y una renovación de suma solicitada por la persona son tráfico necesario. El captcha y los límites requieren operaciones del servidor: no se han eliminado ni trasladado al navegador. Cambiar preferencias o idioma también envía un formulario por acción explícita.

## Recursos

Los originales vectoriales se conservan. La landing sirve WebP: escritorio 1920 x 2287 px (253184 bytes) y móvil 1000 x 1753 px (148222 bytes), frente a SVG de 1160561 y 1159479 bytes respectivamente. La imagen de escritorio no se descarga en móvil; las imágenes del segundo tramo tienen carga diferida. Las nubes y el logo permanecen vectoriales por su bajo peso y escalabilidad. Los fondos no se solicitan en el login.

Las fuentes locales se entregan en WOFF2 con caracteres latinos, acentos y símbolos de navegación. Inter pasa de 876576 a 174176 bytes; JetBrains Mono de 187208 a 48168 bytes; Leckerli One de 43212 a 16432 bytes. El login usa tipografía del sistema y únicamente la fuente pequeña de marca. No conecta a fuentes externas.

## Matriz

La API conserva `codigo`, `recurso_codigo` y `alcance`; añade campos de solo lectura `nombre`, `modulo`, `alcance_nombre` y `ayuda`, traducidos en el idioma activo. No cambian permisos, asignaciones, identificadores ni datos existentes. No requiere migraciones.

La interfaz agrupa por módulo, muestra acciones con nombres humanos y explica su alcance. La búsqueda es local, admite palabras sin acentos y mantiene las selecciones ocultas por el filtro. Los códigos son opcionales. El contador indica permisos elegidos y resultados disponibles. Guardar y Cancelar permanecen visibles. La consulta del catálogo y la matriz se realiza en paralelo después de abrir la ventana, dentro de la sesión autenticada.

Todos los roles siguen siendo editables. Los controles de editor autorizado, organización, asignación y autorización sobre el registro continúan en Django. La consulta de recursos relacionados usa `select_related` para evitar una consulta por fila al mostrar permisos.

## Verificación

Pruebas Django sobre MySQL local aislado: separación landing/login, autenticación y CSRF, permisos editables, etiquetas en español e inglés y ausencia de consultas adicionales por fila. Prueba en Edge: cero Fetch/XHR en login, sin actividad de red posterior a su carga, búsquedas y guardados de matrices globales/de entidad, navegación adaptable y revisión automática WCAG. Esta revisión automática no reemplaza una auditoría manual completa.
