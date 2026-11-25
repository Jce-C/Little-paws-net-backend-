# Onda, Inicio integrado y superficies · 21 noviembre 2026

Continúa la auditoría57 con cambios reales de interfaz. No declara cerrados los contratos públicos ni la aceptación visual completa del producto.

## Implementado

- Acceso con cabecera de papel a ancho completo y onda Bézier continua sobre salvia; no un rectángulo redondeado. Login y registro agrupan los campos en una superficie de lectura separada. Cambiar entre ambos retira el foco y vuelve arriba; la marca permanece visible. El registro sigue usando la API real en el cliente y su limitación explícita en la demo.
- La validación comienza al intentar enviar. Después se actualiza al corregir el campo, sin consultas al escribir. Se conserva contraseña mínima, autofill, mostrar/ocultar y bloqueo durante envío.
- Inicio utiliza una imagen de fondo a ancho completo con desvanecimiento hacia el lienzo. El texto queda después del límite de la imagen, no superpuesto. Desde bienvenida, un acceso correcto lleva a Inicio; explorar sin sesión sigue abriendo adopciones.
- Tarjetas de Inicio con capas, veladura clara, borde luminoso y sombra cálida acotada. No se desenfoca cada tarjeta: el vidrio real sigue limitado a navegación. Los textos mantienen fondos de lectura y se respeta la alternativa sólida. Entrada escalonada finita460ms; movimiento reducido elimina la animación. No hay temporizadores que bloqueen los controles.
- Catálogo con metadatos alineados al inicio, en vez de centrar todas las líneas; se conservan medidas para texto ampliado y fotos autorizadas.
- Compositor con dos grupos visuales: identidad/contexto y temas/redacción. Sugerir un tema no envía ni sustituye un borrador existente. Aviso y envío continúan visibles en la zona inferior segura.
- Aportes con grupo independiente para montos y campo, presets legibles en COP que solo rellenan. Nunca se confirman pagos ni entregas.
- Perfil prioriza identidad y mascotas propias. Los roles de solo lectura aparecen después, sin alterar permisos o la protección por sesión. Cerrar sesión sigue disponible.
- La demo conserva su adaptador de fotos ficticias. El detalle ahora usa edad/tamaño/sexo de su propia ficha de ejemplo, evitando contradicciones con la tarjeta.
- Se incorporan a la demo las correcciones locales de57: voluntariado solo para aceptación explícita, nomenclatura de vacíos y contraste del texto sobre rosa.

## Verificación y alcance

197 pruebas canónicas,203 de la demo, análisis sin incidencias. Tres regresiones nuevas comprueban llegada a Inicio sin consultar catálogo, validación sin consultas y cambio a registro a320px con onda a ancho completo, posición inicial y marca visible. La suite conserva controles de permisos, borradores, respuestas tardías, paginación, galería y texto ampliado. Compilaciones web y Android debug; candidato real apunta a API local10.0.2.2:8016 y no se instala. Solo se instala net.littlepaws.little_paws_net.visualdemo en el emulador; sus datos son ficticios. Capturas nuevas en output/cierre-visual-2026-11-21/pantallas. La publicación y hashes definitivos están en validacion.json.

## Lo que sigue pendiente

- Fotos públicas de productos: falta publicación/retirada y contrato de imagen seguro, aunque exista ProductoImagen. El aviso sin fotografía no se presenta como una foto implementada.
- Logos, contactos y servicios públicos de organizaciones: faltan datos/contratos y una ficha completa; no se publican contactos privados por inferencia.
- Descripción editorial y cuidados particulares de cada mascota: el contrato público no los ofrece; no se extrae información del expediente privado.
- Actividades estructuradas de voluntariado y canales oficiales de aportes. Los compromisos no son dinero recibido.
- Galería visual con varias fotos reales autorizadas por animal en el piloto; la demo tiene una por ficha y la prueba de widget verifica varias.
- Recuperación de contraseña móvil, estados de carga más progresivos, dispositivo físico/TalkBack y aceptación visual de todos los estados. Las pruebas mock no certifican Railway.

La variante de hocico se presenta junto a la marca actual en comparacion-marca.svg para revisión; no se cambia silenciosamente el logo de la app. Las referencias se adaptan a la paleta y al negocio, no se añaden funciones ficticias de hotel/notas/pago.

## Reparto

Majo: cliente, componentes, navegación y pruebas. Sally: guía, estilo, comparación de marca y evidencia visual. José Carlos: contratos públicos pendientes; no hay cambios nuevos de backend en este bloque. Paquetes locales actualizados; sin commits/ramas oficiales, cambios Railway o sobrescritura del Figma manual.
