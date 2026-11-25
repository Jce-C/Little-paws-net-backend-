# 60 · Flechas centradas y fichas públicas de organizaciones

Cierre de revisión: 22 de noviembre de 2026. Evidencia en `output/perfiles-y-flechas-2026-11-21` (carpeta iniciada el día anterior).

## Corrección visual solicitada

La flecha de cada tarjeta de Inicio estaba en una fila de contenido independiente del círculo decorativo. Ahora es hija del círculo y usa `Center`: comparte su centro horizontal y vertical. Se mantienen tamaño, recorte del círculo, paleta, borde y acción de la tarjeta completa. La decoración no crea otro foco ni botón duplicado para lectores de pantalla.

Cuatro pruebas comparan los centros geométricos a 280, 320, 412 y 720 px. Pasan también en el diseño de una sola columna para pantalla estrecha. La corrección se publicó en la **demo independiente, versión 7**, sin modificar Railway ni el repositorio oficial. Captura real: `flechas-centradas.jpg` en la carpeta de evidencia.

## Ficha pública administrable

Se añade `PerfilPublicoEntidad`, separado de los datos internos. Permite descripción editorial, servicios, teléfono, correo y sitio web públicos. No se copian teléfonos, WhatsApp, identificaciones ni información de integrantes existentes. El directorio conserva nombre, tipo, ciudad y los campos legacy que ya eran públicos.

El permiso existente **`entidades.editar`**, de alcance GLOBAL, administra estas fichas. Es configurable por RBAC y no depende del nombre del rol: las pruebas conceden ese permiso a Ciudadano, comprueban el acceso y lo retiran. Este permiso autoriza administrar organizaciones de la plataforma, no solamente la organización del usuario. No se concede automáticamente a gestores de equipos.

Recorrido:

1. En **Organizaciones y equipos**, elegir **Ficha pública** en la fila autorizada.
2. Completar los grupos **Sobre la organización** y **Contacto autorizado**.
3. Para guardar un borrador, dejar desmarcada la publicación y pulsar **Guardar ficha**.
4. Para publicar, escribir una descripción, marcar **Mostrar esta ficha en el directorio público**, confirmar la autorización y guardar.
5. Para retirar los campos del perfil público, desmarcar publicación y guardar. El registro básico de la organización permanece en el directorio si sigue verificada y activa.
6. Cancelar vuelve al listado; el mecanismo existente avisa si hay un borrador sin guardar.

La app muestra los datos explícitamente publicados como información seleccionable. No abre enlaces ni teléfonos automáticamente. Si no hay perfil público, conserva la descripción legacy y el aviso de contactos no publicados. No se añaden contactos o servicios ficticios a organizaciones reales.

## API, autorización y trazabilidad

- `GET /api/red/organizaciones/<id>/perfil/` devuelve la ficha editable, solo con `entidades.editar`.
- `PUT` en la misma ruta reemplaza los campos editoriales completos. `publicada` es obligatorio; publicar exige `confirmar_publicacion=true` y descripción no vacía.
- `GET /api/red/organizaciones/` añade el campo opcional `perfil_publico`: datos autorizados o `null`. No incluye editor, autorización, borradores ni claves internas.
- Solo pueden publicarse organizaciones verificadas y activas, de los tipos existentes fundación/clínica/tienda. Perder verificación o causar baja las oculta del directorio.
- Teléfono, correo, longitud de textos y URL se validan en el backend. Se exige HTTPS sin credenciales para el sitio web. El servidor no descarga ese enlace.
- La escritura vuelve a comprobar permisos dentro de la transacción y usa el bloqueo de seguridad compartido. La autorización no se basa en lo que muestre el navegador.
- El formulario web tiene CSRF, POST explícito, etiquetas, ayuda persistente y grupos semánticos; funciona sin JavaScript. Seleccionar un checkbox no publica por sí solo.
- Se registra actor, fecha, organización y valores anteriores/nuevos. La presentación distingue publicar, actualizar, guardar borrador y retirar; tolera registros incompletos.
- Se añadieron traducciones inglesas para la pantalla y los eventos nuevos.
- El directorio utiliza tres consultas de dominio (una por tipo de organización) en la prueba, sin consultar cada perfil por separado. No se agregan consultas al login.

Los cambios editoriales aparecen al recargar el directorio. No se ha implementado sincronización en vivo del directorio público. La revocación de permisos administrativos sí se comprueba en cada operación.

## Verificación y publicación

Suite canónica: **205 pruebas Flutter**, análisis sin incidencias y APK debug con API local `10.0.2.2:8016`, no instalado. Demo: **207 pruebas**, análisis limpio, compilación web y comprobación visual del círculo y flecha en la publicación v7. La demo solo recibe la corrección de flechas; sus contactos siguen siendo ficticios y no incorpora estas escrituras del backend.

Regresión backend: **66 pruebas** sobre directorio, perfiles, autorización configurable, publicación/retirada, CSRF, comercio, fotos, formularios web y actividad. Las pruebas usan únicamente MySQL local aislado. Los logs definitivos y hashes están en `validacion.json`.

Nueva migración: **`core.0012_perfilpublicoentidad`**, aplicada únicamente en la base de pruebas. La funcionalidad de perfiles y el bloque anterior de fotos comerciales siguen pendientes de integración y despliegue en el backend real. No se cambia la audiencia pública existente de la demo.

## Qué queda pendiente

- Logo público autorizado de organizaciones: este bloque implementa textos/contactos, no la subida de logos.
- Descripción editorial y cuidados por mascota, separados del expediente clínico privado.
- Actividades estructuradas de voluntariado y canales oficiales de aportes; no se simulan pagos recibidos.
- Recuperación de contraseña móvil, piloto con datos consentidos, dispositivo físico y TalkBack.
- Integración por integrantes, migraciones revisadas, almacenamiento persistente, respaldo/restauración y evidencia académica final.

## Reparto

José Carlos: modelo, migración, servicio/API, permisos y pruebas. Majo: presentación móvil y prueba de compatibilidad. Sally: centrado de tarjetas, formulario web, traducciones y guía. Paquetes separados actualizados sin commits, ramas ni publicación en el repositorio oficial y sin sobrescribir el Figma editable.
