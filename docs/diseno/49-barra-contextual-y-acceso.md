# Barra contextual y restauración del acceso · 20 noviembre 2026

## Cambio solicitado

La referencia muestra un círculo elevado sobre una cápsula con una concavidad real. Se reemplaza el medallón decorativo interno de la revisión48 por un botón de56 con recorte de34 de radio y separación visible. La cápsula empieza24 por debajo del botón. `ClipPath` y `CircularNotchedRectangle` dibujan el hueco; el fondo queda visible, sin parches de color que se rompan al cambiar de superficie.

Los cuatro destinos mantienen sus etiquetas y selección. Con texto ampliado se distribuyen en dos columnas, conservando el botón central y objetivos táctiles de al menos48. La barra reserva su altura en el Scaffold y se oculta con teclado. La transición del icono dura180ms y se desactiva con reducción de movimiento.

## Acciones

- Desde Inicio, Adoptar y Mi cuenta, el perro central lleva a Inicio.
- Desde Solicitudes, se convierte en más («Nueva solicitud de adopción») y abre Adoptar para seleccionar una mascota. No envía una solicitud ni elige una mascota automáticamente.
- La ficha, el formulario, la autenticación y los permisos existentes siguen controlando el envío real.

## Acceso anterior

Login y registro recuperan el tema anterior de controles15,5, botones crema con relieve, encabezado22 y ancho máximo393. `access_theme.dart` encapsula esa apariencia para no revertir el diseño nuevo del resto de la app. Se mantienen validaciones, token, carga y errores; no se restaura una implementación antigua de autenticación. El marcado de campo y los errores siguen en el flujo para texto ampliado.

## Fotografías y emulador

La API real no tenía fotografías públicas publicadas para sus mascotas de QA; por eso enseñaba marcadores. La web era una demo con transporte ficticio y fotos locales de ejemplo. No se asignan esas fotos a fichas reales para esconder la diferencia.

Se prepara `demos/mobile-visual` como Android independiente, paquete `net.littlepaws.little_paws_net.visualdemo` y etiqueta «LPN · Demo visual». Reutiliza la UI nueva, `DemoData`/`MockClient` y fotografías locales acreditadas. No conecta con Railway o Django y no reemplaza la app real `net.littlepaws.little_paws_net`. La franja «DEMO · datos ficticios» permanece visible. El simulador se compila con `--target lib/demo_main.dart`; no usar la entrada real main.dart para distribuir esta demo.

La versión QA real se recompila por separado, con LPN_API_BASE_URL local y sin credenciales embebidas. En el emulador se abre la demo visual para revisar las imágenes y la barra. Los procesos de negocio deben seguir probándose con la app QA conectada a su base aislada.

## Pruebas y evidencia

Las regresiones de navegación comprueban cuatro destinos, selección, límites táctiles, área segura, texto200 %, botón superior pulsable y hueco sin relleno. La prueba de integración de widgets comprueba Solicitudes → más → catálogo → perro → Inicio y que no se envía un POST por tocar el más. Se conserva la suite de sesión y adopción. Revisar el acta de output/barra-contextual-2026-11-20 para resultados finales, hashes y capturas del emulador.

No se cambian modelos, migraciones, permisos ni Railway. No se crean commits o ramas en el repositorio oficial. La actualización de la demo alojada es independiente y conserva su audiencia pública y sus datos ficticios.
