# Solicitud de adopción: trazabilidad desde Android y panel

## Problema real

El endpoint POST /api/adopcion/solicitudes/ creaba la solicitud sin emitir un evento de seguridad. El panel añadía un evento genérico al utilizarlo internamente, pero Android llamaba a la API directamente y no ejecutaba ese envoltorio. La creación desde el móvil no incrementaba la revisión del panel y no quedaba trazada de la misma manera.

## Corrección

La API registra una sola creación mediante el servicio auditar existente, dentro de la misma transacción de la solicitud. La acción es adopcion.participar, con operación solicitar-adopcion, actor, identificador de solicitud, mascota, fundación de la custodia y transición inicial a Pendiente. La política y la autorización existentes se conservan. No se copian observaciones libres, contactos ni credenciales al evento.

El evento activa el mecanismo de revisión del panel ya existente. No se añade un canal de red, un sondeo por cliente ni una migración. El envoltorio del panel reconoce el evento emitido y evita crear otro genérico.

Si falla la auditoría, la solicitud se revierte. El middleware puede registrar por separado el intento fallido y elevar la revisión; esto no significa que la solicitud se haya creado. El ensayo comprueba la ausencia del registro y del evento de éxito.

## Comprobaciones

adoption.tests_solicitud_auditoria contiene siete casos sobre MySQL local aislado: éxito con metadatos mínimos, duplicado pendiente, denegación anónima, rol revocado, mascota no disponible, reversión al fallar auditoría y recorrido web sin evento duplicado. Se usa únicamente información sintética. No cambia el contrato de respuesta esperado por Android.

## Reparto e integración

José Carlos: aplicar 01-solicitud-auditoria.patch y copiar adoption/tests_solicitud_auditoria.py desde el módulo 01; ejecutar las siete pruebas y la regresión completa en una base local propia. Sally: guía y evidencia; María José no necesita modificar el contrato del cliente.

Esta entrega sigue local. No se crean commits ni se modifican Railway o datos reales. Persisten las validaciones comerciales de almacenamiento/restauración, dispositivo físico, TalkBack, rendimiento y firma.
