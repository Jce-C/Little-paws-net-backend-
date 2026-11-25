# 66 · Tienda con fotografía y pedido trazable

22 de noviembre de 2026. Punto9 cerrado en implementación:13/14=92,86%. Punto14 mantiene aceptación en dispositivo y entorno real pendiente.

La tarjeta usa foto a la izquierda y datos a la derecha, altura natural y adaptación con texto ampliado. La ficha conserva esta jerarquía y mantiene Preparar pedido visible, incluso al leer una descripción extensa. Los productos agotados o con precio no interpretable no habilitan el pedido.

La demo incorpora una fotografía de Barking Royalty, obtenida de Pexels, con su licencia verificada el22-11-2026. Fuente: https://www.pexels.com/photo/animal-feed-in-bowl-12928245/ . Licencia: https://www.pexels.com/license/ . Recorte inferior cuadrado, WebP640px,19322bytes; EXIF eliminado. No hay fotografías generadas por IA. La imagen, el producto y el precio de la demo son referencias ficticias; no representan inventario comercial ni respaldan nutrición, marcas o ingredientes.

En producción se siguen usando las fotos autorizadas que cada tienda publique mediante el panel. No se inserta la foto de muestra en productos reales. El fixture commerce/fixtures/catalogo-demo se utiliza únicamente para QA y documenta origen/licencia.

## Recorrido

1. Abrir Tienda y Ver producto.
2. Leer precio, disponibilidad y descripción; Preparar pedido permanece visible.
3. Elegir cantidad. El total de referencia se calcula con decimales exactos, sin flotantes binarios.
4. Iniciar pedido sin pago. El servidor revalida tienda/producto/cantidad/precio.
5. El comprobante muestra el total guardado por el servidor, no una suma confiada al cliente. El precio histórico queda conservado cuando cambia el catálogo.

El pedido no cobra dinero y no reserva existencias. El POST devuelve el mismo resumen que el GET propio del pedido, de forma compatible con los campos anteriores. No hace falta una consulta adicional para mostrar el total guardado.

## Pruebas de cierre

Cinco pruebas específicas Flutter verifican decimales, acción fija con texto1x/2x, agotados/precios inválidos y recibo con precio actualizado. El recorrido HTTP real contra MySQL local verificó publicación de la foto, lectura pública WebP, pedido fuera de stock rechazado, creación correcta, snapshot de precio, propiedad, revocación y retirada de imagen.

El mismo recorrido comprueba dos cuentas abiertas: Ciudadano no ve Usuarios; administración concede usuarios.ver; ambas cuentas acceden sin iniciar sesión de nuevo; renombrar el recurso aparece en el menú; revocar retira el acceso de las dos cuentas. Se usan JWT, middleware, solicitudes HTTP y una base de pruebas descartable; no es una prueba del backend de Railway.

Los resultados finales y la publicación de la demo se registran en validacion.json. No hay commits/ramas/push del Git oficial, migraciones de Railway ni cambios en Figma.
