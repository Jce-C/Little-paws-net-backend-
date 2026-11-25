# Exportación editable de la app móvil a Figma · 21 noviembre2026

Archivo nuevo: https://www.figma.com/design/WIsLSGiowLRP3hgUGH5BGl?node-id=19-103

84 frames:6 de acceso,12 de inicio/adopción,11 de rescates,15 de ayudas/red/tienda,15 de comunidad/cuenta y25 de estados/diálogos. Además hay guía de edición y componentes locales. Se cubren las rutas móviles implementadas y variantes principales; no se afirma enumerar todas las combinaciones posibles de datos/validaciones ni incluir el panel web.

La entrega es semántica y editable: unas2700 capas en los tableros, Inter comprobada, controles/espacios/radios vinculados a variables, campos y botones mediante instancias. Marca e iconos Material son vectores; solo las ilustraciones y fotos individuales usan rellenos de imagen. No se importan screenshots de la UI completa. El QR es una referencia visual, no una credencial real.

Se detectaron y corrigieron alturas fijas de100 en componentes que debían ajustar al contenido. Los recursos WebP se cargaron inicialmente pero no se renderizaban en Figma; se transfirieron copias PNG de los mismos originales y se verificó su visualización. Los originales optimizados de la app permanecen intactos. También se corrigió la opacidad del fondo de los diálogos, se mantuvieron transparentes los botones de texto y se añadieron los iconos de visibilidad de contraseñas.

Se comprobó cada tablero con una composición renderizada y los textos dentro de los contenedores. Los frames largos muestran el contenido completo y crecen; los campos se pueden editar sin quedar ocultos por el scroll. Modificar este archivo no modifica automáticamente Flutter: habrá que trasladar las correcciones aceptadas al código.

Inventario de IDs, páginas, dimensiones y auditoría: output/figma-app-editable-2026-11-21/inventario-y-validacion.json. Solo se crea el documento Figma solicitado. No se altera Railway, Git oficial o la demo Sites. Majo puede ajustar flujos y componentes; Sally los fundamentos, composición y contenido; José Carlos conserva API/permisos.
