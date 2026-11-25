# Composición de mensajes aislada por sesión · 21 noviembre2026

Durante la ejecución local interrumpida por la solicitud de Figma se reprodujeron seis fallos: el borrador de comunidad/interés seguía montado al salir/cambiar de cuenta, el nombre de autor no se actualizaba al editar el perfil y una entrada anónima aún mostraba el editor. Aunque el guard de envío bloqueaba una cuenta distinta, no desmontaba el texto anterior.

PublicMessageScreen reutiliza SessionActionGate. El formulario se crea por identidad y se desmonta al salir; el perfil actualizado de la misma identidad conserva el borrador. Una respuesta tardía de la cuenta anterior no cierra el compositor de la cuenta nueva. Se conservan la protección de envío único, comprobación de resultado incierto y confirmación de descarte. No cambia el contrato ni los permisos del servidor.

Seis regresiones fallan antes y pasan después, con MockClient y datos sintéticos. Análisis limpio y180 pruebas completas. Se compila un candidato QA con API local, separado y no instalado. No se modifica la demo visual instalada ni Sites, el backend o Railway. Los primeros intentos de prueba con HTTPS quedaban esperando almacenamiento nativo; se detuvieron y se corrigió el harness a HTTP loopback simulado sin persistencia. El log antes/después definitivo corresponde al transporte corregido.

Evidencias: *mensajes-sesion*20261121.log y validacion-mensajes-sesion-20261121.json en output/adopcion-movil. La inspección de descarte mientras cambia la identidad con un diálogo ya abierto sigue como posible revisión posterior; no se afirma haber probado todos los ciclos de modal/sesión.

Majo: gate y seis pruebas. Sally: guía/evidencia. José Carlos: backend intacto. Guía52 continúa como referencia visual y la54 documenta la exportación Figma. No publicar desde la recurrencia ni cambiar diseño sin nueva petición.
