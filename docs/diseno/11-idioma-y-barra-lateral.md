# Idioma, preferencias y barra lateral

Actualización del 30 de octubre de 2026, sobre el panel Django real.

- Se completó la localización de plantillas, formularios, nombres predeterminados de roles/recursos, métricas, estados, filtros de auditoría y mensajes interactivos. Los catálogos inglés del servidor y JavaScript se compilaron; el de JavaScript contiene solo 150 mensajes utilizados para limitar su peso.
- Los nombres de personas, mascotas y organizaciones, códigos estables, valores enviados en formularios y contenido personalizado se conservan. Las etiquetas de las opciones se traducen sin cambiar sus valores de negocio: por ejemplo, Foundation envía `fundacion`.
- Los errores de formulario muestran mensajes legibles, conservando la estructura y códigos de error de la API. El login integra el catálogo interactivo en el documento, manteniendo una petición inicial.
- Vista utiliza botones más compactos, con icono y etiqueta en una fila y cambios inmediatos. El popover continúa adaptándose a móvil y texto ampliado.
- El avatar y la píldora del rol en Mi espacio comparten el acento persistente del usuario. El modo oscuro utiliza un fondo compatible con su contraste; el color no altera roles ni permisos.
- Se eliminó la X y el margen antiguo bajo el logo. En escritorio, el botón superior alterna entre el menú completo y una barra de 72 px con iconos, nombres accesibles, título al pasar el puntero y sección activa marcada. El estado se conserva entre páginas. En móvil el menú se abre sobre el contenido y se cierra con el mismo botón o Escape; cerrado queda fuera del foco.
- La sincronización mantiene la estructura de etiquetas de la barra al actualizar nombres y accesos. Configuración sigue en la cabecera, sin un grupo vacío en el lateral.

Archivos principales: plantillas de `seguridad/web`, `contexto.py`, `dashboard.py`, `negocio.py`, `usuarios.py`, `i18n.py`, `templatetags/panel_i18n.py`, `templatetags/publicos.py`, catálogos `locale/en`, `administracion.js`, `sincronizacion.js`, `interacciones.js`, `preferencias.js`, `preferencias.css` y `compacto.css`.

Verificación: 170 pruebas Django aprobadas, recorrido en inglés de 11 vistas y formularios, guardado de usuario y protección de borradores, barra persistente, controles en móvil y texto ampliado, 15 combinaciones de resolución sin desbordamiento de página, y revisión axe del lateral claro/oscuro y Vista. Se comprobaron siete perfiles visuales: avatar y píldora comparten el acento correspondiente. Los datos de prueba se mantuvieron en la base local aislada.

No se crearon commits ni ramas en el repositorio oficial. Esta actualización no requiere migraciones ni modifica los accesos de las cuentas.

Publicación verificada: `bca4052f-a5e0-4a53-a2e2-fe022534c043`, SUCCESS. En producción se comprobaron el dashboard y formulario en inglés, la barra de iconos persistente, el color compartido de avatar y píldora y los controles compactos; ningún error JavaScript observado. El login en inglés conserva una petición inicial. La sesión temporal de verificación se cerró y su archivo se eliminó.

## Barra superior durante el desplazamiento

Se redujo de 72 a 64 px en escritorio, con altura consistente en móvil y menor separación alrededor del separador de navegación (5 px a cada lado). Es sticky en todas las vistas que comparten la base del panel. En móvil, el lateral se abre debajo de la cabecera para mantener disponible el botón de las tres rayas. Se comprobaron nueve recorridos con scroll en tres resoluciones, el plegado/desplegado sin perder scroll y 15 casos de responsividad sin desbordamiento de página.

Despliegue de la barra fija: `fab35cf3-fd76-4f4c-9f0e-2d6322d40d8b`, SUCCESS. Verificación en producción: nueve recorridos con cabecera visible y tres pruebas de alternancia del lateral sin cambiar la posición de scroll, todos aprobados y sin errores JavaScript.
