# Evaluación inicial de adopción por etapas

24 de noviembre de 2026. Implementación local del siguiente bloque de la guía 75. No hay commits, cambios en Railway/Northflank ni publicación.

## Recorrido implementado

1. La persona inicia sesión y el perfil anuncia la capacidad `evaluacion_adopcion`. Al solicitar desde la ficha de una mascota se abre el formulario nuevo si el servidor lo admite. Se conserva el acceso anterior para servidores sin esa capacidad; no se envían respuestas estructuradas a un endpoint que las ignore.
2. Cinco etapas: Contacto, Vivienda y hogar, Cuidados, Experiencia, Revisar y enviar. Se reutilizan nombre/correo/teléfono del perfil, editables como contacto de esta solicitud. El borrador solo vive en memoria; no se guarda en almacenamiento del navegador o teléfono.
3. Preguntas condicionales para autorización del propietario, mascotas actuales y experiencia previa. Los campos que dejan de aplicar se eliminan del envío y el servidor también descarta sus valores antiguos.
4. Motivo obligatorio de 10 a 2000 caracteres. Validación local y autoritativa del servidor, campos acotados y autorización de evaluación sin preseleccionar. Revisar/corregir vuelve a exigir las confirmaciones antes de enviar.
5. El botón de envío queda fuera del scroll del resumen. Los errores se muestran en un diálogo legible, sin borrar respuestas. Cancelar pide confirmar descarte si hay cambios; volver de una etapa conserva los datos.
6. Un único POST final crea solicitud, evaluación cifrada y trazabilidad dentro de una transacción. Una respuesta incierta lleva a comprobar Mis solicitudes y no habilita reenvíos automáticos. El bloqueo de la mascota conserva la protección existente contra solicitudes pendientes duplicadas.
7. La persona consulta sus respuestas iniciales en el detalle de su solicitud. El gestor autorizado y asignado las consulta desde el detalle del panel. La decisión administrativa no sobrescribe esa evaluación.

## Contrato y persistencia

- `POST /api/adopcion/solicitudes/evaluacion/`: JSON con `id_mascota` y `evaluacion`. Requiere autenticación y el permiso configurable `adopcion.participar`; no acepta datos de titular, organización ni estado suministrados por el cliente. Rechaza multipart y archivos.
- Los grupos recogen contacto, vivienda/tenencia y seguridad, número y acuerdo de convivientes, disponibilidad/recursos/cuidados/seguimiento, experiencia y motivo. Respuestas como «Necesito orientación» no equivalen a aprobación ni generan un rechazo automático.
- `adoption.0002_evaluacionadopcion` añade una tabla relacionada uno a uno con la solicitud y con la fundación receptora. No convierte ni elimina las solicitudes anteriores.
- El contenido se cifra con Fernet usando la clave existente `LPN_DATA_KEY`. La copia cifrada incluye respuestas y el texto exacto de autorización mostrado. Se conservan versión y fecha de aceptación del servidor; la identidad responsable es la cuenta vinculada a la solicitud.
- No se duplica el formulario privado en observaciones, historial de estados ni auditoría de seguridad. La auditoría conserva actor, operación, recurso y resultado.
- Si el cifrado falla, la transacción no deja una solicitud incompleta. Si una clave se pierde o es incorrecta no se devuelve contenido descifrado ni se usa un fallback en texto plano.

No regenerar `LPN_DATA_KEY` en una instalación con datos: también protege información bancaria previa. El respaldo de la clave requiere el mismo cuidado que el de la base. Una clave temporal de pruebas no debe copiarse a producción.

## Lectura y permisos

- El endpoint de detalle propio conserva la comprobación de titularidad y `adopcion.participar`, con `no-store` también en errores.
- El detalle privado usado por el panel conserva sus comprobaciones de lectura por objeto y asignación. No se concede acceso por conocer el ID ni por pertenecer a otra fundación.
- Django admin permite la consulta técnica de esta evaluación solo al superusuario activo, sin altas, edición o eliminación desde ese editor. El contenido está escapado al renderizar y la consulta técnica se audita. Los metadatos se paginan sin descifrar formularios en la lista.
- No se han cambiado roles de cuentas reales. Los gestores y usuarios de las pruebas son ficticios, en bases locales aisladas.

## Consumo y diseño

- Cambiar de etapa, corregir y marcar opciones no realiza consultas al servidor. No se agrega sondeo, SDK, rastreo, servicio externo ni dependencia nueva.
- Una fila cifrada adicional por solicitud; no se añaden fotografías o documentos a la base. Los listados de solicitudes no descifran ni incluyen toda la evaluación; la lectura se hace al abrir un detalle autorizado.
- Los límites por campo acotan el cuerpo; las nuevas preguntas no permiten JSON arbitrario. La pantalla usa componentes y fuentes existentes.
- Etiquetas persistentes, resumen agrupado, controles con estados, footer accesible, iconos y mensajes concretos: vídeos 1, 2, 5, 9, 10, 12, 13, 14, 16 y 17 de la guía de referencias. No se introducen animaciones que retrasen el envío.
- La barra de progreso refleja etapas reales. El texto ampliado al 200 % se prueba también en el recorrido completo, no solo al abrir el formulario.

## Trazabilidad de la implementación

| Necesidad | Implementación | Evidencia |
|---|---|---|
| S01, S03, S11: respuestas tipadas y persistencia | `adoption/questionnaire.py`, modelo y migración 0002; API dedicada | Validación, cifrado y rollback en MySQL aislado |
| S02, S06, S07, S09: cinco etapas y condicionales | `questionnaire_screen.dart`, capacidad del perfil y entrada desde ficha | Widget tests de recorrido y snapshots de cinco etapas |
| S10: salida, errores y respuesta incierta | Borrador en memoria, diálogo de descarte/error y verificación de solicitudes | Cancelar no envía; respuesta tardía tras cerrar sesión no afecta la nueva sesión |
| S13: evaluación visible para quien corresponde | Detalle propio, detalle privado del panel y consulta técnica en admin | Titular, gestor asignado, cuenta ajena, revocación y consulta técnica |
| Integración | Cliente Flutter real → HTTP loopback → Django → MySQL → asignación → resolución → lectura propia | `http-cliente.txt` y `http-real.json` en la carpeta de evidencias |

Carpeta de evidencias del workspace principal: `output/correcciones-app-2026-11-24/evaluacion-adopcion`. Las capturas son renderizados Flutter con datos ficticios, no capturas de un teléfono físico. La muestra HTTP local no certifica latencia ni capacidad de producción; su entorno de pruebas usa configuración distinta de producción.

## Pendientes explícitos

- Adjuntos de identidad/recibo/fotos de vivienda: el momento y necesidad siguen por definir (D02); no se ha añadido un cargador que exponga documentos ni se finge que ya funciona.
- No se recogen edades/identidades de menores ni información de alergias/asma del hogar en este bloque. Esa parte de S05 queda pendiente de justificar necesidad, autorización y protección de datos de terceros antes de incorporarla.
- La autorización específica de evaluación no sustituye términos de uso, condiciones de adopción ni política de privacidad revisados. Por ello S08 y la puerta jurídica de la guía 74 no se dan por terminadas.
- Retención, exportación/eliminación, restauración de respaldos, rotación de claves, revisión jurídica y prueba física Android siguen en la lista de publicación.
- El endpoint anterior de solicitud sigue disponible por compatibilidad y no recoge la evaluación nueva. Debe decidirse su migración/deprecación para impedir recorridos antiguos una vez actualizados todos los clientes y el flujo de creación del panel. No se afirma que todos los caminos de creación exijan ya el cuestionario.

## Integración posterior del equipo

Primero integrar backend y aplicar migraciones, conservando la clave privada existente. Verificar permisos y la capacidad del perfil; después actualizar la app y renovar sesión. El panel y la app no necesitan servicios de pago para este cambio. Los paquetes acumulados deberán regenerarse al cerrar la entrega; no aplicar ZIP antiguos suponiendo que contienen esta implementación.


## Resultado de verificación local

- Backend: 77 pruebas aprobadas y 15 focales finales; comprobación Django y ausencia de migraciones faltantes verificadas.
- Cliente real: 268 aprobadas, 5 opcionales omitidas; 28 focales finales aprobadas. Análisis limpio y compilación APK debug correcta.
- Integración HTTP optativa ejecutada contra MySQL local: respuestas y autorización exacta preservadas tras resolver, sin suplantación de titular. La muestra de tiempos es local, con configuración de pruebas, y no es un compromiso de latencia productiva.
- Demo local Android: 342 pruebas aprobadas, 4 visuales opcionales omitidas, 2 focales finales y análisis limpio. Perfil marcado `demostracion`; advertencia de datos ficticios. Respuestas solo en memoria, sin conexión con organizaciones reales.
- Capturas: `01-contacto.png` a `05-revision.png` y `mosaico-evaluacion.png`, en la carpeta de evidencias indicada. Se corrigió un recorte de etiquetas seleccionadas y el bloque de autorización al ampliar texto al 200 %.

El listado técnico del admin difiere la carga del contenido cifrado y evita el conteo global adicional. Solo se descifra al consultar un detalle autorizado. No se afirma que los controles globales de cuotas, retención o capacidad ya estén cerrados.


Demo web local sincronizada en `sites/little-paws-mobile-demo`: 2 pruebas focales aprobadas, análisis sin observaciones y `flutter build web --release --no-pub --target lib/demo_main.dart` correcto. Salida en `build/web`; no publicada ni copiada a `dist` de alojamiento. El compilador informa una referencia a la familia CupertinoIcons no empaquetada; la compilación finaliza y esta advertencia queda pendiente de revisar en la auditoría global de iconos. No se agrega una dependencia solo para silenciarla.
