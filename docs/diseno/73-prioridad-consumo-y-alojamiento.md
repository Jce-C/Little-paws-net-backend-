# Prioridad de consumo y alojamiento

Acuerdo del 24 de noviembre de 2026. Es una condición de entrega, no una optimización opcional al final.

## Decisiones del propietario

- Privacidad, accesibilidad, licencias y prácticas comerciales transparentes son también prioridades de publicación. Aplicar durante el desarrollo y verificar antes de la entrega comercial la lista de la guía 74. No presentar esta lista ni documentos de plantilla como garantía de cumplimiento legal o ausencia de errores. Los textos finales requieren revisión jurídica según jurisdicción, responsable y funcionamiento real.
- Acuerdo final de alojamiento: usar únicamente opciones gratuitas por ahora. Al cerrar la versión local, antes de publicar, presentar control de consumo y presupuesto comparativo para una operación profesional en VPS. Incluir mensualidad y renovación, impuestos, transferencia excedente, disco, respaldos externos, dominio si se requiere, mantenimiento y margen de crecimiento; distinguir costes fijos y variables. Estimar capacidad con mediciones, sin prometer usuarios ilimitados. No contratar el VPS durante esta etapa.
- Completar y probar primero la app, API, panel web y administración de Django en local. Después preparar paquetes revisables para tres integrantes y actualizar GitHub. No crear commits ni publicar por adelantado.
- Minimizar CPU, RAM, transferencia, almacenamiento y construcciones durante todo el trabajo. No contratar tamaños de pago, réplicas o servicios adicionales sin explicar su coste y acordarlo.
- Northflank queda como candidato, no como despliegue completo ni garantía de coste cero. La cuenta muestra Free; el formulario de addon exige tarjeta. No se ha creado la base de datos ni introducido datos de pago durante esta revisión.
- No cancelar ni borrar Railway sin comprobar facturación y recuperar los datos y archivos necesarios. Cambiar de proveedor no elimina deudas anteriores.

## Referencias que hay que reconsiderar antes de publicar

| Referencia | Uso posible | Condición |
|---|---|---|
| https://github.com/ripienaar/free-for-dev | Encontrar almacenamiento, correo y monitoreo con nivel gratuito | Verificar límites y condiciones en el proveedor; no dispersar el sistema sin ahorro comprobado. |
| https://github.com/awesome-selfhosted/awesome-selfhosted | Herramientas para respaldos o administración si se utiliza servidor propio | Medir memoria, mantenimiento y coste del servidor; software gratuito no equivale a alojamiento gratuito. |
| https://github.com/DigitalPlatDev/FreeDomain | Dirección gratuita opcional | Revisar registro, renovación y condiciones vigentes; no aporta capacidad de servidor. |

No instalar todos los complementos por defecto. Registrar la necesidad, ahorro esperado, límite gratuito y mantenimiento antes de elegir uno.

## Primer ajuste local

El contenedor arranca con un proceso Uvicorn por defecto, configurable con WEB_CONCURRENCY. Esto evita duplicar el proceso de aplicación y el lector de revisión SSE del panel en un piloto pequeño. No reduce a la mitad toda la memoria: MySQL, conexiones, sistema y otros recursos siguen consumiendo. No cambia el tamaño contratado ni bloquea cobros.

Se conserva ASGI y la sincronización de permisos. Las autorizaciones siguen comprobándose en cada operación. No habilitar caché pública de respuestas privadas para ahorrar tráfico.

## Revisión inicial del código

- Las fotografías públicas subidas ya pasan por normalización a WebP con dimensiones y peso acotados, sin guardar el original en ese circuito. Evitar recomprimirlas en cada lectura.
- La sincronización web usa un lector de revisión por proceso mientras hay clientes; no uno por usuario. Revisar su coste SQL con sesiones simultáneas antes de modificarla.
- No se encontró Timer.periodic en el cliente Flutter en esta búsqueda inicial. Esto no demuestra que no existan peticiones duplicadas o recargas por navegación: necesitan medición.
- Algunas fotografías llevan no-store para respetar visibilidad y retirada. Cualquier cambio de caché debe probar retirada, revocación y cambio de cuenta, no solo velocidad.

## Cola de implementación y evidencia para cerrar

1. Inventariar imágenes y fuentes realmente empaquetadas. Medir bytes, dimensiones, transparencia y referencias; convertir solo si el resultado reduce peso y conserva fidelidad. Distinguir recursos incluidos en Android de descargas del backend.
2. Medir peticiones por recorrido: login en reposo, inicio, adopción, reporte con foto, cambios de roles, auditoría y cambio de cuenta. Separar descarga fría de caché y eliminar duplicados sin ocultar datos actualizados.
3. Medir consultas SQL y tiempos en listados/detalles. Verificar paginación, select_related/prefetch_related y catálogos; no cargar tablas completas en formularios.
4. Revisar Flutter: evitar solicitudes durante build, agrupar cargas compatibles y cancelar/ignorar respuestas obsoletas al salir. Conservar el aislamiento de sesión y el reintento seguro existente.
5. Revisar panel y admin de Django: listados paginados, filtros, relaciones costosas y acciones acotadas. Mantener trazabilidad y permisos.
6. Ensayar un proceso con sesiones concurrentes y sincronización SSE. Registrar RAM máxima, CPU, errores, tiempos y consultas. Definir capacidad admitida con evidencia; aún no está certificada.
7. Estimar almacenamiento y transferencia por usuario/foto y fijar retenciones, respaldo y restauración. No borrar fotos ni auditorías de negocio indiscriminadamente.
8. Elegir alojamiento al final, revisar cuotas de cómputo, red, disco y construcciones por separado, y comprobar si existen topes efectivos o solo alertas. Un aviso de gasto no es un bloqueo de cobro.

Estado: prioridad documentada y primer ajuste local aplicado. Auditoría integral de consumo, ensayo de carga, migración y publicación siguen pendientes. Las evidencias de la guía 72 corresponden a la revisión previa; no se presentan como pruebas nuevas de este ajuste.
