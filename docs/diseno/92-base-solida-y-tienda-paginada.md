# 92. Base sólida local y tienda paginada

25 de noviembre de 2026. Cierre de consolidación para revisión y preparación de commits, sin publicar. Instrucciones de integración y despliegue posterior en [base sólida local](../entrega/base-solida-local.md).

## Cambio funcional

`GET /api/catalogo/productos/?paginado=1&limite=20` devuelve `results`, `next_cursor` y, en la primera página, `categorias`. El cursor es el ID del último producto, no una URL. Se admiten `buscar`, `categoria` y `despues`; límite válido entre uno y cincuenta. Se valida longitud/formato antes de convertir números. Los parámetros inválidos producen 400.

La respuesta anterior sin `paginado=1` sigue siendo una lista limitada a cien productos. No se retiraron las restricciones de estado, tienda verificada, bajas o fotografías públicas. La página inicial usa dos consultas, incluida la lista de categorías; las siguientes usan una. No se solicita COUNT por página.

La app conserva las tarjetas y añade consulta al enviar búsqueda, categoría global y Cargar más. No consulta por cada letra. Los resultados previos se conservan cuando falla otra página; el reintento usa el mismo cursor. Se rechazan cursores externos/incoherentes y se ignoran respuestas de filtros anteriores. La lista se construye de forma perezosa. Un servidor anterior con respuesta de lista sigue siendo compatible, aunque conserva su límite antiguo hasta actualizar el backend.

## Arranque y configuración

Se retiró el origen Railway implícito del cliente. `LPN_API_BASE_URL` debe configurarse en cada compilación. Si falta o tiene formato inválido, se muestra un aviso sin crear una conexión; esto evita que una prueba local consulte un servicio antiguo por accidente. Los clientes ya compilados no se modifican con este cambio de código. Las demos siguen inyectando su cliente ficticio.

## Verificación

- Backend: **476 pruebas aprobadas** con descubrimiento completo en MySQL local aislado; incluye RBAC, acceso dinámico, dominios, APIs, HTTP y los cuatro casos nuevos de paginación.
- Cliente: **370 aprobadas, nueve optativas omitidas**, incluidos cinco casos de catálogo y dos de arranque sin configuración.
- Herramientas: siete aprobadas. Demos: 18 focales por copia. Análisis limpio en las tres copias; Android debug y web release compilados.
- Django check sin incidencias; makemigrations check no detecta cambios. Este bloque no añade una migración.
- HTTP real con un fixture de 500 productos: 25 páginas de veinte, 500 IDs únicos/ordenados y búsqueda de la última página correcta. Primera respuesta: **5.385 bytes frente a 26.928, reducción del 80 % en esa muestra**. El verificador solo consulta; no realiza compras ni pagos.

Se fortaleció el workflow existente: todas las aplicaciones Django y pruebas de scripts. Se comprobó su equivalente local; la ejecución GitHub queda para después del push. No se presenta como CI remota ya aprobada.

El primer intento de suite completa desde el directorio del workspace descubrió cero pruebas. Se corrigió el directorio de trabajo al backend y el resultado válido fue de 476; el workflow ya usa ese directorio. No se utiliza un resultado de cero pruebas como aceptación.

## Entrega

Paquetes nuevos en `output/base-solida-2026-11-25/paquetes`, acumulados sobre la base indicada. Orden José/backend → Sally/app → Majo/diseño y documentación. Se verifican los tres juntos mediante reconstrucción antes de preparar commits. No contienen credenciales, bases, archivos privados o APKs. Las demos de trabajo se sincronizan y prueban aparte; no son otro backend productivo.

Se conservó el Dockerfile raíz del backend anterior. La guía indica expresamente el contexto `backend-panel/` del servicio vigente y corrige la referencia antigua a Gunicorn: el panel usa Uvicorn/ASGI.

No se hizo commit, push, tag, despliegue o cambio productivo. La base local queda preparada para revisión e integración; las puertas comerciales siguen separadas en la guía de entrega. La lista original mantiene **49/57 (86,0 %)**: el defecto de paginación era un hallazgo adicional, no un punto nuevo que permita inflar ese porcentaje.
