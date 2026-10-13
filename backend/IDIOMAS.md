# Idiomas de la API

La API usa español por defecto y admite inglés mediante el encabezado HTTP
`Accept-Language: en`. Las respuestas indican el idioma elegido en
`Content-Language`; `/api/idiomas/` permite comprobarlo. Los nombres de campos
JSON y las rutas se mantienen estables en ambos idiomas para no romper clientes.

Los módulos de rescate, expediente, adopción, fondo y comercio localizan sus
estados, etiquetas de catálogo, avisos y errores de negocio controlados por el
backend. En comercio, productos y tarifas admiten también contenido opcional
en inglés (`nombre_en`, `descripcion_en`, `concepto_en`). Si falta una traducción
de contenido, se devuelve el texto original en español. No se traduce
automáticamente el contenido escrito por usuarios, nombres de entidades,
datos bancarios ni anotaciones médicas. Las claves de estado aceptadas como
entrada mantienen sus valores internos en español; el frontend debe usar los
valores del contrato, no las etiquetas visibles traducidas.

Ejemplo:

```http
GET /api/productos/ HTTP/1.1
Accept-Language: en
```

```http
GET /api/productos/ HTTP/1.1
Accept-Language: es
```

Las pruebas automatizadas cubren ambos idiomas en los procesos principales y
el retorno al español. Esta funcionalidad es del backend: el selector visual
Español / English corresponde al frontend, que deberá guardar la elección y
enviar `Accept-Language` en cada solicitud.
