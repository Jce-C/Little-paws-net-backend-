# Cierre funcional de la etapa 2 — Backend Django

Fecha: 2026-10-26.

**Estado: base funcional de autorización y recorridos aprobados preparada para conectar el acceso web de la etapa 3.** Se amplió el bloque inicial, se aplicaron las migraciones y se ejecutaron 84 pruebas sobre una instancia MySQL independiente. Esto no declara desplegado un producto en producción ni implementado su frontend.

La explicación de cada archivo y tecnología está en [Guía de archivos y tecnologías](05-guia-archivos-y-tecnologias.md). Las decisiones originales permanecen en los documentos 01 y 02. El informe 04 conserva el estado histórico del primer bloque.

## 1. Qué faltaba y qué se añadió

| Pendiente del primer bloque | Implementación entregada |
| --- | --- |
| Cuentas receptoras | Delegación específica por el principal, preparación por otra persona, revisión del principal y publicación de una nueva cuenta. Conserva la anterior y sus referencias. Una propuesta basada en una cuenta ya sustituida no sobrescribe la nueva configuración. |
| Acceso excepcional | Solicitud para un único registro, autoridad competente sobre ese dato, sin autoaprobación, consulta únicamente, aprobación de 1 a 24 horas, vencimiento y revocación. No permite autorizar un expediente entero mediante un filtro. |
| Documentos privados | Carga de PDF/PNG/JPEG de hasta 10 MB, nombres aleatorios, metadatos separados del contenido y descarga autorizada por petición. No se entrega una URL pública del archivo. |
| Verificaciones | Creación por el responsable de la entidad, documentos privados, revisión asignada, petición de correcciones, reenvío y aprobación/rechazo. Se conservan documentos anteriores y auditoría. Un reenvío no verifica automáticamente a la entidad. |
| Soportes clínicos del dueño | Adjuntos separados de las anotaciones profesionales y sin validación automática. El veterinario verificado y autorizado registra validación o solicitud de aclaraciones. |
| Enmiendas clínicas | Nuevo registro vinculado al original, con motivo, autor y fecha. Solo el profesional autor con autorización vigente puede enmendarlo. Se conserva la anotación original. |
| Reclamaciones de mascotas | Reclamación con soportes, toma exclusiva por moderador, revisión asignada y decisión justificada. No concede lectura clínica por recibir el caso. |
| Cambio de titularidad | Segundo paso explícito después de una decisión favorable, con destinatario y titular actual confirmados en la petición. Comprueba otra vez el titular, impide ejecutar una decisión obsoleta, conserva historial, revoca autorizaciones clínicas/QR y notifica internamente. Una mascota en custodia de una fundación no se entrega por este atajo. |
| Solicitudes de adopción | Consulta autorizada del detalle, respuestas propias con versiones y retirada confirmada mientras está pendiente. Se bloquea la resolución posterior al retiro; comparte el orden de bloqueo de la resolución existente. |
| Reportes | Edición/cierre del reportante registrado antes de aceptación; propuesta de corrección de un reporte aceptado y revisión de la fundación. Ocultación con motivo y republicación solo después de solicitud del autor y decisión de moderación. Corregir no republica. |
| Catálogo y pedidos | Crear/editar productos de la tienda autorizada, con historial de precio/disponibilidad; conserva precios referenciales de pedidos existentes. El gestor de pedidos requiere asignación y realiza transiciones entre los estados existentes. |
| Rescates | Cambios explícitos de En atención a Cerrado o Cancelado, con autorización de la fundación e historial. No mezcla la moderación pública con el estado del caso. |
| Publicidad | Anuncios de la entidad y versiones separadas pendientes de revisión. Una versión pendiente no sustituye a la aprobada visible. Se controla vigencia y ocultación. La consulta pública existente incorpora los anuncios nuevos aprobados. |

Los anuncios anteriores conservan su consulta pública bajo sus reglas originales de aprobación y vigencia. Se añadió una acción de ocultación para moderación; no se reescribieron los anuncios históricos como si tuvieran versiones que nunca existieron. Los anuncios nuevos utilizan el recorrido de versiones.

## 2. Titularidad: los dos pasos aprobados

1. **Resolver la reclamación.** El moderador asignado revisa motivos y soportes y registra FAVORABLE o RECHAZADA. Esto no cambia al dueño ni concede al reclamante acceso clínico.
2. **Ejecutar el cambio.** El revisor todavía autorizado envía una operación distinta indicando el titular que espera encontrar, el reclamante que recibirá la ficha y el motivo. El servidor bloquea la ficha y comprueba que nada relevante haya cambiado. Solo entonces registra la entrega y revoca los accesos vinculados al titular anterior.

Casos contemplados: moderador con conflicto personal, rol revocado, dos revisores que intentan tomar el mismo caso, decisión no favorable, decisión desactualizada, destinatario diferente al revisado, cuenta destinataria inactiva y mascota bajo custodia. Ninguno se resuelve mediante un cambio libre del campo `dueno`.

Esta operación administra la titularidad y los accesos **de la ficha en la aplicación**; el registro de una decisión no sustituye otros procedimientos de acreditación que correspondan fuera de la aplicación.

## 3. Dónde están las API nuevas

Prefijo común: `/api/seguridad/operaciones/`. Las peticiones privadas usan la autenticación JWT existente y permisos actuales; no basta con conocer la dirección.

| Ruta relativa | Métodos y finalidad |
| --- | --- |
| `mis-registros/` | GET: identificadores propios, asignaciones e historial de revocación |
| `entidades/{entidad}/delegacion-cuentas/` | POST: delegar o revocar al preparador de cuentas |
| `entidades/{entidad}/propuestas-cuenta/` | GET/POST: consultar propuestas y preparar cambios |
| `propuestas-cuenta/{id}/` | GET: detalle privado para revisión; POST: aprobar/rechazar |
| `excepciones/` | GET/POST: solicitudes de acceso específicas |
| `excepciones/{id}/resolver/`, `excepciones/{id}/revocar/` | POST: decisiones explícitas |
| `registros/{recurso}/{id}/` | GET: detalle privado sujeto a titularidad, asignación o autorización específica |
| `documentos/{recurso}/{id}/cargar/` | POST multipart con campo `archivo` |
| `documentos/{id}/descargar/` | GET: descarga autorizada, sin caché y como adjunto |
| `historiales/{id}/enmiendas/` | POST: corrección profesional vinculada |
| `soportes/{id}/revisar/` | POST: resultado profesional del soporte |
| `autorizaciones/{id}/revocar/` | POST: revocar autorización clínica como titular/custodio competente |
| `adopciones/{id}/respuestas/`, `adopciones/{id}/retirar/` | POST: gestionar solicitud propia pendiente |
| `reportes/{id}/propio-pendiente/` | PATCH: edición propia; POST con confirmación: cierre propio |
| `reportes/{id}/correcciones/`, `correcciones/{id}/resolver/` | GET/POST: cambios propuestos y decisiones |
| `reportes/{id}/moderacion/` | POST: ocultar, solicitar revisión o republicar, según el actor |
| `reportes-publicos/` | GET público: contenido visible sin contacto del reportante |
| `entidades/{entidad}/verificaciones/` | POST: iniciar solicitud propia de verificación |
| `verificaciones/{id}/resolver/` | POST: aprobar, rechazar, pedir correcciones o reenviar, según el actor |
| `entidades/{entidad}/anuncios/`, `anuncios/{id}/versiones/` | GET/POST: gestionar anuncios propios y enviar nuevas versiones |
| `publicidad-pendiente/`, `versiones-anuncio/{id}/revisar/` | GET/POST: revisión de publicidad por moderación |
| `publicidad-anterior/{id}/ocultar/` | POST: moderación de un anuncio histórico |
| `reclamaciones/`, `reclamaciones/{id}/tomar/` | GET/POST: casos propios o cola mínima y toma del revisor |
| `reclamaciones/{id}/resolver/` | POST: primer paso de decisión |
| `reclamaciones/{id}/ejecutar-titularidad/` | POST: segundo paso explícito de aplicación |
| `mascotas-propias/` | POST: declarar una nueva ficha propia; no admite ID de ficha existente ni otro dueño |
| `entidades/{entidad}/productos/`, `productos/{id}/` | GET/POST y PATCH: catálogo de la propia tienda |
| `pedidos/{id}/estado/`, `casos/{id}/estado/` | POST: cambios de estado permitidos |

El contrato de campos de entrada está en `flujos_serializers.py`, y las condiciones adicionales en `flujos.py`. Los listados de este bloque usan límites acotados; la paginación avanzada por cursor y las búsquedas de un despliegue de mayor escala no forman parte de esta entrega.

### Ejemplo de cambio de titularidad

Primera petición, a `reclamaciones/12/resolver/`:

```json
{"aprobar": true, "motivo": "Soportes revisados y decisión registrada"}
```

Segunda petición independiente, a `reclamaciones/12/ejecutar-titularidad/`:

```json
{"dueno_actual_id": 7, "nuevo_dueno_id": 9, "motivo": "Aplicación expresa de la decisión revisada"}
```

Los identificadores son ejemplos. El nuevo dueño debe ser el reclamante del caso revisado; si cambia el dueño desde la revisión o existe custodia de una fundación, se rechaza esta ejecución.

## 4. Validación y estado local

- **84 pruebas aprobadas** en MySQL 8.0.46, con todas las migraciones, datos sintéticos y archivos de prueba en directorios temporales.
- Incluyen los 56 escenarios del bloque inicial y 28 adicionales de aprobaciones, alcance privado, excepciones, enmiendas, titularidad, versiones, catálogo y estados.
- Se ejecutaron con conexiones concurrentes reales: dos revisores compitiendo por una verificación, dos moderadores por una reclamación y retirada frente a aprobación de una adopción.
- `manage.py check`: sin incidencias. `manage.py makemigrations --check --dry-run`: sin diferencias pendientes de modelos.
- Aplicadas en la base local: `seguridad.0004`, `0005` y `0006`, además de las del bloque inicial.
- Catálogo actual: **13 roles del sistema activos, 20 recursos y 51 permisos reconocidos**.
- La base local conserva **20 usuarios, 0 activos y 0 administradores activos**. No se crearon credenciales públicas ni se reactivaron cuentas demo.
- El almacenamiento `.private-data/` está excluido de Git. Los archivos sintéticos de la suite no se guardaron en el almacenamiento habitual.

Para reproducir las pruebas, utilizar la configuración aislada y el comando documentados en el informe 04. No ejecutar pruebas con el esquema habitual de la aplicación.

## 5. Qué necesita el propietario para entrar en la etapa 3

No hace falta compartir claves, contraseñas ni otro diseño para continuar con la conexión del login. Antes de utilizarlo con una cuenta real se debe inicializar localmente el primer Administrador de seguridad:

```powershell
# Desde backend, sustituir TU_CORREO por el correo del propietario.
.\.venv\Scripts\python.exe manage.py iniciar_seguridad --email TU_CORREO --nombre "Tu nombre"
```

La persona escribe su contraseña oculta en su terminal. El comando no la recibe como argumento ni la imprime. Si ya existe un administrador activo, se utilizan las operaciones autorizadas normales de asignación.

## 6. Límite de esta entrega y paso siguiente

La etapa 2 deja disponibles las reglas, tablas, API y pruebas para conectar la interfaz. La **etapa 3** implementará el acceso web y su comportamiento de sesión, CSRF cuando corresponda, captcha básico, límites de intentos y navegación por permisos. La **etapa 4** conserva el boceto de Figma y su refinamiento visual.

Actualización del 26 de octubre: la [etapa 3 ya está implementada](07-etapa-3-acceso-web.md), con 107 pruebas aprobadas en total. También se entrega el [boceto completo de Figma](../diseno/README.md). El alcance descrito en este cierre corresponde a la etapa 2; el informe nuevo distingue el panel inicial programado de los formularios propuestos para conectar después.

No se implementaron procesamiento de pagos, validación bancaria automática, envío externo de notificaciones, una aplicación móvil ni el frontend del panel. No son funciones de autorización que deban darse por hechas por disponer de permisos en la base.

Los archivos se descargan como adjuntos y se comprueba su formato inicial; esto no equivale a análisis antimalware. El almacenamiento local, la estrategia de respaldo, el servidor HTTPS, el control de tráfico y un posible servicio de análisis de archivos se configuran según el despliegue. No hay un despliegue público realizado por este trabajo.
