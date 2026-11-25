# Guía 71 · Correcciones ciudadanas y paleta

Fecha: 23 de noviembre de 2026. Estado: implementación local revisada; no migrada a Railway.

## Alcance y orden de integración

1. José: revisar e integrar API, modelos y pruebas del módulo 01. Instalar las dependencias ya declaradas. Ejecutar primero en una base local desechable. Revisar `showmigrations` y `migrate --plan`; aplicar `animals.0010` y `rescue.0004` junto con todas sus dependencias pendientes. Hacer respaldo antes de cualquier futura migración real. No mezclar el SQLite de una demo con MySQL de producción.
2. Majo: incorporar el cliente `frontend/mobile` del módulo 02 sobre esa API. Revisar el diff antes de sustituir archivos propios. Ejecutar `flutter pub get`, `flutter analyze` y `flutter test`. Configurar `LPN_API_BASE_URL` para el backend del entorno; nunca incluir credenciales en el código.
3. Sally: incorporar esta guía y las evidencias del módulo 03. Revisar los mosaicos y realizar la aceptación manual de cámara, galería, teclado, lectura de pantalla y regreso tras cerrar Android.
4. Cada integrante crea su propio commit descriptivo después de revisar su bloque. Esta entrega no crea ramas, commits ni despliegues del repositorio oficial. Los ZIP son acumulativos; no aplicar a ciegas parches antiguos sobre archivos que ya contienen el cambio. Usar `git diff` y `git apply --check` cuando corresponda.

## Cambios del PDF

- Paleta móvil compartida: azul, amarillo y naranja suavizados sobre fondo cálido. Texto principal oscuro y variante azul oscura para controles legibles. Se conservan los colores semánticos de error.
- Inicio: fotografía proporcionada optimizada a WebP (38 284 bytes), degradado hacia el fondo continuo, sin banda fija. Adoptar, Rescates, Ayudar y Red son accesos principales; Comunidad y Tienda son tarjetas secundarias.
- Rescates: cabecera compacta integrada, tarjetas con foto/estado/ciudad/resumen. Las fichas mantienen el detalle, la organización responsable y el acceso a apadrinar cuando hay caso asignado.
- Reportar: cámara/galería, previsualizar, sustituir o retirar antes de enviar. El backend valida y vuelve a codificar la imagen en WebP, elimina metadatos y guarda el resultado en SQL en la misma transacción del reporte. Máximo de salida 960 px y 128 KB. Ocultar la publicación también impide descargar su foto pública.
- Apadrinar: acción explícita para registrar el compromiso; luego se consulta la cuenta del caso y la organización receptora. Un error al consultar la cuenta no crea otro compromiso. No se procesa dinero.
- Ayudas: modalidades separadas; gestión organizacional fuera del flujo ciudadano. La gestión continúa condicionada por permisos comprobados en el servidor.
- Recordarme: conserva la preferencia por origen. Android guarda únicamente el refresh token en almacenamiento protegido cuando la API usa HTTPS; no guarda contraseñas. Al desmarcarlo deja de persistir la sesión. En navegador solo persiste la preferencia: una sesión web duradera necesita un mecanismo de cookie HttpOnly/Secure con protección CSRF y política de origen revisada; no se añadió JWT a localStorage.
- Solicitudes: listado privado paginado de 20, miniatura, fecha, estado, detalle, historial y motivo de decisión. Los datos se vuelven a autorizar en cada consulta. No existe acceso a historiales ajenos.
- Disponibilidad: una solicitud pendiente reserva la mascota y la retira del catálogo; rechazo con motivo permite devolverla si no quedan pendientes. La aprobación cambia dueño/estado, cierra custodia y conserva el historial. La solicitud bloquea la fila de mascota antes de comprobar disponibilidad.
- Mascotas personales: nombre/especie y datos opcionales, foto normalizada, titularidad tomada de la sesión y ficha/expediente privados. No crea custodia de fundación ni publicación de adopción. Listado privado paginado y actualización al registrar.
- Aportes: datos bancarios ligados a la entidad verificada del fondo, cifrados con la clave de datos existente. Se muestra titular, banco, tipo, número e identificación; copiar no genera una consulta. Campos no publicados no se inventan. El acceso requiere autenticación y permiso; editar requiere el permiso y asignación del gestor de ese fondo.

## Configurar datos de aporte

Un gestor autorizado usa `PATCH /api/fondos/<id>/datos-aporte/` con `titular`, `banco`, `tipo_cuenta`, `numero_cuenta`, `identificacion_titular` y `confirmar: true`. Requiere entidad verificada, `fondo.reportar_distribucion`, asignación vigente y `LPN_DATA_KEY` gestionada como secreto. El servidor cifra los valores y audita la operación sin registrar números bancarios. La app consulta con `GET` al mismo recurso. No hay una cuenta genérica compartida entre organizaciones. La pantalla dedicada de edición bancaria para gestores queda como mejora de administración; el endpoint está implementado y probado.

## Demostración y límites de aceptación

La demo web usa transporte en memoria, cuentas y números explícitamente ficticios; no conecta con Railway ni cobra dinero. Los datos se reinician al recargar. Para probar se usa `demo@example.invalid` / `LittlePawsDemo2026!`. La demo guarda las fotos seleccionadas en memoria como PNG limitado; producción las normaliza y persiste como WebP en SQL.

Las evidencias visuales son renders de widgets con fuentes reales, no capturas de navegador ni de emulador. Se comprueban las vistas a 390×884 y a 320×640 con texto al 200 %, incluyendo contenido que requiere desplazamiento. Esto no sustituye TalkBack, cámara/galería real, persistencia tras reinicio ni la integración final con Railway. El antiguo punto 14 de aceptación integral continúa abierto por esas comprobaciones.

Ver `lista-implementacion.md` y `validacion-final.json` en las evidencias de esta entrega para el resultado exacto de cada comprobación. No confundir una implementación probada localmente con una función ya publicada en el backend real.
