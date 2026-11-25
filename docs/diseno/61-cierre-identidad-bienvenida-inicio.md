# 61 · Cierre de implementación de identidad, marca, bienvenida e Inicio

22 de noviembre de 2026. Esta guía sustituye el estado de los puntos1–4 en las auditorías anteriores. El cierre se refiere a la implementación y evidencia de los requisitos concretos; la aceptación integral, dispositivo físico, TalkBack y entorno real permanecen en el punto14.

## Qué se cierra

| Punto | Implementación concreta | Evidencia |
|---|---|---|
| 1 · Identidad | Se conservan FCF0D3/FFF9EC, Inter y acentos del proyecto. Se unifican materiales de formularios, tarjetas, diálogos y controles. Los diálogos pasan a marfil, switches salvia y la preferencia sólida retira sombras/capas ambientales. Contraste alto refuerza bordes. Vidrio acotado a navegación; lectura sin blur. | Tema y componentes compartidos; prueba de superficies sólidas; contraste de19 combinaciones planas; suite completa. |
| 2 · Logotipo | La variante vectorial de hocico orgánico se aplica como perro completo en bienvenida, acceso, cabecera interna y botón central. El original queda conservado como asset; la variante deja de ser solo un estudio. | Asset brand-organic.svg registrado, compilación y capturas reales. |
| 3 · Bienvenida | Texto explícito de encontrar/solicitar adopción, fundaciones/veterinarias, aportes/ayuda y comunidad. Acceso a login/registro en una acción, jerarquía diferenciada y composición adaptable. No se promete procesar pagos. | Pruebas de ventanas bajas, texto ampliado, movimiento reducido y flujo de acceso. |
| 4 · Inicio | La ilustración deja de pertenecer a un widget de cabecera dentro de la lista. HomeBackdrop la pinta detrás de la página y de forma independiente del desplazamiento. Espacio de protagonismo visual sin controles superpuestos; lectura protegida con degradado, seis destinos reales y tarjetas por capas. | Prueba de geometría/fondo fijo al desplazar; acceso autenticado llega a Inicio; captura real de la demo. |

No se cambia la lógica de negocio ni los permisos. No se modifica el Figma editable manual. No se sustituye la app por una maqueta. El asset de marca nuevo es vectorial, no una imagen generada por IA.

## Materiales y accesibilidad

- `LpnMaterials.solid` centraliza contraste alto/reducción de transparencias.
- FormCard y FormSection mantienen la misma familia de superficie, bordes y alternativa sin sombras. FeatureDeck conserva el centrado de flechas de60.
- Fondo ambiental de Inicio omitido en modo sólido. La imagen principal se conserva sin incorporar controles dentro de ella.
- La tipografía principal sigue siendo Inter; la tipografía script permanece limitada a titulares decorativos existentes. El QR conserva fondo blanco por legibilidad, no se tiñe para simular vidrio.
- Las animaciones siguen siendo finitas, con movimiento reducido. No hay filtros de desenfoque por cada tarjeta ni nuevas consultas de datos en Inicio/login.

## Pruebas y alcance

208 pruebas del cliente canónico y210 de la demo. Los registros finales de análisis, pruebas, compilación, publicación y capturas están en `output/cierre-puntos-1-4-2026-11-22/validacion.json`.

Tres regresiones nuevas comprueban: imagen fuera del encabezado de la lista y posición estable al desplazar; preferencias de materiales en modo normal y sólido. Las pruebas anteriores mantienen rutas, borradores por identidad, accesos, límites de red, geometría de navegación y compatibilidad de datos.

La suite no certifica WCAG completa ni operaciones contra Railway. No se ha realizado publicación en Railway, integración Git oficial ni migración de producción. La demo Sites se publica por separado con datos ficticios, preservando su audiencia existente y sus adaptadores de fotografías.

## Seguimiento de los14 puntos

Se utiliza un criterio estable: **un punto cerrado aporta1/14; un parcial no aporta un punto completo**. El porcentaje indica cierre técnico de esta tabla. No se pondera por cantidad de archivos, pruebas o tiempo invertido.

Con este bloque quedan cerrados en implementación **1,2,3,4,10,11,12 y13: 8/14 = 57,1 %**.

| Pendiente | Falta para cerrar |
|---|---|
| 5 · Adopciones | Descripción y cuidados editoriales individualizados, con publicación autorizada, presentación y pruebas. |
| 6 · Ayudas | Actividades estructuradas y canales oficiales administrables; separación clara de participación/gestión. |
| 7 · Directorio | Publicación autorizada de logos, retirada y visualización. Los textos/contactos/servicios ya se implementaron localmente en60. |
| 8 · Comunidad | Fotografía de perfil autorizada, retirada y fallback; integrar en publicaciones/comentarios. |
| 9 · Tienda | Completar composición de referencia y validar fotografías autorizadas en catálogo/detalle. El contrato de fotos existe en59. |
| 14 · Validación integral | Recorridos completos con datos consentidos, entorno real, dispositivo físico/TalkBack, aceptación visual y preparación de distribución. |

Los puntos pueden reabrirse si una comprobación posterior demuestra un defecto. Los logs y capturas permiten identificar qué versión fue revisada. El siguiente bloque funcional es5.

## Reparto

Majo: cliente y pruebas. Sally: materiales, marca, bienvenida, composición y evidencia. José Carlos: integración posterior y contratos pendientes, sin nuevas migraciones en este bloque visual. Se actualizan los tres paquetes de trabajo sin crear commits o ramas del repositorio oficial.
