# Matriz resumen de accesos — Little Paws Net

Actualizada: 2026-10-26.

Estado: decisiones principales de la etapa 1 confirmadas el 2026-10-26. Resume decisiones de la conversación; no representa permisos ya implementados ni reemplaza la especificación técnica de campos, transiciones y endpoints de la etapa 2. La fuente detallada es [01-definicion-de-accesos.md](01-definicion-de-accesos.md). Los detalles expresamente pendientes no se consideran permisos aprobados.

## Actores, acciones y alcance

| Actor o rol | Recursos y acciones | Alcance y condiciones principales |
| --- | --- | --- |
| Administrador de seguridad | Gestión de seguridad: usuarios, roles, recursos, permisos y asignaciones. Autorizar al primer principal y atender recuperación de acceso. | Plataforma; diferente del superusuario técnico de Django. El cargo no abre automáticamente datos clínicos o soportes de aportes. La granularidad de sus operaciones debe cerrarse en la matriz técnica. |
| Moderador de plataforma | Ocultar contenido con motivo; aprobar republicación después de correcciones; verificar entidades, pedir correcciones y resolver; revisar publicidad; revisar reclamaciones sobre legitimación de mascotas con decisión justificada. | Verificaciones y casos de legitimación solo asignados; la cola mínima y devolución aprobadas corresponden a verificaciones. El caso de legitimación permite revisar motivos y soportes pertinentes, no el historial clínico completo por defecto. Los demás procesos conservan su ámbito; no obtiene gestión de roles. |
| Responsable principal | Gestionar integrantes y roles internos permitidos, nombrar/revocar secundarios, iniciar transferencia del cargo; delegar gestión de cuentas receptoras y aprobar cambios preparados por el delegado. | Una entidad propia; único principal activo. Transferencia efectiva cuando el sucesor acepta. No concede por sí solo todos los permisos operativos ni acceso a todo dato privado. |
| Responsable secundario | Gestionar integrantes y roles internos permitidos; nombrar secundarios y revocar a otros secundarios. | Su entidad. No puede revocar al principal ni convertirse en principal mediante un nombramiento ordinario. No hereda la facultad exclusiva del principal de delegar gestión de cuentas receptoras o aprobar sus cambios. |
| Ciudadano registrado | Cuenta básica activa tras registro; gestionar sus registros según cada proceso. | Datos y registros propios; no concede cargos administrativos o de entidad ni verificación profesional. |
| Reportante | Gestión de reporte propio pendiente según reglas base; solicitar corrección de un reporte aceptado. | Tras aceptación, revisa la fundación encargada: aprobación/rechazo con justificación e historial. Corregir no republica contenido oculto por moderación. |
| Solicitante de adopción | Consultar su solicitud, editar respuestas y retirarla mientras esté pendiente. | Solo propia. Sin cambiar mascota, solicitante o decisiones internas. Retirada conserva historial y bloquea aprobación posterior. |
| Dueño legitimado de mascota | Crear nueva ficha propia como declaración; aportar soportes privados no verificados; consultar historial clínico, correcciones y soportes de su mascota. | No reclama fichas existentes por ID, nombre o QR. No edita anotaciones profesionales. La acreditación y los conflictos de legitimación requieren detalle. |
| Veterinario verificado y autorizado | Anotar según las reglas del expediente, revisar soportes del dueño y registrar resultado profesional; corregir anotación propia con enmienda vinculada. | Autorización vigente para la mascota concreta, además de verificación profesional. Conservar originales y autoría; sin editar anotaciones ajenas. |
| Gestor de rescates | Aceptar reportes por su fundación; consultar información operativa y realizar actualizaciones permitidas de casos. | Todos los casos de su propia fundación, sin asignación individual obligatoria. Mantener condiciones de verificación, cobertura, capacidad y transiciones. Sin permisos médicos, financieros o de adopción automáticos. |
| Gestor de adopciones | Revisar y aprobar/rechazar solicitudes. | Solo asignadas y correspondientes a custodia vigente de su fundación. Toma exclusiva desde cola mínima; devolución con motivo, historial y pérdida de acceso. |
| Gestor de aportes | Revisar declaraciones y soportes necesarios; confirmar recepción declarada por la fundación. | Solo revisiones asignadas de su fundación. Cola mínima sin soportes/referencias privadas; toma exclusiva y devolución con motivo. No modifica cuentas receptoras ni ejecuta pagos. |
| Persona delegada para cuentas receptoras | Preparar cambios de los datos de recepción. | Permiso específico delegado por el principal, limitado a su fundación. Requiere aprobación del principal antes de entrar en vigencia. Conservar referencias históricas. No incluye redelegación automática. |
| Gestor de catálogo | Publicar productos y cambios de precio/disponibilidad directamente. | Su tienda, con historial. No cambia precios de pedidos anteriores ni obtiene acceso a datos privados de compradores. |
| Gestor de pedidos | Consultar el detalle privado necesario y realizar actualizaciones autorizadas. | Solo pedidos asignados de su tienda. Toma exclusiva de cola mínima; devolución con motivo si el estado lo permite. No cancela por devolver ni ejecuta cobros. |
| Gestor de fondo | Registrar directamente distribuciones informativas, sin segunda aprobación. | Fondos asignados administrados por su entidad, no cada distribución individual. Principal y secundarios autorizados asignan/retiran los fondos de su entidad. No ejecuta transferencias ni confirma recepción por la fundación beneficiaria. |
| Gestor de publicidad | Preparar y gestionar anuncios y enviarlos a revisión. | Todos los anuncios de su propia entidad. La nueva versión solo se publica tras aprobación del moderador. La anterior sigue visible únicamente si está aprobada, vigente y no oculta. |

## Reglas comunes aprobadas

- El nombre del rol no concede permisos fuera de su entidad, asignación o recurso autorizado.
- Una persona puede acumular roles autorizados; no recibe todos por administrar integrantes.
- En verificaciones, adopciones, aportes y pedidos, tomar trabajo genera una asignación exclusiva; devolverlo con motivo conserva historial y retira el acceso de revisión. Los estados admitidos se especifican por proceso.
- Las decisiones de publicación y de negocio son diferentes: ocultar un reporte no cierra el rescate y corregirlo no aprueba su republicación.
- La transferencia de principal espera aceptación. Casilla inicialmente desmarcada: «Mantener a [nombre] como responsable secundaria/o». Sin marcar, el saliente pierde el cargo de responsable y conserva los demás roles operativos. Salir de la organización es una operación distinta.
- Acceso privado excepcional: autoriza el titular/custodio/responsable competente para el dato; solo consulta de registros seleccionados, sin autoaprobación, máximo 24 horas desde aprobación o menos, sin renovación automática y revocable anticipadamente. Registrar y bloquear consultas posteriores a revocación o vencimiento.

## Base existente que debe conservarse al implementar

Los visitantes tienen los recorridos públicos que ya contemplan los requisitos y la API: catálogo público y mascotas disponibles en adopción; reporte anónimo con clave privada de gestión y sus restricciones. Esto no habilita acceso a expedientes, documentación privada o datos de otros usuarios. No se ha aprobado convertir actividades como donar o adoptar en roles independientes obligatorios.

## Detalles para la especificación técnica de la etapa 2

1. Precisar el procedimiento de revisión de legitimación por un Moderador de plataforma con el caso asignado: soportes pertinentes, comunicación, registro de decisión y aplicación autorizada de sus efectos. No hay bloqueo general automático por reclamar ni acceso clínico completo por recibir el caso.
2. Consolidar acciones precisas, campos, transiciones, permisos administrativos y reglas de revocación en la especificación técnica, sin ampliar accesos por omisión. Los extremos sin política suficiente se mantienen restringidos hasta concretarlos.

### Reglas de cierre aprobadas

- Aprobada expresamente por el usuario: para cambios ordinarios de cuentas receptoras, mantener siempre la separación de personas: el delegado prepara y el principal aprueba. Si el principal desea un cambio, solicita su preparación al delegado; no dispone de un recorrido de autoaprobación. La autorización de gestión de cuentas no se usa para saltar esa separación.
- Aprobada expresamente por el usuario: reclamar una mascota, escanear su QR o crear una ficha parecida no concede acceso a una ficha existente ni permite quitar o bloquear automáticamente el acceso del dueño registrado. Cualquier cambio de titularidad de la ficha o permisos exige revisión autorizada. No se aprueba un bloqueo general automático ante una simple reclamación. El usuario eligió como revisor a un Moderador de plataforma con el caso asignado, limitado a motivos y soportes pertinentes, con decisión justificada e historial y sin acceso clínico completo automático.

Las reglas técnicas de aplicación de decisiones deben precisarse al contrastar esta política con los requisitos y modelos existentes; registrar una disputa no asigna acceso automáticamente a un nuevo actor. Los límites que sigan sin definirse no se convierten en permisos concedidos.

Las tareas de modelos, migraciones, endpoints, pruebas y auditoría corresponden a la etapa 2. El acceso web corresponde a la etapa 3 y el boceto de Figma a la etapa 4 acordada. Esta matriz no declara terminadas esas etapas.
