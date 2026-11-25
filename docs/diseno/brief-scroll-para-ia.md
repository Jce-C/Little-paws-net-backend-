# Little Paws Net · Brief de diseño y movimiento para complementar con otra IA

## 1. Objetivo

Mejorar una demo web aislada que combina la identidad móvil de Little Paws Net con un recorrido narrativo ligado al scroll. El usuario quiere una experiencia más elaborada: **primero entra la imagen sola y luego entran elementos independientes a medida que se desplaza la página**. No basta con mover una foto y una tarjeta juntas.

La demo sirve para aprobar dirección visual y movimiento antes de definir el STYLE.md de todos los paneles. No se está solicitando rediseñar el backend ni programar una aplicación completa.

## 2. Referencias y jerarquía

1. **Identidad propia, prioridad máxima:** https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu?node-id=0-1
2. **Referencia de composición y movimiento:** https://styles.refero.design/style/6c0b77d3-71f9-469d-98aa-4ce1d6d76ac8
3. **Boceto del panel, alcance posterior:** https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=16-2

En el paquete se incluyen el DESIGN.md aportado por el usuario y su video de referencia. El DESIGN.md describe la marca Structured: es inspiración, no una orden de sustituir la marca Little Paws Net. Sus tamaños extremos, paleta negra y pinturas clásicas no deben copiarse automáticamente.

## 3. Identidad que debe conservarse

| Función | Valor |
| --- | --- |
| Fondo crema | #FCF0D3 |
| Superficie marfil | #FFF9EC |
| Texto marrón oscuro | #423222 |
| Texto secundario | #5F513F |
| Beige | #DDC5AB |
| Verde suave | #B2CD99 |
| Cacao oscuro propuesto para sección de contraste | #33291F |
| Fuente funcional de la demo | JetBrains Mono |
| Fuente expresiva de la demo | Leckerli One |

Las dos fuentes proceden de la app móvil y se incluyen con licencia SIL OFL. El logo SVG es el símbolo original del perrito. Mantener proporción y forma. Botones redondeados, escenas cálidas, bordes finos y sombras discretas. La fuente expresiva es para momentos de marca; su uso en formularios y datos debe evaluarse por legibilidad.

## 4. Qué existe en la demo

- Portada con logo, título, frase, botón y marca tipográfica grande.
- Tres escenas: encontrar/reportar; cuidar/recuperar; unir/adoptar.
- Fotografía fija por escena, pequeño movimiento de encuadre y barrido vertical al cambiar de escena.
- Título, tarjeta y contenido con entradas independientes.
- Navegación 01/02/03, progreso y salida del recorrido.
- Sección cacao de comunidad con imágenes circulares y entradas progresivas.
- Ejemplo visual de un panel y ventana de adopción con datos ficticios.
- Créditos, recursos locales, modo reducido y contenido disponible sin JavaScript.

No hay backend, autenticación, envíos, datos reales ni permisos implementados dentro de esta demo. El panel Django existente es otro proyecto funcional dentro del mismo repositorio y queda fuera de esta entrega.

## 5. Secuencia de movimiento actual

Todo se controla mediante la posición de scroll, no mediante un video reproducido ni una secuencia de segundos. La escena ocupa el viewport en un contenedor sticky. La sección completa mide 760vh en escritorio y 700vh en móvil, incluyendo la pantalla fijada.

Para cada escena, el progreso local va de 0 a 1:

| Progreso aproximado | Elemento |
| --- | --- |
| 0–0.12 | Fotografía sin títulos ni tarjetas; permanece la navegación del recorrido |
| 0–0.14 | En escenas posteriores, la nueva foto entra por barrido vertical |
| 0.12–0.22 | Rótulos superiores |
| 0.20–0.36 | Palabra grande mediante recorte y desplazamiento |
| 0.34–0.51 | Superficie de tarjeta, entrando desde un lateral y desde abajo |
| 0.43–0.56 | Índice de tarjeta |
| 0.50–0.63 | Título de tarjeta |
| 0.56–0.69 | Párrafo |
| 0.63–0.76 | Pie de tarjeta |
| 0.66–0.76 | Crédito fotográfico |
| 0.76–0.90 | Composición terminada y tramo de lectura |
| 0.90–1.00 | Salida de las capas de texto antes de la siguiente escena |

Se usa una interpolación suave. Al subir, se revierte la secuencia. Los botones de capítulo llevan a un estado legible de la escena. El movimiento reducido elimina la coreografía y muestra contenido estático.

## 6. Qué queremos mejorar

- Afinar la coreografía para que la entrada por capas sea evidente, elegante y relacionada con el contenido.
- Mejorar la transición de una escena a otra y la conexión entre portada, recorrido y cierre.
- Revisar profundidad, escala, encuadres y espacio del texto sin tapar las caras o elementos importantes.
- Evitar tarjetas vacías durante demasiado scroll y transiciones que obliguen a detenerse en texto casi transparente.
- Evaluar si el recorrido tiene la longitud adecuada en escritorio y móvil.
- Conservar un tramo suficiente de lectura con texto estable.
- Mantener legibilidad y coherencia con el logo y la aplicación móvil.
- Proponer dónde ubicarlo en el panel: una sección opcional de identidad o impacto, posterior a los accesos y tareas, nunca como obstáculo para trabajar.
- Si una mejora necesita otros recursos, listar exactamente cuáles, sus dimensiones, formato y procedencia/licencia.

El objetivo es complementar la propuesta. No es necesario copiar el sitio original píxel por píxel ni añadir efectos a cada formulario administrativo.

## 7. Elementos disponibles y resoluciones

| Recurso | Medidas reales incluidas | Uso |
| --- | --- | --- |
| logo-original.svg | Vector, marco original aprox. 128 × 143 | Símbolo original |
| rescate.jpg | 1920 × 2880 | Copia fuente descargada |
| cuidado.jpg | 1920 × 2880 | Copia fuente descargada |
| hogar.jpg | 1920 × 2880 | Copia fuente descargada |
| *-1600.webp | 1600 × 2400, tres archivos | Recorrido en escritorio |
| *-800.webp | 800 × 1200, tres archivos | Móvil, círculos y miniaturas |
| JetBrainsMono.ttf | Fuente variable | Tipografía funcional |
| LeckerliOne.ttf | Fuente regular | Tipografía expresiva |

Los JPG son las copias fuente usadas en la demo, no una afirmación de máxima resolución disponible en el proveedor. Fuentes y licencias están en assets/. La procedencia fotográfica exacta está en assets/sources.json.

Las fotos del encuentro y del hogar son de cottonbro studio; la escena veterinaria, de Mikhail Nilov. Son escenas ilustrativas de stock, no un caso real seguido por Little Paws Net. Las personas retratadas no avalan el proyecto.

## 8. Restricciones

- **No generar imágenes con IA.** Reutilizar los elementos incluidos o buscar recursos web con licencia adecuada, registrando procedencia y créditos.
- No cambiar el logo ni adoptar la identidad de Structured.
- No incluir credenciales, conexión al backend ni datos personales reales.
- No bloquear ni secuestrar la rueda, el teclado o el gesto de desplazamiento.
- No usar auto-scroll, reproducción automática obligatoria o efectos interminables.
- Mantener salida rápida del recorrido, navegación por teclado y versión con movimiento reducido.
- Mantener el contenido legible y accesible sin animación.
- Preferir HTML/CSS/JavaScript y recursos locales para esta prueba; justificar cualquier dependencia nueva.
- Los títulos, tarjetas y botones deben seguir siendo elementos reales y editables, no texto incrustado en imágenes.
- Conservar licencias y créditos.

## 9. Entrega esperada de la IA especializada

1. Análisis breve de los problemas de la demo actual.
2. Propuesta concreta de coreografía, con fases y comportamiento al subir/bajar.
3. Versión mejorada funcional, con código y recursos necesarios.
4. Vista de escritorio y móvil y explicación de la versión reducida.
5. Inventario de recursos nuevos, si los hay, con resolución, licencia y autor.
6. Cambios propuestos frente a la versión actual y aspectos que quedan por validar.
7. Borrador opcional de criterios para un futuro STYLE.md, claramente separado de decisiones aprobadas.

## 10. Cómo abrir el código incluido

Abrir demo/index.html directamente permite revisar gran parte de la demo. Se recomienda servir la carpeta demo mediante un servidor local para una revisión consistente:

```powershell
py -3 -m http.server 8091 --bind 127.0.0.1 --directory demo
```

Luego abrir http://127.0.0.1:8091/. No requiere npm, compilación, base de datos ni login.

Las capturas muestran estados de la versión actual. Para entender el movimiento hay que probar la demo o revisar el video de referencia, no solo una imagen fija.
