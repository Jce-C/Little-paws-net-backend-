# Una consulta pendiente por vista privada

En Mis mascotas y Expediente privado, pulsar actualizar o iniciar varias actualizaciones antes de recibir la respuesta podía crear consultas simultáneas. Aunque la interfaz descartaba datos antiguos, las peticiones repetidas consumían red y presupuesto de lectura.

Cada instancia de pantalla comparte ahora su petición pendiente. El botón de actualización queda deshabilitado hasta recibir una respuesta; el gesto de actualización y los reintentos usan la misma operación mientras siga pendiente. Al finalizar, tanto con éxito como con error, se libera la petición para permitir una nueva consulta explícita. No se almacena una caché persistente de expedientes.

Se conserva una sola zona de desplazamiento y la presentación existente. Durante la actualización se ocultan los datos anteriores; una denegación no deja visible el expediente ni el acceso a su QR. Cambiar de cuenta crea otra instancia identificada por usuario y mascota: no se comparten datos ni peticiones entre cuentas.

## Reproducir

Desde `frontend/mobile`:

```sh
flutter test test/owned_pet_refresh_test.dart test/medical_session_boundaries_test.dart test/owned_pets_test.dart --reporter expanded
flutter test --reporter expanded
flutter analyze
flutter build apk --debug --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016
```

Las dos nuevas pruebas mantienen respuestas pendientes y solicitan tres actualizaciones durante la carga inicial: solo se realiza una consulta. Después agrupan dos actualizaciones en una segunda consulta, simulan un error 503, comprueban que no hay reintento automático y recuperan la pantalla mediante Reintentar. Las regresiones existentes comprueban cierre de sesión, cambio de cuenta y revocación 403.

Todas las respuestas y cuentas de las pruebas son sintéticas mediante MockClient; no se escribe ni consulta Django, MySQL o Railway. El transporte y los permisos del servidor no cambian. La mejora reduce consultas duplicadas de esta vista, sin establecer cifras de rendimiento de producción.

## Alcance y continuidad

La prueba de interacción es de widgets Flutter. El APK de este bloque se verifica como compilación local separada; las capturas previas conservan su hash de origen y no se presentan como capturas del nuevo binario. No se actualiza la demo web alojada desde esta tarea local.

Se revisó el contexto y la captura del frame Figma `128:599`: su composición de expediente incluye un carnet y un QR de ejemplo que no se deben trasladar a fichas reales. Este cambio solo gestiona el estado de la actualización; la composición compacta del expediente permanece pendiente de una implementación visual con datos reales y su comprobación nativa.

María José: pantalla y regresiones; Sally: guía y evidencias; José Carlos: backend sin cambios. Permanecen pendientes validación física/TalkBack/firma y contratos de mapa, fotos de reporte, tienda y apadrinamiento.
