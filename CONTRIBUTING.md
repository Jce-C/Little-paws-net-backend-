# Colaboración

- José Carlos (`Jce-C`): identidad, modelos compartidos, reporte, rescate y expediente.
- María José (`MAJO025`): adopción y fondo externo.
- Sally Andrea (`andreagutiber-pixel`): productos, pedidos y publicidad.

Cada integrante trabaja desde su propia cuenta GitHub en una rama y realiza commits pequeños por funcionalidad. `git config user.email` debe corresponder a un correo asociado a su cuenta; nunca se modifica la autoría de otra persona. Los Pull Requests se integran sin squash para conservar los commits.

Cada proceso debe exponer claramente `models.py`, `serializers.py`, `views.py` y `urls.py`, además de reglas de negocio y pruebas donde corresponda. Los serializers validan datos; permisos y servicios verifican autorización. No se usan templates para esta API. No introducir contraseñas, tokens, datos médicos reales ni archivos `.env` en Git.

Las apps nuevas se integran en orden de dependencias. Antes de cada commit: revisar el diff, ejecutar `manage.py check`, comprobar migraciones y ejecutar las pruebas aplicables. No rehacer ni falsificar commits ajenos.

## Secuencia de trabajo

1. María José incorpora primero las entidades compartidas de mascotas (`animals`) y solicita revisión. José Carlos integra ese PR sin squash antes de construir `rescue`, que depende de `Mascota`.
2. José Carlos incorpora reporte, caso y trazabilidad en varios commits. Después, María José continúa adopción y fondo externo en commits separados.
3. Sally Andrea puede desarrollar comercio en paralelo, pues depende únicamente de `accounts` y `core`.

Ejemplos de commits pequeños por responsabilidad:

- María José: `feat(animals): modelar mascotas`, `feat(adoption): modelar solicitudes`, `feat(adoption): resolver solicitudes`, `feat(funds): registrar distribuciones`, `test(adoption): cubrir decisiones`.
- Sally Andrea: `feat(commerce): modelar productos`, `feat(commerce): consultar catálogo`, `feat(orders): iniciar pedidos`, `feat(ads): gestionar anuncios`, `test(orders): validar tienda`.
- José Carlos: `feat(rescue): modelar reportes`, `feat(rescue): aceptar casos`, `feat(rescue): consultar seguimiento`, `test(rescue): cubrir autorizaciones`.

Los mensajes son orientativos: cada commit debe contener cambios reales y comprobables. Antes de comenzar, cada integrante configura `git config user.name` y `git config user.email` localmente, verifica que el correo esté vinculado a su propia cuenta GitHub y obtiene acceso al repositorio. La secuencia habitual es crear una rama propia, programar y probar una función, revisar con `git diff`, hacer `git add` solo de los archivos de esa función, `git commit`, `git push` y abrir un Pull Request. Las migraciones se generan con Django y se incluyen junto al modelo correspondiente.
