# O03/O04 — Mi cuenta y mascotas personales

Fecha: 24 de noviembre de 2026. Implementación local, sin publicación ni migración nueva en este bloque.

## Recorrido e integración

Mi cuenta conserva identidad, edición de nombre/teléfono, correo y roles de solo lectura, seguridad y accesos personales. La vista previa solicita hasta tres mascotas; no presenta esa muestra como un total global. Volver de Mis mascotas o de un registro actualiza la vista previa. Una mascota personal abre su ficha privada; una adopción conserva su expediente médico. Se corrigió el enlace que confundía esos dos destinos.

Agregar mascota usa bloques cálidos coherentes con los formularios compartidos: nombre/especie requeridos, detalles opcionales y foto privada. Admite especies y razas no catalogadas sin inventar registros del catálogo. Los máximos coinciden con el servidor; edad entre cero y seiscientos meses. Cancelar y Registrar permanecen accesibles en el pie; el descarte requiere confirmación si hay borrador. Un fallo conserva datos y muestra un diálogo. Una respuesta incierta permite comprobar el registro antes de repetir; salir avisa que puede haberse guardado.

Los formularios y listados privados cambian de identidad al cerrar/reiniciar sesión, incluso con el mismo correo: un borrador anterior no se hereda. Una actualización del perfil no provoca ese reinicio.

## Contrato y seguridad

- `POST /api/mascotas/personales/`: exige `mascotas.participar`, deriva el titular de la sesión y rechaza campos ajenos al contrato (incluidos dueño y estado). Conserva el recibo idempotente de creación.
- `GET /api/mascotas/personales/{id}/`: exige permiso y titularidad, con respuesta privada `no-store`. Incluye especie con la misma consulta.
- `GET /api/mascotas/mias/?pagina=1&limite=3`: muestra limitada para Mi cuenta; listado completo conserva páginas de veinte y cursor. Límite válido entre uno y veinte. La respuesta histórica sin paginación permanece compatible.
- Foto normalizada en backend a WebP, máximo 160 px y 16 KiB. No se publica ni se pide consentimiento para publicar algo que permanece privado.
- Registrar una mascota personal crea estado **Con dueño**, sin custodia de organización. No publica un animal en adopción ni genera un expediente médico ficticio.

## Trazabilidad y evidencia

| Unidad | Implementación | Verificación |
|---|---|---|
| O03 identidad y perfil | `SessionActionGate`, `AccountScreen`, `profile_screen.dart` | Cambio de sesión, fallo/reintento y guardado con teclado/texto ampliado |
| O03 vista previa | `account_overview.dart`, `profile_pet_preview.dart` | Consulta de tres, actualización al regresar, ruta privada correcta |
| O04 formulario | `personal_pet_screen.dart` | Cancelación/descarte, validación, pie accesible a 320×640 y 200 % |
| O04 API real | `personal_views.py`, `mobile_views.py` | HTTP desde Flutter a Django/MySQL aislado y comprobación posterior de persistencia |
| RBAC/propiedad | Permiso servidor y filtro titular | Acceso anónimo y ajeno rechazados; fuera del catálogo público de adopción |

Evidencias del workspace: `output/correcciones-app-2026-11-24/cuenta-mascotas`.

- Backend ampliado: 145 pruebas aprobadas (cuentas, animales, adopción, API core, reintentos y RBAC dinámico/roles abiertos).
- Cliente canónico: 293 aprobadas y ocho optativas omitidas. Focales finales: 31 aprobadas. Análisis sin observaciones y APK debug compilado.
- `http-real.json`, `http-cliente.txt`: perfil actualizado/restaurado, creación con foto, repetición con el mismo ID, lista y detalle propios, rechazo de otra cuenta y del acceso anónimo; no aparece en adopción pública.
- `persistencia-real.json`: una ficha privada y un recibo de creación, titular/estado correctos, foto WebP de 2928 bytes, 160×88, sin EXIF ni custodia. Datos sintéticos en MySQL QA aislado. Servidor HTTP QA detenido al acabar.
- Capturas y mosaico: renderizados Flutter con fixtures; no son un dispositivo físico ni datos productivos. Se revisaron vista previa, ficha privada y registro.

## Demos y cierre de compilación

Las once piezas compartidas del cliente y sus pruebas se sincronizaron en `demos/mobile-visual` y `sites/little-paws-mobile-demo`, preservando los servidores simulados y adaptando su límite de listado. Demo Android local: 367 pruebas aprobadas y cuatro capturas opcionales omitidas, análisis sin observaciones. Demo web: 31 focales aprobadas, análisis limpio y compilación release correcta en `build/web`, sin copiar a alojamiento ni publicar. Persiste la advertencia previa de CupertinoIcons no empaquetada; se conserva como pendiente de la auditoría global.

Se renderizaron además seis recorridos visuales de cuenta, perfil y Mis mascotas (escala normal y texto 200 %), todos aprobados. `inventario` conserva la última captura de cada pantalla. La foto del recorrido HTTP no aparece en esas capturas ficticias; su integridad se acredita por la prueba HTTP y persistencia. No se ejecutó aceptación en dispositivo físico en este bloque.

## Estado

Se cierran O03/O04: **33/57 unidades (57,9 %)** de la guía 75, conteo simple de esa lista, no porcentaje de la aplicación completa. Sigue O05 (ayudas/ofrecimientos), O06 (rutas restantes) y Q01-Q10 (aceptación integral). Permanecen las decisiones jurídicas/documentales, licencias, privacidad/retención/derechos, seguridad final, respaldo/restauración, firma Android/dispositivo real, paquetes de los tres integrantes y presupuesto gratuito/VPS. No se certifica aún publicación ni rendimiento productivo.
