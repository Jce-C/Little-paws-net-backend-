# Perfil Android y consulta de roles propios

Referencia: [Figma, frame 156:1796](https://www.figma.com/design/sR48elLBOFINiQXIfwJsNu/Untitled?node-id=156-1796).

Se consultaron contexto detallado y captura antes de implementar. El perfil usa el título centrado de 15 puntos, contenido de hasta 295 puntos, tarjeta crema de identidad con borde cálido, avatar ilustrativo predeterminado de 54 × 54 y secciones más compactas. Los nombres, correo y teléfono siguen siendo los de la cuenta autenticada; la ilustración no se presenta como fotografía de la persona. Los textos largos se envuelven y respetan la escala del sistema.

## Roles reales, de solo lectura

La sección Mis roles consulta el endpoint existente GET /api/seguridad/mis-accesos/ mediante Session.authorized. No se modifica Django, el contrato ni la autorización. La petición solo se inicia al abrir Mi cuenta con sesión válida. La pantalla anónima y el formulario de login no consultan roles. Cada entrada al perfil carga una vez; cambiar datos de contacto no dispara otra consulta. Actualizar mis roles permite una lectura explícita, sin polling ni reintentos automáticos de errores 403.

Se distinguen roles globales de los de cada organización y se eliminan duplicados únicamente dentro del mismo contexto. El endpoint devuelve identificadores estables de rol, que se muestran tal cual, bajo una explicación clara; no se inventan etiquetas para los roles personalizados. Una futura ampliación del contrato podría añadir sus nombres editables. Esta versión no afirma que los códigos sean los nombres configurables del panel.

Los switches ilustrativos de Figma no se convierten en controles para otorgarse privilegios. La lista es de solo lectura y lleva indicación de candado. Las asignaciones se administran por las personas autorizadas en el panel. Un error elimina los roles previamente mostrados; cerrar sesión descarta también respuestas tardías. No se adjudica CIUDADANO como rol de respaldo si la respuesta está malformada o vacía.

Mis mascotas abre el listado real existente; no se añade a Bruno, vacunas ni expedientes ilustrativos del prototipo. La edición de contacto, sus confirmaciones y el cierre de sesión conservan sus comportamientos. Las operaciones siguen autorizándose en el servidor: esta lista es una fotografía al consultar, no una suscripción en tiempo real a cambios de permisos.

## Verificación

- 115 pruebas Flutter aprobadas y análisis limpio; APK debug QA compilado.
- Siete regresiones nuevas: anonimato sin consultas, lectura autenticada y contextos, denegación sin datos anteriores/bucles, respuesta tardía tras logout, respuesta inválida sin rol inventado, texto 200 % y contratos de organizaciones malformados.
- Se conservan las ocho regresiones de edición de perfil, incluida respuesta tardía tras logout.
- Contrato local real: anónimo 401 y ciudadano sintético QA 200. Se revoca el token de renovación creado para ese ensayo. Las credenciales se leen solo desde un archivo privado local y no forman parte de las evidencias.
- Capturas nativas 19-perfil-roles-reales.png y 20-perfil-texto-200.png; escala original restaurada y sesión QA cerrada. No se cambian datos personales, roles ni registros de negocio. La autenticación local sí utiliza su flujo normal de tokens.

## Repartición y continuidad

María José recibe componentes/modelo de acceso y pruebas Android; Sally, guía y evidencias; José Carlos no necesita cambiar backend en este bloque. Los módulos se separan y comprueban sin commits ni publicación.

Pendiente: comparación de rescates, formularios/estados y panel web; nombres editables de roles en un contrato futuro, composición de mascotas propias dentro del perfil y revisión del material de cabecera. No se declara fidelidad píxel a píxel ni producto comercial terminado. TalkBack y dispositivo físico, firma y validación de rendimiento fuera del equipo siguen pendientes.
