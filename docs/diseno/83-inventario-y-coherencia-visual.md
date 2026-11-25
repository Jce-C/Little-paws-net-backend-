# Bloque 1 — Inventario y coherencia de rutas existentes

Cierre local: 25 de noviembre de 2026. Fuente: PDF de correcciones de doce páginas y guía local de los 17 vídeos. No se incorporan funciones ficticias ni se reemplaza el backend por la demo.

## Alcance comprobado

Inventario de 39 clases públicas de pantalla/contenedor/control, con ruta de código y línea en `docs/evidencias/2026-11-25/inventario-rutas.json`. `PublicReportsPageControls` es un componente reutilizable, no una pantalla adicional. Inicio aloja Explorar; las pestañas de Home alojan catálogo, solicitudes y cuenta. Se conservan los formularios de compatibilidad para servidores anteriores, separados de la evaluación nueva.

Se revisaron 46 vistas/estados, con 92 renderizados Flutter: 390×884 a escala normal y 320×640 al 200 %. Incluyen Inicio, catálogo/ficha/galería, directorio/contactos, comunidad, tienda/producto/pedido, cuenta/perfil/foto/mascotas, expediente/QR, ayudas/gestión/publicación, avisos, solicitudes/detalle/evaluación, reporte/clave/historial y bienvenida/login/registro. Se añadieron capturas de carga, vacío, error, sin sesión y permiso denegado. Las cinco etapas y resultados de los flujos anteriores siguen documentados en las guías 76-82.

No existe todavía una pantalla funcional de adjuntos de adopción: S04/S12 siguen abiertos y no se simula una carga de documentos para completar el inventario.

## Correcciones de este bloque

- Expediente, QR y comunidad incluyen la revisión de identidad, además del correo, en su estado. Una nueva autenticación de la misma cuenta ya no conserva el expediente o QR cargados con la sesión anterior.
- El formulario antiguo de solicitud también queda bajo `SessionActionGate`; guarda su borrador al editar el perfil, pero lo elimina al reautenticar. Se confirma el descarte y se bloquea la salida durante el envío. No se retira la compatibilidad con servidores anteriores.
- Los controles de galería respetan explícitamente la reducción de movimiento.
- La navegación inferior ampliada utiliza dos columnas completas, sin reservar en toda su altura el hueco del botón elevado. Mantiene objetivos táctiles y texto ampliado; utiliza esquinas de 24 en ese modo para evitar el óvalo excesivo. El recorte y cápsula normales se conservan.
- En mascotas personales, la acción secundaria médica se llama Salud y QR, distinguiéndola de Ver ficha; conserva el permiso y la operación médica real. La foto privada añade texto alternativo.

## Criterios visuales compartidos

| Elemento | Implementación vigente | Criterio |
|---|---|---|
| Escala | `lpn_theme.dart` | Título 28, secciones 18, subtítulo/cuerpo 16, metadatos 14; excepciones explícitas en navegación y referencia de acceso |
| Superficies | `form_surfaces.dart`, `refined_surfaces.dart`, `decision_card.dart` | Formularios y tarjetas de lectura de radio 20; controles 14; contenedores destacados 24-28 |
| Tonos | `LpnFormPalette`, `CommunitySurface` | Cinco pasteles asignados explícitamente o mediante ID estable, sin aleatoriedad por reconstrucción |
| Material | `LpnMaterials`, `GlassSurface`, `LpnNavigation` | Vidrio en navegación/cabecera; lectura y formularios opacos. Fallback sólido para contraste/transparencia reducida; sin blur en cada fila |
| Imágenes | cabeceras, galería y fotos públicas/privadas | Espacio reservado, ajustes por pantalla y semántica. Retratos privados y copias públicas siguen siendo contratos separados |
| Movimiento | `organic_surface.dart`, Home, navegación, galería | Entradas breves con opacidad/desplazamiento, sin cambiar geometría del formulario ni esperar por decoración; reducción del movimiento respetada |

Se contrastaron las referencias de comunidad, acceso, otras secciones e identidad del PDF con el atlas. El vídeo 2 se aplica a jerarquía de la información, no a copiar precios de hoteles. Los vídeos 3/8/12/16 separan navegación, creación y acciones secundarias. Los vídeos 4/5/11 orientan movimiento/feedback sin demoras. Los vídeos 6/9/10/13/14/17 orientan proximidad, lectura, formularios y trazabilidad; el 15 solo se aplica a fechas que realmente requieren un intervalo. No se añadieron estadísticas o calendarios decorativos sin datos.

## Resultado y límites

Se cierran V01, V03, V04, V06, V07, V08 y O06 para las rutas existentes: **41/57 (71,9 %)**. V02 permanece abierto: existe la escala compartida, pero el acceso de referencia todavía utiliza pistas dentro de los campos en vez de etiquetas visuales persistentes. No se declara terminado ese punto por conservar el aspecto del login. La revisión completa de teclado/lector, oscuro, orientación y dispositivo físico queda en Q01/Q02.

Las capturas son pruebas con fixtures, no emulador físico ni datos de producción. El atlas registra estados iniciales y los tests recorren contenido diferido; no garantiza que todo formulario quepa sin scroll al 200 %.
