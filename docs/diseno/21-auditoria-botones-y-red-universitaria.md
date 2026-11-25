# Auditoría de botones y diagnóstico de red universitaria

Fecha: 2026-11-04.

## Alcance y resultados

Inventario automatizado en navegador local, con cuenta de pruebas autorizada: 27 páginas y 586 diálogos representativos de rutas y operaciones disponibles. Se inspeccionaron 18.215 apariciones de controles, incluyendo controles compartidos repetidos entre vistas; no son 18.215 botones únicos. No se detectaron botones de envío sin formulario ni botones visibles sin nombre accesible en el inventario. Esto no sustituye probar todas las combinaciones posibles de datos y permisos.

Las 242 pruebas Django pasan. Se verificaron además 62 comprobaciones de interfaz: confirmaciones de eliminación (6), cambios pendientes (12), landing/login y avisos (14), barra fija y accesibilidad (13), menú móvil (1), combobox con teclado (2), asignación de perfiles (6), sincronización RBAC entre sesiones (5) y botones de matriz de permisos (3).

Se corrigió un fallo adicional: la confirmación de eliminación buscaba el botón únicamente entre los descendientes del formulario; al estar el botón en el pie fijo asociado mediante el atributo form, no lo encontraba y producía una excepción JavaScript al habilitarlo. Ahora utiliza form.elements, que incluye los controles asociados fuera del formulario. Se preservan motivo, aceptación y confirmación del nombre cuando se exige. Se verificó una eliminación real únicamente sobre un rol sintético local sin dependencias. El arreglo anterior del campo id y el guardado de nombres de recursos se documenta en 20-guardado-nombres-recursos.md.

Las pruebas modifican exclusivamente la base local. No se cambiaron cuentas, permisos ni datos de negocio en producción. Se actualizó una prueba antigua del menú para usar el botón de tres rayas vigente, y se renovaron sesiones locales caducadas para la aceptación.

## Fortinet

El usuario confirmó que el mismo login abre sin advertencia mediante datos móviles, mientras falla en la red universitaria. Una lectura del certificado TLS recibido en esta red identifica al emisor como Fortinet y falla la validación de confianza con UNABLE_TO_VERIFY_LEAF_SIGNATURE. Se inspeccionó el certificado público sin enviar HTTP ni credenciales y sin modificar los certificados o la confianza del sistema.

Esto acota el incidente al trayecto de red universitaria y su inspección HTTPS. No se desinstaló Fortinet, no se modificó el firewall y no se deshabilitó la validación TLS de la aplicación. Corresponde al equipo de redes universitario revisar la inspección, la cadena de confianza y, si aplica, la clasificación o autorización del dominio little-paws-panel-production.up.railway.app.

Referencias oficiales:
- https://support.google.com/chromebook/answer/95669?hl=es
- https://community.fortinet.com/fortigate-3/troubleshooting-tip-untrusted-certificate-warning-for-https-websites-during-ssl-deep-inspection-92584

Evidencias locales: output/auditoria-botones-2026-11-04/ y .codex_tmp/auditoria-botones-django-20261104.log.
