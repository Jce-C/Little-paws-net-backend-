# Idiomas y preferencias de accesibilidad

El panel funcional de Django ofrece español e inglés, disponibles desde **Idioma y accesibilidad** en el login, el panel y los estados de acceso. Las traducciones no cambian nombres introducidos por personas, datos, códigos de permisos, identificadores ni URLs de la API. La demo estática conserva su función de referencia visual independiente.

## Uso

- Seleccionar Español o English y pulsar Cambiar idioma. Se aplica también a formularios, errores de seguridad y controles/tablas generados por JavaScript.
- Elegir tema Claro, Oscuro o Según el dispositivo; tamaño Normal, Grande o Más grande; contraste Original o Reforzado; y movimiento según el dispositivo o Reducir movimiento. Pulsar Guardar preferencias.
- Restablecer vista recupera los valores visuales originales; conserva el idioma seleccionado.

Las preferencias se guardan un año en cookies del navegador, sin modificar cuentas ni permisos. Los valores se validan contra una lista cerrada; no se ejecuta CSS o código recibido del navegador. Las cookies usan SameSite Lax, HttpOnly y Secure en producción. Los formularios requieren POST y CSRF y no permiten redirigir a un sitio ajeno. Funcionan sin JavaScript. Si se bloquean las cookies, la selección puede no persistir entre visitas.

## Diseño e interacción

El contraste reforzado mantiene crema, tierra y salvia con superficies opacas y texto/bordes más oscuros. El color no sustituye al nombre del rol. El tamaño mayor conserva tablas desplazables y disposición móvil. El zoom del navegador sigue disponible; el selector de tamaño no lo sustituye.

El menú utiliza details/summary nativo, controles con etiquetas, foco visible y objetivos de al menos 44 px en las preferencias. Escape lo cierra y devuelve el foco al resumen; es un desplegable no modal, por lo que no atrapa el teclado. Los diálogos de edición conservan su comportamiento modal nativo.

Movimiento reducido se respeta desde CSS y desde el código de las nubes/entradas, tanto por elección explícita como por la preferencia del sistema. El contenido queda visible, sin transformaciones o transiciones obligatorias. No se intenta sustituir ni simular un lector de pantalla.

## Implementación y mantenimiento

- LocaleMiddleware de Django, después de sesiones y antes de CommonMiddleware; set_language estándar, cookie lpn_language y catálogos gettext.
- locale/en/LC_MESSAGES/django.po contiene traducciones del servidor; djangojs.po, las del navegador. Los .mo compilados acompañan al código para no depender de gettext en el equipo o contenedor.
- seguridad/i18n.py traduce las respuestas de error en el límite HTTP, preservando claves y códigos. El dominio y sus decisiones de autorización no cambian por el idioma.
- seguridad/web/preferencias.py valida y guarda las preferencias. Las plantillas reciben valores seguros antes de pintar, sin depender de localStorage o de un script inicial.
- preferencias.css y preferencias.js contienen presentación y navegación del desplegable. No usan una biblioteca externa ni cookies de analítica.

Para revisar o añadir traducciones, editar los catálogos .po y marcar los nuevos mensajes del servidor con gettext/gettext_lazy, los del template con translate/blocktranslate y los de JavaScript con gettext. No concatenar traducciones con nombres o números: utilizar placeholders cuando sea necesario. Las traducciones de errores del límite HTTP también se mantienen en el catálogo, aunque el dominio devuelva el mensaje original en español.

Desde backend-panel:

```powershell
python -m pip install -r requirements-i18n.txt
python tools/compilar_traducciones.py
```

Commit de los .po y .mo juntos. CI recompila y comprueba que no haya diferencias. polib es una herramienta de mantenimiento, no una dependencia del servidor. El formulario real y entrada.js se mantienen en backend-panel; build-login-django.py solo sincroniza recursos visuales y no los sobrescribe. La demo no genera la autenticación.

## Límites de la verificación

Se comprobaron tamaños 320, 390, 768, 1366 y 2560 px, idioma, contraste, texto mayor, reducción de movimiento, teclado, editores, retorno a español y funcionamiento sin JavaScript. Axe-core revisó siete estados con reglas WCAG 2/2.1/2.2 A/AA. Una revisión automática sin hallazgos no equivale a certificación WCAG completa.

Siguen siendo necesarias pruebas manuales con lectores de pantalla (por ejemplo NVDA/VoiceOver), usuarios con distintas necesidades, zoom del navegador al 200–400 % y revisión lingüística independiente. Las nuevas pantallas y reglas deben añadirse a la misma revisión.

## Tema oscuro

El menú incluye Tema → Claro / Oscuro / Según el dispositivo. La elección se guarda como lpn_tema con la misma validación, seguridad y duración de las preferencias existentes. Por defecto utiliza Claro; Restablecer vista recupera ese modo. Las elecciones válidas ya guardadas se conservan. El contraste reforzado es independiente y funciona también en oscuro.

El servidor entrega la elección en data-theme y en meta color-scheme antes de las hojas de estilo. tema.css utiliza color-scheme y light-dark para adaptar los colores nativos de controles y los componentes, sin invertir toda la página ni depender de un script inicial. En modo automático, un cambio del sistema se refleja sin recargar. Se requiere un navegador moderno con soporte de light-dark; versiones antiguas pueden conservar los colores claros.

La paleta nocturna usa carbón cálido, verde salvia y texto marfil. Las ilustraciones mantienen composición y colores, reduciendo brillo; únicamente el logo monocromo cambia de luminosidad para conservar visibilidad. Las tarjetas, filas alternadas, estados, errores, selectores, diálogos y scroll tienen sus propios colores. El modo claro continúa disponible y no se promete que el oscuro sea más cómodo para todas las personas.

Verificación ampliada: 124 pruebas Django; 12 comprobaciones de navegador (persistencia, modo automático, elección explícita, 320–2560 px y funcionamiento sin JavaScript); nueve estados revisados con axe-core A/AA sin infracciones detectadas. Esto no reemplaza las pruebas manuales y con usuarios indicadas anteriormente.

## Cabecera compacta

Las preferencias se abren desde el botón con icono Lucide de ajustes: junto a «Acceso al equipo» en el login y a la izquierda de «Salir» en la cabecera del panel. El nombre accesible y el tooltip siguen siendo «Idioma y accesibilidad». No hay una franja independiente. En móvil el desplegable se ancla al viewport para conservar todos sus controles dentro de la pantalla; mantiene teclado, Escape y formularios sin JavaScript.

El scroll conserva 12 px de ancho y 3 px de margen interior tanto en contraste normal como reforzado. El modo reforzado modifica el color/opacidad, no el grosor. El fallback estándar usa el mismo ancho nativo fino en ambos modos; los colores forzados del sistema conservan su adaptación nativa.
