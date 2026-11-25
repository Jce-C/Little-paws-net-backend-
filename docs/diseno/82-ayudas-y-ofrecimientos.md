# O05 — Ayudas y ofrecimientos

Fecha: 24 de noviembre de 2026. Trabajo local. Sin cambios del esquema ni migraciones nuevas en este bloque.

## Recorrido y presentación

Las tres modalidades conservan destinos distintos y explicaciones breves: aporte monetario (compromiso, sin cobro), tiempo/voluntariado (actividad y acuerdo de participación) y ayuda en especie (insumos según necesidades). Se distinguen mediante icono, texto y tono de la paleta; el color no es el único indicador.

Un componente compartido `HelpOfferCard` presenta los intereses del titular y los recibidos por la organización con la misma jerarquía: persona u organización, modalidad, actividad si existe, mensaje y fecha localizada. No se inventa aceptación, reserva, pago o entrega. Los mensajes largos conservan todo su contenido; las listas usan desplazamiento de página sin un scroll interior por tarjeta.

La configuración de necesidades y recepción de voluntarios queda agrupada en un bloque de formulario. Cancelar y Guardar permanecen en el pie, con adaptación por Wrap. Actividades/canales tienen campos compactos, etiquetas más breves y límites conservados. La publicación sigue exigiendo autorización explícita sin preselección.

## Fallos corregidos

- El editor de convocatoria no ofrecía recuperación en la misma pantalla después de un conflicto de versión. Ahora puede consultar el servidor, confirma antes de reemplazar el borrador y reconstruye los controladores sin duplicar entradas.
- Un conflicto 409 al editar necesidades no bloqueaba los siguientes intentos con la misma versión antigua. Ahora se exige volver a consultar antes de guardar otra vez.
- Las pantallas privadas de gestión y ofrecimientos usaban únicamente el correo como identidad de estado. Ahora incluyen `identityRevision`, de modo que volver a autenticar la misma cuenta también elimina el borrador anterior. Editar el perfil conserva la sesión y el borrador.
- La lista de organizaciones no tenía reintento tras un fallo inicial; ahora permite volver a consultar.
- El compromiso monetario carecía de Cancelar persistente y de confirmación antes de perder el monto. Ahora ambos están disponibles; se bloquea la salida durante el envío y se explica un resultado incierto sin prometer que salir deshace el registro.
- El error del editor público podía alargar demasiado el pie. Se muestra en diálogo desplazable, dejando en el pie las acciones breves de cancelación, consulta y guardado.

## Trazabilidad y permisos

| Recorrido | Ruta/componente | Garantía comprobada |
|---|---|---|
| Modalidades y consulta | `HelpScreen`, `PublicListScreen`, `/api/red/organizaciones/`, `/api/fondos/` | Navegación explícita, sin sondeo ni consultas al abrir el selector de modalidades |
| Actividad → interés | `HelpProgramInfo`, `PublicMessageScreen`, `POST /api/ayudas/intereses/` | `ayudas.participar`; organización verificada y actividad vigente; titular derivado de sesión |
| Mis ofrecimientos | `PublicListScreen(kind: offers)`, `HelpOfferCard`, `GET /api/ayudas/intereses/` | Datos propios; actividad y fecha conservadas; nueva sesión reconstruye la vista |
| Gestión de organización | `help_management.dart`, `/api/ayudas/organizaciones/{id}/` | `ayudas.gestionar` en esa entidad; versión para impedir sobrescrituras y actualización explícita de recibidos |
| Publicar/retirar | `help_program.dart`, `/api/ayudas/organizaciones/{id}/programa/` | Permiso contextual, consentimiento, versión, organización verificada y auditoría |
| Aporte monetario | `ContributionScreen`, `POST /api/fondos/donaciones/` | `fondo.participar`; monto válido, estado Comprometida, `dinero_recibido=false` |

El cierre de recepción de voluntarios oculta actividades y rechaza nuevos envíos; conserva los canales publicados. Retirar la convocatoria oculta actividades y canales públicos sin borrar el borrador. Los contactos privados y ofrecimientos no se añaden a la respuesta pública.

## Validación

Evidencias del workspace: `output/correcciones-app-2026-11-24/ayudas-ofrecimientos`.

- Backend MySQL aislado: **162 pruebas aprobadas**, incluyendo cuentas, animales, adopción, comunidad/ayudas, programas públicos y RBAC dinámico/roles abiertos. No hubo cambios de lógica backend en este bloque.
- Cliente canónico: **297 pruebas aprobadas y nueve optativas omitidas**; cuatro nuevas comprueban recuperación de conflicto y versión, actualización de recibidos, separación por sesión y acciones a 320×640 con texto al 200 %. Focales finales: **26 aprobadas**, incluyendo sesión, envíos y fallos de los compromisos monetarios.
- Demo local: **371 aprobadas y cuatro capturas optativas omitidas**; cinco archivos compartidos sincronizados sin sustituir los servidores de datos ficticios. Demo web: **26 focales aprobadas**.
- Análisis final sin observaciones en cliente, demo y web. APK debug compilado. Compilación web release correcta (`web-build.txt`); persiste la advertencia previa de CupertinoIcons no empaquetada, pendiente de la auditoría global de iconos. No se sustituye el directorio de alojamiento.
- `http-cliente.txt` y `http-real.json`: Flutter real → HTTP loopback → Django → MySQL. Publicación y lectura anónima, conflicto 409, envío/repetición con mismo ID, lectura del titular y gestor, denegación ajena/anónima, cierre de voluntariado y retirada de publicación. Registro de compromiso sin pago.
- `persistencia-real.json`: una fila del interés por modalidad, actividad/mensaje correctos, una entrada de auditoría por creación, borrador conservado tras retirada y compromiso de 10000 COP del mismo titular en estado Comprometida.
- Capturas y mosaico son renderizados Flutter con fixtures en español, no capturas de un emulador ni de producción. Se revisó la composición de convocatoria, gestión y ofrecimientos. La prueba de texto ampliado acredita el recorrido indicado; no toda la accesibilidad del producto.

Solo se usaron bases locales aisladas, cuentas ficticias y un dominio `.invalid` para el canal de ejemplo. El servidor HTTP QA quedó detenido.

## Límites y siguientes pasos

Un interés no es un proceso de aceptación/entrega: no se añade un estado ficticio ni un botón sin operación backend. El contrato actual admite un interés por persona, organización y modalidad; repetir exactamente el mismo devuelve el registro y cambiarlo devuelve conflicto. El listado propio está limitado a cien y los recibidos a cincuenta; no se presentan como totales globales. La paginación de esos listados queda para la revisión de escala, si se supera ese volumen.

Los aportes a fondos son compromisos informativos. El cliente bloquea reenvíos tras un resultado incierto e indica consultar con la organización; este endpoint no incorpora recuperación idempotente como el de mascota personal. Los canales son declarados por la organización: no se presentan como verificados ni se solicita dinero para probarlos.

Se cierra **O05: 34/57 unidades (59,6 %)** de la guía 75. Siguiente: **O06, recorrido de rutas restantes** y después Q01-Q10. Se mantienen las puertas de publicación de las guías 72-74: seguridad final, privacidad/retención/derechos, licencias, revisión jurídica, respaldo/restauración, firma Android y dispositivo real, paquetes para tres integrantes y presupuesto gratuito/VPS. No se certifica todavía producto listo para publicar, integración productiva o latencia real.

Sin commits, ramas, push, despliegue ni servicios de pago.
