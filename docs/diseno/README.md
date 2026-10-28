# Boceto editable del panel Little Paws Net

Entrega: 26 de octubre de 2026.

Refinamiento del 27 de octubre: crema, salvia y arcilla aplicados al panel, con encabezados de tabla, filas alternadas, botones y navegación coherentes. La [guía de estados y colores](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=104-6) está en la página 00; las capturas actualizadas están en `output/estilo-salvia/`. Las reglas implementables se mantienen en [STYLE.md](../../STYLE.md).

[Abrir el índice del Figma](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=16-2). Archivo actualizado: **Little Paws Net · Panel de gestión · Boceto completo**. El archivo original de diseño móvil no se modificó.

Hay **118 pantallas y estados**, incluidas **55 ventanas**, **13 vistas de inicio por perfil**, **4 adaptaciones móviles** y **4 estados nuevos del acceso**. Se usan capas nativas editables para textos, formularios y componentes; las ilustraciones combinan vectores e imágenes. Las capturas del estilo actualizado están en `output/estilo-editorial/`; las de `output/panel-admin-etapa-3/` conservan el boceto anterior.

## Cómo recorrerlo

1. Abrir el índice de Figma. Sus tarjetas enlazan con la vista inicial de cada perfil.
2. Revisar las páginas en el orden 01 a 08; cada marco tiene un código estable, por ejemplo C12.
3. Usar la matriz B04/B17 para discutir acciones y alcance antes de refinar los formularios.
4. Para cada ventana, comprobar el actor, la entidad, el registro, la confirmación y el resultado esperado contra `docs/rbac/01-definicion-de-accesos.md` y la API existente.

El índice y algunos enlaces sirven para recorrer el diseño. **No es un prototipo completo con todos los botones conectados**, ni guarda cambios, autentica personas o demuestra permisos reales. Esas comprobaciones pertenecen a Django.

## Perfiles representados

- Administrador de seguridad
- Responsable principal
- Responsable secundario
- Preparador delegado de cuentas
- Moderador de plataforma
- Gestor de rescates
- Gestor de adopciones
- Gestor de aportes
- Gestor de catálogo
- Gestor de pedidos
- Gestor de fondo
- Gestor de publicidad
- Veterinario autorizado

El preparador de cuentas es una delegación restringida, no un rol general adicional. El ciudadano usa los recorridos públicos de la aplicación; no recibe acceso administrativo por registrarse. Estas cuatro vistas móviles adaptan el panel del equipo autorizado; el diseño completo de la aplicación de adopción para ciudadanos conserva su alcance separado.

## Decisiones reflejadas

- Separación visible entre seguridad global, organización y operación. Ser administrador técnico no otorga acceso clínico ni acceso de negocio ilimitado.
- Selector de organización y mensajes de alcance; las tablas muestran ejemplos ficticios, nunca registros de la base local.
- Transferencia del principal pendiente de aceptación. C12 ofrece la casilla desmarcada «Mantener a Ana como responsable secundaria»; Ana conserva el cargo principal hasta la aceptación de Carlos.
- Preparación y aprobación de cuentas receptoras en pasos separados; la delegación no permite aprobar su propia propuesta.
- Colas y trabajo asignado para revisiones; devolución de tareas con motivo.
- Reclamación en dos pasos: decisión documentada (D09) y ejecución expresa del cambio de titularidad con nueva comprobación (D10).
- Expediente con autorización vigente, enmienda que conserva el original y acceso excepcional separado.
- Solicitud de adopción como ventana sobre la lista (E13). En móvil se usa un detalle que aprovecha el ancho disponible (G03).
- Navegación móvil con iconos acompañados de texto, para conservar claridad.
- Estados de error, sesión vencida, bloqueo temporal, acceso pendiente y permiso insuficiente.

## Fundamentos visuales

Se aplicó la referencia editorial cálida de Refero, conservando el logo original y los tonos marrón, crema, arena y salvia de Little Paws. Inter sustituye a Manrope para lectura y titulares; Leckerli One queda para la marca y bienvenida. Se mantienen componentes reutilizados, variables, estados y ventanas con contexto translúcido.

Los fundamentos de TypeUI guían jerarquía, espaciado, accesibilidad y formularios. La guía implementable está en [STYLE.md](../../STYLE.md); los valores reales están en `backend-panel/seguridad/static/seguridad/tokens.css`.

La revisión de límites encontró cero textos fuera de sus marcos en las 118 vistas. Se inspeccionaron capturas de matrices, transferencias, escritorio, móvil y el nuevo acceso. Esta revisión no equivale a una certificación de accesibilidad.

La [demo del panel](http://127.0.0.1:8094/) muestra 33 vistas con 13 perfiles ficticios y tres estados de acceso. La [demo del scroll](http://127.0.0.1:8092/) muestra la secuencia real de bienvenida. En Figma, L01–L04 son estados editables de referencia; no una animación de scroll programada.

## Qué está implementado

La [etapa 3](../rbac/07-etapa-3-acceso-web.md) implementa login, sesión, captcha, límites, CSRF, navegación autorizada y tablas/formularios iniciales del panel. **Las 118 vistas de este boceto no son 118 formularios web ya programados**. Los formularios completos de transferencias, aprobaciones, documentos y recorridos operativos deberán conectarse y probarse al implementar el diseño aprobado; sus reglas y API de etapa 2 ya existen.

## Inventario de marcos

La versión estructurada está en [panel-admin-inventario.json](panel-admin-inventario.json).

### 01 · Acceso y estados

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [A01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-2) | Login | Acceso |
| [A02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-3) | Datos o suma incorrectos | Acceso |
| [A03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-4) | Validando acceso | Acceso |
| [A04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-5) | Demasiados intentos | state |
| [A05](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-6) | Autorización pendiente | state |
| [A06](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-7) | Tu sesión terminó | state |
| [A07](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-8) | Sin permiso para este módulo | state |
| [A08](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=5-9) | No pudimos cargar la información | state |

### 02 · Administración

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [B01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-2) | Hola, Ana. | Inicio |
| [B02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-3) | Usuarios | Listado |
| [B03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-4) | Roles y permisos | Listado |
| [B04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-5) | Permisos · Administrador de seguridad | Matriz |
| [B05](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-6) | Recursos | Listado |
| [B06](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-7) | Permisos | Listado |
| [B07](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-8) | Organizaciones y principales | Listado |
| [B08](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-9) | Auditoría | Listado |
| [B09](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-10) | Crear usuario | Ventana |
| [B10](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-11) | Editar usuario | Ventana |
| [B11](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-12) | Desactivar cuenta | Ventana |
| [B12](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-13) | Asignar un rol global | Ventana |
| [B13](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-14) | Crear rol | Ventana |
| [B14](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-15) | Registrar recurso | Ventana |
| [B15](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-16) | Designar primer principal | Ventana |
| [B16](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=8-17) | Recuperar responsabilidad principal | Ventana |
| [B17](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=18-394) | Permisos · Gestor de adopciones | Matriz |

### 03 · Organización

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [C01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-2) | Hola, Ana. | Inicio |
| [C02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-3) | Hola, Carlos. | Inicio |
| [C03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-4) | Equipo y responsables | Listado |
| [C04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-5) | Roles de mi entidad | Listado |
| [C05](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-6) | Transferencias | Listado |
| [C06](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-7) | Cuentas receptoras | Listado |
| [C07](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-8) | Hola, Elena. | Inicio |
| [C08](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-9) | Incorporar integrante | Ventana |
| [C09](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-10) | Gestionar roles del integrante | Ventana |
| [C10](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-11) | Nombrar responsable secundario | Ventana |
| [C11](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-12) | Retirar integrante | Ventana |
| [C12](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-13) | Transferir responsabilidad principal | Ventana |
| [C13](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-14) | Aceptar responsabilidad principal | Ventana |
| [C14](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-15) | Delegar preparación de cuentas | Ventana |
| [C15](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-16) | Preparar cambio de cuenta | Ventana |
| [C16](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-17) | Revisar propuesta de cuenta | Ventana |
| [C17](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-18) | Rechazar propuesta de cuenta | Ventana |
| [C18](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-346) | Cancelar transferencia pendiente | Ventana |
| [C19](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-347) | Revocar preparación de cuentas | Ventana |
| [C20](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=15-393) | Mis propuestas de cuenta | Listado |
| [C21](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=15-394) | Equipo y responsables | Listado |
| [C22](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=15-395) | Roles de mi entidad | Listado |
| [C23](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=15-396) | Transferencias | Listado |
| [C24](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=17-453) | Verificación de mi entidad | Listado |
| [C25](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=17-454) | Adjuntar documentos y reenviar | Ventana |

### 04 · Moderación

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [D01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1752) | Hola, Laura. | Inicio |
| [D02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1753) | Verificaciones | Listado |
| [D03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1754) | Verificación asignada | Listado |
| [D04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1755) | Pedir correcciones | Ventana |
| [D05](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1756) | Aprobar verificación | Ventana |
| [D06](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1757) | Devolver revisión a la cola | Ventana |
| [D07](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1758) | Reclamaciones | Listado |
| [D08](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1759) | Reclamación asignada | Listado |
| [D09](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1760) | Registrar decisión de reclamación | Ventana |
| [D10](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1761) | Ejecutar cambio de titularidad | Ventana |
| [D11](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1762) | Revisión de anuncios | Listado |
| [D12](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1763) | Revisar versión de anuncio | Ventana |
| [D13](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1764) | Contenido público | Listado |
| [D14](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1765) | Ocultar contenido público | Ventana |
| [D15](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=12-1766) | Aprobar republicación | Ventana |
| [D16](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-890) | Rechazar verificación | Ventana |

### 05 · Operación

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [E01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-998) | Hola, Miguel. | Inicio |
| [E02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-999) | Hola, Elena. | Inicio |
| [E03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1000) | Hola, Sofía. | Inicio |
| [E04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1001) | Hola, Pablo. | Inicio |
| [E05](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1002) | Hola, Marta. | Inicio |
| [E06](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1003) | Hola, Andrés. | Inicio |
| [E07](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1004) | Hola, Valeria. | Inicio |
| [E08](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1005) | Casos de rescate | Listado |
| [E09](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1006) | Detalle del rescate | Listado |
| [E10](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1007) | Aceptar reporte de rescate | Ventana |
| [E11](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1008) | Cerrar o cancelar caso | Ventana |
| [E12](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1009) | Adopciones | Listado |
| [E13](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1010) | Solicitud de adopción #041 | Ventana |
| [E14](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1011) | Resolver solicitud de adopción | Ventana |
| [E15](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1012) | Devolver solicitud de adopción | Ventana |
| [E16](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1013) | Aportes | Listado |
| [E17](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1014) | Revisar aporte #081 | Ventana |
| [E18](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1015) | Confirmar recepción de aporte | Ventana |
| [E19](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1016) | Catálogo | Listado |
| [E20](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1017) | Crear o editar producto | Ventana |
| [E21](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1018) | Pedidos | Listado |
| [E22](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1019) | Pedido #051 | Ventana |
| [E23](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1020) | Actualizar estado del pedido | Ventana |
| [E24](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1021) | Fondos asignados | Listado |
| [E25](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1022) | Registrar distribución informativa | Ventana |
| [E26](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1023) | Publicidad | Listado |
| [E27](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1024) | Preparar versión de anuncio | Ventana |
| [E28](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1025) | Resolver corrección de reporte | Ventana |
| [E29](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1026) | Devolver revisión de aporte | Ventana |
| [E30](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-1027) | Devolver pedido a la cola | Ventana |

### 06 · Expediente y excepciones

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [F01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3871) | Hola, doctora Laura. | Inicio |
| [F02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3872) | Expedientes autorizados | Listado |
| [F03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3873) | Expediente · Luna | Listado |
| [F04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3874) | Registrar anotación profesional | Ventana |
| [F05](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3875) | Enmendar anotación propia | Ventana |
| [F06](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3876) | Revisar soporte del dueño | Ventana |
| [F07](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3877) | Autorizar atención veterinaria | Ventana |
| [F08](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3878) | Accesos excepcionales | Listado |
| [F09](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3879) | Solicitar acceso excepcional | Ventana |
| [F10](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3880) | Resolver acceso excepcional | Ventana |
| [F11](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3881) | Revocar acceso temporal | Ventana |
| [F12](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3882) | Revocar autorización veterinaria | Ventana |
| [F13](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3883) | Asignar gestor a un fondo | Ventana |
| [F14](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-3884) | Documento privado | Ventana |

### 07 · Móvil

| Código | Pantalla o estado | Tipo |
| --- | --- | --- |
| [G01](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-5408) | Login móvil | mobile-login |
| [G02](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-5409) | Mi trabajo | mobile-dashboard |
| [G03](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-5410) | Solicitud de adopción #041 | mobile-form |
| [G04](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=13-5411) | Transferir responsabilidad | mobile-form |


### 08 · Acceso animado y recursos

| Código | Pantalla | Enlace |
| --- | --- | --- |
| L01 | Portada con nubes desde el inicio | [Figma](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=72-22) |
| L02 | Entrada del paisaje con títulos compartidos | [Figma](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=72-45) |
| L03 | Login final en escritorio | [Figma](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=72-56) |
| L04 | Login final en móvil | [Figma](https://www.figma.com/design/Kv2Na4SBOxyGoQ4tC8CMxR?node-id=72-100) |

El paquete `output/kit-capas-little-paws.zip` contiene las regiones vectoriales y PNG transparentes derivados del fondo suministrado. No se generaron imágenes con IA.
