# Etapa 2 — Plan técnico de autorización Django

Fecha: 2026-10-26.
Estado: base funcional de la etapa implementada en Django y preparada para conectar la etapa 3. Consultar [cierre de la etapa 2](06-cierre-etapa-2.md) para el alcance y la validación actuales. Este documento conserva el plan de referencia.

Fuentes: [decisiones detalladas](01-definicion-de-accesos.md) y [matriz resumen](02-matriz-resumen.md). La implementación debe respetar esas decisiones, sin convertir detalles pendientes en derechos nuevos.

## 1. Inventario y compatibilidad

- Revisar modelos, migraciones, endpoints y servicios existentes, incluidas las comprobaciones que hoy consultan RolPermiso y EntidadMiembroRol.
- Conservar el usuario personalizado, MySQL, las restricciones de negocio y la separación del superusuario técnico respecto de roles de negocio.
- Trabajar sobre los cambios existentes del usuario sin descartar ni incorporar indiscriminadamente archivos ajenos a la tarea.
- No reactivar cuentas de demostración deshabilitadas ni publicar credenciales para poner en marcha el panel.

## 2. Catálogo explícito de recursos y acciones

- Añadir mediante migraciones nuevas el recurso protegido y su relación con permisos. Reutilizar Rol, Permiso y sus asignaciones cuando sean compatibles.
- Mantener acciones del negocio además de CRUD: aceptar caso, resolver adopción, tomar/devolver revisión, confirmar recepción, proponer/aprobar cambio de cuenta, emitir enmienda, etc.
- Separar los roles globales y operativos acordados. No convertir automáticamente usuarios de ADMIN_PLATAFORMA en todos los nuevos roles.
- Definir códigos estables y compatibilidad de los códigos existentes antes de migrar asignaciones.
- Registrar un recurso desde el panel no implementa automáticamente su módulo: solo deben concederse operaciones efectivamente soportadas y protegidas.

## 3. Asignaciones, jerarquía y evaluación de acceso

- Modelar responsables principal/secundarios por entidad y sus transferencias con aceptación, incluyendo la casilla de conservación del cargo secundario.
- Modelar las asignaciones de solicitudes/casos/fondos según su unidad de alcance. Respetar que el Gestor de rescates accede a todos los casos de su fundación, mientras otros recorridos requieren asignación individual.
- Unificar la evaluación de autorización: cuenta activa, rol vigente, permiso, entidad, membresía, titularidad, asignación y condiciones del objeto.
- Aplicarla tanto a listados como a detalle, archivos, acciones y servicios. IsAuthenticated o esconder un botón no sustituyen estos controles.
- No introducir un bypass general de negocio por is_staff o is_superuser.
- Precisar en esta fase los campos, transiciones y operaciones administrativas; si una decisión de negocio nueva es imprescindible, presentarla puntualmente al usuario.

## 4. Operaciones y trazabilidad

- Operaciones transaccionales para tomar/devolver trabajo, resolver/retirar solicitudes, transferir principal y aprobar cambios de cuentas. Mantener un orden de bloqueo coherente con los servicios existentes.
- Conservar historial de asignaciones, decisiones, correcciones, versiones de publicidad y enmiendas clínicas; no sobrescribir originales o precios históricos.
- Acceso excepcional: solicitante, autoridad aprobadora sobre el recurso, motivo, registros concretos, inicio, expiración de máximo 24 horas y revocación. Solo consulta, sin autoaprobación ni renovación automática.
- Aplicar la autorización a cada consulta y descarga privada; no exponer URLs públicas permanentes. Separar documentos de verificación, soportes de aportes y expediente clínico.
- Para legitimación de mascota, el moderador asignado revisa los soportes pertinentes y registra decisión. No hay acceso ni bloqueo automático por reclamar. Definir efectos autorizados antes de habilitarlos.
- Mantener separados el registro de distribuciones, la confirmación de recepción y los pagos externos.

## 5. API para el panel

Diseño de referencia para la etapa completa; consultar el informe del bloque 1 para las rutas ya creadas:

- Identidad y permisos efectivos del usuario, incluyendo sus entidades y contexto seleccionado.
- Gestión de usuarios, recursos, roles y sus permisos.
- Membresías, responsabilidades y asignaciones dentro de los límites acordados.
- Acciones explícitas para tomar, devolver, solicitar revisión, resolver, transferir y revocar; no un endpoint genérico que permita cambiar cualquier estado o campo.
- Respuestas de error consistentes y filtros que no revelen información privada de otras entidades.

El login web y captcha corresponden a la etapa 3. Al prepararlos, diferenciar sesiones web con protección CSRF de JWT para la aplicación móvil y evitar usar la sesión técnica de Django Admin como autorización de negocio.

## 6. Pruebas de aceptación necesarias

1. Una cuenta sin permiso no obtiene la operación mediante una petición directa.
2. Una membresía o rol revocado deja de autorizar operaciones.
3. Un rol de una entidad no permite leer ni modificar registros de otra.
4. Un gestor sin asignación no abre detalle ni archivos privados del trabajo de otra persona.
5. Dos tomas simultáneas no generan dos revisores activos; devolver trabajo conserva historial y retira acceso.
6. Aprobación/retirada/devolución concurrentes no producen estados incompatibles.
7. El principal no puede desaparecer por una baja ordinaria sin reemplazo; la transferencia solo se completa al aceptar y respeta la casilla del saliente.
8. Los cambios de cuenta no entran en vigor antes de aprobación por una persona diferente a quien los preparó.
9. La edición clínica produce enmienda, no sobrescritura del original.
10. El acceso excepcional es específico, de solo consulta y no funciona tras revocación o vencimiento.
11. Una reclamación o QR no revela el expediente ni bloquea automáticamente al dueño; el revisor no recibe el historial clínico completo por su asignación.
12. No se publican anuncios nuevos o modificados sin aprobación y no se mantienen visibles versiones vencidas u ocultas.

Realizar estas comprobaciones sobre una base de pruebas aislada y compatible con MySQL y las migraciones existentes, no sobre los datos del usuario. Informar el alcance real de pruebas ejecutadas.

## 7. Entrega explicada

Al terminar cada bloque funcional, explicar qué cambió, dónde, cómo se guarda y cómo se comprueba. Documentar comandos de instalación/migración y resultados reales, distinguiendo implementado, probado y pendiente. La etapa 3 conectará el acceso web; la etapa 4 elaborará el boceto del panel en Figma según lo acordado.
