# Preparación del alojamiento después de integrar main

Revisión del 25 de noviembre de 2026. El PR #24 está integrado; no se ha creado un despliegue nuevo. La siguiente entrega debe separar construcción del contenedor, configuración del proveedor y publicación efectiva.

## Comprobaciones realizadas

- Los cuatro commits del equipo se conservaron mediante merge commit, sin squash.
- El servicio anterior `little-paws-api` de Railway estaba conectado al repositorio, pero su autodeploy estaba desactivado. Se comprobó ese estado antes del merge, sin borrar servicios, bases ni volúmenes. Esto no cancela facturas ni acredita coste cero de los recursos existentes.
- Docker Desktop no pudo iniciar su motor Linux en la PC de revisión. Se prepara una comprobación de imagen y arranque en GitHub Actions; no anunciarla como aprobada hasta ver su resultado remoto.
- El nuevo workflow construye desde `backend-panel/`, sin secretos, ejecuta un contenedor temporal acotado a 512 MiB y 0,5 CPU y comprueba salud sin base, redirección HTTPS, recurso estático, usuario del proceso y directorio privado. No migra datos ni publica una imagen o servicio.

## Diseño inicial de bajo consumo

Un servicio ASGI para API y panel, un proceso Uvicorn inicial, una base MySQL y un volumen privado persistente. Android se conecta a esa misma API por HTTPS; instalar la app no requiere otro servidor de backend. Sus imágenes empaquetadas no se descargan del backend en cada apertura; consultas, fotos públicas y operaciones sí consumen red y trabajo del servidor.

No incorporar Redis, colas, réplicas, GPU, IP dedicada o proveedores adicionales sin una necesidad y presupuesto medidos. Mantener paginación, tamaños máximos de archivos, normalización WebP y autorización real, sin almacenar respuestas privadas en cachés públicas.

## Confirmar las condiciones de Northflank antes de crear recursos

Las fuentes oficiales consultadas no coinciden en el requisito de tarjeta:

- [Pricing](https://northflank.com/pricing) anuncia Sandbox gratuito, dos servicios, dos jobs, una base y hasta USD 20 mensuales de recursos; indica que no requiere tarjeta.
- [Documentación de facturación](https://northflank.com/docs/v1/application/billing/pricing-on-northflank) indica que todos los planes requieren método de pago para crear recursos y que Sandbox no debe utilizarse como producción.

No asumir que una cuota de crédito es un límite duro de gasto. Confirmar en la cuenta el plan efectivo, requisitos de tarjeta, cómputo permitido, volumen, transferencia, construcciones y comportamiento al agotar la cuota. No seleccionar Pay as you go ni crear recursos con precio distinto de cero en esta etapa. La decisión de usar servicios gratuitos sigue vigente.

Los ejecutores estándar de Actions en repositorios públicos son gratuitos según [GitHub](https://docs.github.com/en/actions/concepts/billing-and-usage). Esta comprobación no utiliza ejecutores grandes, un registro de imágenes ni artefactos persistentes.

## Pasos previos al despliegue

1. Confirmar que la imagen construye y arranca en el workflow de contenedor.
2. Preparar y probar configuración específica del proveedor: HTTPS, proxy, IP de cliente, hosts y CSRF. El Dockerfile actual usa `config.settings_railway`; no reutilizar automáticamente su confianza en `X-Real-IP` para otro proveedor.
3. Confirmar el presupuesto de cada recurso en la cuenta elegida. Elegir base y volumen privados; no exponer MySQL públicamente ni activar autoscaling sin presupuesto.
4. Configurar claves y credenciales únicamente mediante secretos del proveedor. La clave de cifrado debe conservarse con el respaldo. Revisar y rotar cualquier credencial heredada aún vigente en el historial de Git.
5. Aplicar migraciones a una base nueva, cargar únicamente los datos de demostración previstos y publicar ilustraciones/archivos por los servicios existentes.
6. Ensayar restauración completa de SQL, archivos privados y claves en un destino separado. La restauración SQL local previa no valida por sí sola los volúmenes del alojamiento.
7. Repetir login, autorización/revocación entre sesiones, adopción y reportes desde el teléfono y otra red. Medir RAM, CPU, transferencia, latencia y errores en ese host.
8. Compilar la app con el origen HTTPS, firma y versión de distribución. La demo debug local no se ofrece como aplicación de producción.

## Puertas de publicación

Mantener pendientes explícitos de privacidad, términos/consentimientos, conservación y derechos sobre datos, licencias de imágenes/fuentes/código, accesibilidad y revisión de seguridad. Una imagen con marca de agua conservada como referencia no acredita licencia comercial. No ofrecer pagos, disponibilidad garantizada o certificaciones no implementadas.

Al final, presentar el presupuesto profesional de VPS acordado: cómputo, almacenamiento, transferencia, respaldos externos, dominio, impuestos, renovación y mantenimiento. No contratarlo durante esta fase gratuita.
