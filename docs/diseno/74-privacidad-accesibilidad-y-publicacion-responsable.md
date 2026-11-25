# Requisitos de privacidad, accesibilidad y publicación responsable

Solicitud del propietario: 24 de noviembre de 2026. Prioridad transversal de desarrollo y puerta de cierre, junto a optimización y presupuesto de alojamiento (guía 73).

Estado inicial: requisitos registrados; no se afirma que estén implementados ni verificados. La lista es un inventario de trabajo, no una determinación de obligaciones legales. Antes de redactar o implementar se deben identificar jurisdicción, responsable, público objetivo, proveedores y tratamientos reales y consultar fuentes oficiales vigentes. Un abogado debe revisar los documentos y decisiones antes del uso comercial.

## Documentos e información pública

- Política de privacidad accesible desde app, panel y páginas públicas; describir datos, finalidades, destinatarios/proveedores, conservación, derechos y contacto reales.
- Términos y condiciones versionados, coherentes con funcionalidades, responsabilidades y límites reales del servicio.
- Identificación y contacto del operador; no inventar sociedad, dirección, certificaciones o datos de contacto pendientes.
- Política de reembolsos y condiciones comerciales si se habilitan cobros, pedidos o intermediación que lo requieran. Distinguir compromisos/aportes registrados de pagos procesados por terceros. No prometer reembolsos automáticos inexistentes.
- Canal de reclamos de derechos de autor con procedimiento y responsable.
- Publicar proveedores que procesan datos y revisar acuerdos de tratamiento, subencargados, transferencias y condiciones de eliminación con cada proveedor cuando correspondan.
- Publicar disponibilidad y soporte realistas; no afirmar SOC 2 u otras certificaciones no acreditadas ni prometer ausencia de errores.

## Consentimiento, comunicaciones y rastreo

- Casilla inicialmente sin marcar para aceptación de términos cuando corresponda; enlace al documento y registro verificable de usuario, versión y fecha de aceptación. Determinar separadamente base jurídica y avisos de cada tratamiento; aceptar términos no equivale a autorizar todo uso de datos.
- Marketing con permiso separado, opcional y sin preseleccionar. No condicionar acceso a publicidad innecesaria.
- Enlace de baja funcional en correos de marketing; mantener distinción con mensajes transaccionales o de seguridad necesarios. Probar baja y exclusión en envíos posteriores.
- Inventariar cookies, SDKs, analítica, permisos y rastreadores de app y web, incluidos terceros. Auditar tráfico antes y después del consentimiento.
- Definir si se necesita banner y gestor de cookies según tecnologías y jurisdicción reales. Si existen rastreadores opcionales sujetos a consentimiento, bloquearlos antes de aceptar, permitir rechazo y retirada sencillos y conservar la preferencia. No añadir rastreadores para justificar un banner ni bloquear cookies estrictamente necesarias por defecto.
- No entrenar modelos de IA con datos de usuarios sin autorización válida y finalidad definida; revisar también las condiciones de proveedores de IA, si se incorporan.
- Identificar contenido generado con IA según su uso, contexto y requisitos aplicables; inventariar recursos actuales. No presentar imágenes sintéticas, testimonios o datos ficticios como evidencia de casos reales.

## Derechos, menores y ciclo de vida de los datos

- Inventario de datos y finalidades; retirar campos o permisos del dispositivo innecesarios y evitar registrar secretos o datos personales en logs.
- Definir tabla de retención por categoría: cuentas, solicitudes, reportes, fotografías, auditoría, recibos de operaciones, logs, consentimiento y respaldos. Documentar inicio del plazo, fundamento, eliminación/anonimización, excepciones y responsable. No inventar un plazo único para todo ni borrar auditoría/recibos que aún protegen trazabilidad o reintentos seguros.
- Permitir solicitudes autenticadas de descarga/exportación y eliminación; verificar titularidad, aislar datos ajenos, aplicar plazos y excepciones pertinentes, explicar qué se conserva y evitar filtraciones en archivos de exportación.
- Probar propagación de eliminación a archivos, proveedores y copias según su ciclo; una restauración no debe reactivar cuentas/datos eliminados sin control.
- Definir política de edades antes de admitir menores. Si el servicio trata sus datos, aplicar los mecanismos de autorización parental/representación y garantías que correspondan; una casilla genérica no prueba autorización. No recolectar documentación adicional sin necesidad.

## Accesibilidad y experiencia honesta

- Auditar contraste en todos los temas, estados y colores de usuario; no depender solo del color para comunicar estado.
- Texto alternativo útil o marcado decorativo apropiado en web; semántica equivalente para lectores de pantalla en Flutter. Evitar repetir etiquetas innecesarias.
- Navegación completa por teclado en web/panel y dispositivos compatibles, foco visible, orden lógico, diálogos con foco gestionado y sin encierros. Probar lectores de pantalla en Android y navegador.
- Eliminar cuentas regresivas ficticias, escasez inventada, reseñas falsas, promesas no demostrables y patrones engañosos. Distinguir demo y producción.
- Cancelación/revocación tan accesible como contratación/consentimiento. Si existen suscripciones, mostrar precio total, periodicidad, renovación automática y procedimiento de cancelación antes de aceptar.
- Sin cargos ocultos ni opciones de pago preseleccionadas. Comprobar condiciones comerciales de servicios externos integrados.

## Propiedad intelectual y licencias

- Inventariar imágenes, ilustraciones, logos, iconos, fuentes, código, dependencias y SDKs; registrar origen, licencia, versión, atribución y autorización comercial cuando aplique.
- No usar logos de clientes/organizaciones sin permiso comprobable.
- Sustituir recursos de referencia, imágenes con marcas de agua y material de licencia no confirmada antes de distribución comercial. La aprobación previa de una imagen provisional con marca de agua no prueba derechos de uso.
- Cumplir licencias open source: avisos, atribuciones, textos, redistribución y demás obligaciones aplicables; no asumir que todo repositorio público autoriza cualquier uso.

## Orden de implementación y pruebas de aceptación

Pendiente solicitado: instalar y ejecutar al cierre `security-audit`, el arnés de GitHub indicado por el propietario, antes de publicar. Identificar primero el repositorio exacto (nombre ambiguo), verificar procedencia, licencia, permisos y manejo de datos/secretos; no instalar un paquete homónimo sin comprobarlo. Auditar app, API, panel, admin de Django, dependencias y configuración según las capacidades reales de la herramienta. Guardar resultados, corregir hallazgos y repetir las comprobaciones pertinentes. Esta herramienta complementa las pruebas y revisión manual; no certifica seguridad ni cumplimiento jurídico por sí sola. Estado: anotado, no instalado ni ejecutado.

1. Inventario y auditoría del estado real: datos, recursos, flujos comerciales, SDKs y proveedores. Registrar hallazgos y riesgos; no dar por existentes pagos, suscripciones o analítica.
2. Corregir filtraciones, rastreo no consentido, patrones engañosos, accesibilidad y usos de recursos sin licencia antes de ampliar funciones.
3. Definir responsable, políticas de edad, retenciones y procedimientos de derechos; implementar flujos autenticados, registro de consentimiento y comunicaciones.
4. Redactar documentos acordes con decisiones reales, configurar contactos válidos y obtener revisión jurídica.
5. Ensayar exportación, eliminación, baja de marketing, consentimiento/rechazo/revocación, navegación por teclado, contraste y lector de pantalla. Documentar evidencias y fallos pendientes.
6. Cerrar matriz con estado implementado/verificado/no aplicable y justificación. Bloquear publicación comercial si faltan licencias, identidad/contacto del operador, garantías esenciales o revisión requerida.

No se incorpora la frase promocional «sígueme y comenta legal»: forma parte del material de origen, no es una funcionalidad solicitada para Little Paws. La exigencia de no cometer errores se traduce en revisión y pruebas; no es posible garantizar un sistema sin errores ni inmunidad legal.
