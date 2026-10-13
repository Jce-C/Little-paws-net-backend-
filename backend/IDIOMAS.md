# Idiomas de la API

La API usa español por defecto y admite inglés mediante el encabezado HTTP
`Accept-Language: en`. Las respuestas indican el idioma elegido en
`Content-Language`; `/api/idiomas/` permite comprobarlo. Los nombres de campos
JSON y las rutas se mantienen estables en ambos idiomas para no romper clientes.

El módulo de comercio localiza etiquetas de sus catálogos, avisos, errores de
negocio y contenido de producto y tarifa cuando se haya proporcionado su
versión inglesa (`nombre_en`, `descripcion_en`, `concepto_en`). Si falta una
traducción de contenido, devuelve el texto original en español. No se traduce
automáticamente el contenido escrito por usuarios ni los nombres de tiendas.

Ejemplo:

```http
GET /api/productos/ HTTP/1.1
Accept-Language: en
```

```http
GET /api/productos/ HTTP/1.1
Accept-Language: es
```

El selector global de idioma ya está disponible, pero las respuestas de los
otros módulos (`rescue`, `animals`, `adoptions`, `funds`, etc.) requieren
traducciones propias antes de afirmar que toda la plataforma es bilingüe. Las
pruebas automatizadas cubren ambos idiomas en comercio y el retorno al español.
