# Rediseño móvil con referencias visuales · 21 noviembre 2026

> Revisión posterior: la guía57 distingue los requisitos completos y parciales y corrige las afirmaciones de cobertura. Implementar una sección no equivale a completar cada referencia visual.

## Alcance y referencia vigente

Implementación en Flutter, no una maqueta HTML que sustituya al cliente real. Se revisaron las seis páginas del PDF «Referencias visuales para Little Paws Net», los siete ejemplos HTML del ZIP stitch_high_fidelity_interface_replicator y los catorce apartados del encargo integral. El ZIP se usa como referencia visual, no como instrucciones ejecutables ni como un plugin instalado.

Esta guía sustituye los valores visuales de las guías48–52 donde difieren. Bienvenida #FCF0D3, operación #FFF9EC, texto #423222, carbón #252525 y acentos salvia, mantequilla y rosa. Inter continúa como fuente local; titulares28 y texto16, apoyo14. Campos14, botones18 y tarjetas20–24 de radio. El acceso ahora tiene una cabecera orgánica salvia y el perro completo. No aplicar estos cambios globales al panel administrativo Django.

## Cambios y trazabilidad con el PDF

| Referencia | Aplicación real |
| --- | --- |
| PDF1, tienda de muebles | Imagen limpia e integrada, presentación fuera del arte y categorías en Inicio. Fotografías autorizadas en tarjetas de adopción, metadatos separados y acción de detalle. |
| PDF2, rescates | Se retiran textos/controles superpuestos al arte. Búsqueda separada. Huella pequeña en vez del recuadro amarillo grande. Categorías con título fuera de la imagen. |
| PDF3, perfil y hotel | Se conserva la tarjeta cálida del perfil, se refuerza nombre y se explica el alcance de roles. Tienda con superficie fotográfica preparada, categoría, tienda, precio, existencias y detalle. Iconos inferiores reducidos sin reducir sus áreas táctiles. |
| PDF4, AI Notes | Tarjetas agrupadas con icono contenido, texto jerarquizado y decoración fuera de la lectura. Gestión de ayudas solo para cuentas autorizadas; borradores con temas sugeridos. |
| PDF5, formularios | Superficie de lectura diferenciada, requisitos de adopción por temas e iconos; sugerencias de tema y montos que rellenan, sin enviar. |
| PDF6, acceso orgánico | Cabecera curva, marca completa, formularios de acceso/registro directos y jerarquía de acciones. Bienvenida adaptada a ventanas bajas y a texto ampliado. |

Los ejemplos furniture_store_home, bangkok_hotels_card y anana_resort_reviews aportan composición imagen/metadatos. asia_trip_itinerary aporta agrupación de información; ai_notes_your_notes, ai_notes_lecture y ai_notes_editor aportan jerarquía de tarjetas, lectura y sugerencias. No se copia su paleta ajena ni se agregan funciones de viaje/notas al negocio.

## Cobertura de los catorce apartados

1. Identidad: paleta conservada y componentes coherentes. Vidrio acotado a navegación, superficies suaves y alternativa sólida; no desenfoque sobre textos/fotos.
2. Marca: perro completo en acceso y navegación; el estudio orgánico existente sigue disponible en recursos/logo-organico-estudio.svg como alternativa de evaluación, sin sustituir silenciosamente la identidad.
3. Bienvenida: descripción de adopción, organizaciones/veterinarias, ayudas y comunidad; acceso directo. Entrada finita280ms, anulada con movimiento reducido.
4. Inicio: ilustración sin botones ni texto superpuesto, introducción editorial y seis accesos reales. Las rutas y funcionalidades previas permanecen.
5. Adopción: fotos públicas autorizadas, metadatos fuera de la foto y enlace de detalle. Carrusel existente hasta seis fotos con deslizamiento e indicadores. Requisitos agrupados de espacio, responsabilidad, recursos y cuidados; envío, recuperación y controles de sesión conservados.
6. Ayudas: modalidades monetaria, voluntariado y especie diferenciadas; intereses, compromisos y gestión autorizada existentes. Montos sugeridos solo rellenan. No se procesa ni se simula un pago recibido.
7. Directorio: filtros reales por tipo y datos públicos de organizaciones verificadas; iconos distintos para veterinarias, tiendas y fundaciones. Se explicita lo que no está publicado.
8. Comunidad: conserva publicaciones, comentarios, respuestas, reacciones, moderación y recuperación de envío incierto. Autor con inicial real y fecha; temas sugeridos sin envío automático.
9. Tienda: catálogo, categorías, nombre, precio, existencias, detalle y pedido existente. Superficie de imagen preparada; no se vinculan fotografías ajenas a productos reales.
10. Nomenclatura: «Animales que necesitan ayuda» identifica reportes públicos. No se convierte un reporte en mascota adoptable.
11. Navegación: cápsula cóncava y medallón funcional elevado. Perro a Inicio; más en Solicitudes para seleccionar mascota. Cuatro destinos permanentes y accesos complementarios en Inicio; teclado/zona segura y cierre de sesión conservados.
12. Movimiento: transición de rutas existente, respuesta de pulsación Material, entrada breve y carrusel con movimiento reducido. Sin bucles ni demoras para desbloquear acciones.
13. Arquitectura: widgets reutilizables refined_surfaces.dart; sin cambios de esquema, RBAC, contratos privados ni credenciales. Datos ficticios únicamente en el transporte aislado de la demo.
14. Verificación: registros, capturas y manifiesto final en output/redisenio-referencias-2026-11-21. Las pruebas comprueban flujo y protección de sesiones, no solo colores.

## Correcciones encontradas durante la implementación

- Altura insuficiente de tarjetas al ampliar texto: reajuste de la medición y espacio de acción; pruebas con nombres largos y escalado no lineal.
- Aviso de error del compositor fuera de vista: se mueve junto al envío en el área inferior segura. El borrador no se envía al pulsar una sugerencia.
- Reintento de gestión retornaba un Future desde setState y podía producir un error antes de que FutureBuilder escuchara: se inicia la consulta fuera de setState, se observa inmediatamente su fallo y se conserva el resultado original para mostrar/reintentar. Denegaciones401/403 ocultan herramientas; fallos de servicio mantienen reintento.
- Dos expectativas de disposición anteriores se actualizan: la búsqueda ahora debe quedar fuera del arte y la tarjeta de historias se busca mediante desplazamiento, conservando comprobaciones de destino y número de peticiones.

## Datos que no pueden fabricarse

El catálogo público de productos no devuelve fotografías aunque exista ProductoImagen en el modelo. Se requiere un contrato de publicación/consentimiento, entrega segura y retirada antes de exponer ArchivoDigital. La interfaz indica «Sin fotografía publicada».

El directorio no publica logos, contacto o servicios clínicos. No se leen miembros ni contactos privados para llenar estas tarjetas. Se utilizan nombre, tipo, ciudad, dirección y descripción disponibles; queda preparada su composición para información pública futura.

La ficha pública de adopción no publica diagnóstico o tratamientos ni una descripción editorial específica. Se muestran los datos reales disponibles; los cuidados especiales se consultan con la organización, sin inferir enfermedades ni extraer el expediente privado.

Los aportes son compromisos registrados; faltan los medios oficiales de recaudo publicados y un proveedor de pagos para cobrar. Ninguna cuenta bancaria, transacción o aceptación se inventa. Fotos stock de animales solo en registros ficticios de la demo identificada.

## Entrega y límites

Fuentes reales: frontend/mobile/lib y test. El manifiesto enumera archivos modificados. Demo de navegador independiente y APK .visualdemo usan datos ficticios y reiniciables; no son una publicación en Railway ni una integración con producción. El documento Figma editable anterior no se sobrescribe: puede contener correcciones manuales del usuario.

Majo: fuentes y pruebas móviles. Sally: sistema visual, guía y evidencia. José Carlos: revisar contratos públicos pendientes; este bloque no agrega migraciones/backend. Sin commits ni ramas en el repositorio oficial. Firma de distribución, datos consentidos, pruebas en dispositivos físicos/TalkBack y piloto operativo siguen siendo validaciones aparte.
