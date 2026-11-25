# 63 · Jerarquía de tarjetas y actividades de ayuda

Fecha: 22 de noviembre de 2026. Cambios locales en el repositorio oficial; sin commits, ramas, PR ni despliegue Railway. La demo pública independiente usa datos ficticios.

## Referencias y decisiones

Se leyeron `guia-aplicacion-little-paws.md` y `analisis-visual.md` de los 17 vídeos. La tarjeta de hotel suministrada corresponde a los criterios 2 y 17: imagen separada, título dominante, metadatos subordinados, proximidad y acción inequívoca. También se aplican 6 (menos cajas), 9 (escala de lectura), 12/16 (prioridad de botones). No se copian precios, valoraciones, cancelaciones ni datos comerciales al dominio de adopción.

Contrato común: radio20, imagen a ancho completo cuando existe, cuerpo16 de padding, título20/700 en tarjetas de decisión; texto secundario14; separaciones4/12/16 y acción de48 mínimo. ListTile tiene título18/700 y apoyo14. Las superficies de formulario conservan sus etiquetas y leyendas. El modo sólido sigue definido por el tema y las tarjetas no añaden filtros de vidrio a cada fotografía.

| Familia | Información protagonista | Apoyo y acción |
|---|---|---|
| Adopción | Foto y nombre; estado explícito | Edad/sexo/tamaño, especie/raza, descripción breve y Ver detalles alineado |
| Productos | Foto, nombre y precio24/700 | Categoría/tienda, stock y Ver producto; no se presenta como compra confirmada |
| Reportes en carrusel | Situación y estado | Ciudad y descripción breve, Ver reporte; no imagen inventada |
| Reportes completos, solicitudes, notificaciones y listas de gestión | Título de registro18/700 | Estado/contexto14; heredan el contrato ListTile |
| Directorio, ayudas y fondos | Nombre20/700 | Tipo/ciudad junto al nombre; propósito y acción correspondiente |
| Mascotas propias / resumen de perfil | Nombre y estado | Datos secundarios agrupados; expediente sujeto a permisos |
| Comunidad | Contenido del mensaje | Autor/fecha separados y acciones compactas; no se convierte un post en ficha comercial |
| Formularios / editor de convocatoria | Propósito y etiquetas persistentes | Agrupación por actividad/canal, acciones fijas, error junto a las acciones |

Las familias comparten criterios, no una altura idéntica. El catálogo mide el texto con su peso real; se corrigió un desbordamiento4px detectado por la prueba de alineación. Los listados y los formularios crecen con el contenido y la ampliación de texto. La aceptación visual integral de todas las pantallas sigue en el punto14; no se presenta como revisión manual de cada tarjeta.

## Punto6 · Actividades y canales

- `ProgramaAyuda` por fundación: hasta8 actividades (título, tarea, horario, requisitos),4 canales (título, propósito, URLHTTPS), publicación/borrador, editor y fecha.
- GET/PATCH `/api/ayudas/organizaciones/<id>/programa/`: permiso configurable `ayudas.gestionar` en esa organización; versión obligatoria y conflicto409 sin sobrescritura. Bloqueo compartido de seguridad y comprobación del permiso al escribir.
- Autorización explícita para publicar; solo organizaciones verificadas/activas. Retirar conserva borrador y elimina datos del directorio. Desactivar recepción de voluntarios oculta las actividades, conservando canales publicados.
- Panel: Organizaciones → Actividades y canales → formulario por secciones, publicación y Guardar. También `/panel/ayudas/<id>/programa/`. POST/CSRF, campos semánticos y fallback sinJavaScript. Cancelar vuelve a organizaciones. Nuevos textos del panel tienen catálogoEN.
- App: Ayudas → Gestionar ayudas → organización → Editar actividades y canales públicos. Primero guardar/descartar cambios de recepción/necesidades; después editar la publicación. Error, Guardar y Cancelar permanecen visibles; revocación403 oculta el formulario. Conflicto o resultado incierto bloquea el reenvío hasta consultar de nuevo.
- Público: Ayudas → Tiempo y voluntariado → actividad → Me interesa esta actividad. La solicitud conserva el título de la actividad como snapshot y la disponibilidad que escribió la persona. El servidor rechaza una actividad retirada/cerrada antes del envío.
- Ayudas → Canales publicados por las organizaciones: acceso público sin login. Muestra únicamente organizaciones con canales publicados, propósito y enlace seleccionable/copiar. Consultar/copiar no visita el tercero.
- Los enlaces son declarados por la organización; la plataforma no certifica titularidad, no cobra ni confirma pagos. La demo usa `example.invalid` expresamente ficticio. No se inventaron cuentas bancarias.
- El interés de ayuda sigue siendo uno por usuario/organización/modalidad: reintento idéntico no duplica; un contenido/actividad diferente devuelve409. No implica plaza aceptada, entrega ni pago. La aceptación operativa se acuerda con la organización.

## Integración y comprobación

Migraciones nuevas `core.0013_programa_ayuda` y `core.0014_interes_actividad`, aplicadas únicamente a la BD aislada de pruebas. No migrar la BD real sin revisar e integrar el paquete. El directorio añade `programa_ayuda` opcional y usa select_related, sin consultas por cada tarjeta. Registros anteriores sin programa siguen funcionando.

Pruebas: permisos anónimo/ciudadano/organización ajena/revocación, consentimiento, listas y campos anidados, HTTPS sin credenciales, concurrencia409, borrador/retirada, cierre de voluntariado, snapshot de actividad, formularioPOST conCSRF y publicación real, directorio sinN+1. Flutter prueba edición exitosa/403/409, validación de contrato, selección de actividad, canales anónimos bajo navegación explícita, ausencia de consulta antes del clic y tarjetas a320px/escala2. Compilación web y APK debug de demostración.

Ver `validacion.json` y los logs finales del bloque. Los logs iniciales de diagnóstico no representan el estado final. La prueba visual del catálogo se observó en Brave a100%; el puente de UI se desconectó antes de poder exportar la captura o recorrer Ayudas. No se atribuye una captura inexistente ni aceptación manual de ese flujo. Las pruebas de widgets/servidor de Ayudas sí se ejecutaron.

Cierre de implementación del punto6:10/14=71,43%. Pendientes7 (logos públicos),8 (fotos de perfil),9 (composición/fotos de tienda) y14 (aceptación integral, entorno real y dispositivo físico/TalkBack). No se afirma que el producto esté listo para venta.
