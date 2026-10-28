# Vista del panel editorial

Vista compartible publicada: https://little-paws-panel-diseno.mintyboar64.chatgpt.site

Es una copia estática pública del diseño, con selector de perfiles y datos ficticios. No depende del computador local ni se conecta al backend. Su fuente y configuración de Sites se conservan en `sites/panel-little-paws/`. Incluye la nueva bienvenida, el acceso de demostración y la galería de estados.

Abrir http://127.0.0.1:8094/ mientras esté iniciado el servidor local.

Desde la raíz: `py -3 -m http.server 8094 --bind 127.0.0.1 --directory demos/panel-editorial`.

Contiene 33 vistas de panel, 13 perfiles con temas distintos y nueve estados de acceso. La barra superior permite cambiar de actor. Se generó a partir de las plantillas Django con contextos ficticios; no inicia sesión ni utiliza cuentas reales. Las peticiones de lectura se resuelven con ejemplos en `preview.js`; las escrituras se rechazan y no persisten cambios. Lucide Static 1.62.0 aporta los SVG locales que reemplazan los rombos; la guía y el generador están en `frontend/panel-design/`.

El login real permanece en http://127.0.0.1:8000/panel/login/. La demo pública empieza en la bienvenida y usa la composición aprobada de Figma con seis nubes independientes. El formulario solo admite los datos de ejemplo que ofrece su propio botón; no envía ni almacena credenciales. La demostración anterior del scroll en 8092 permanece como referencia aislada.

Guía de estilo: [STYLE.md](../../STYLE.md). El boceto completo de Figma incluye ventanas que todavía requieren formularios y conexión de interfaz: esta demo no pretende implementarlas todas.
