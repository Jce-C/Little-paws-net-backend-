# Colaboración

- José Carlos (`Jce-C`): identidad, modelos compartidos, reporte, rescate y expediente.
- María José (`MAJO025`): adopción y fondo externo.
- Sally Andrea (`andreagutiber-pixel`): productos, pedidos y publicidad.

Cada integrante trabaja desde su propia cuenta GitHub en una rama y realiza commits pequeños por funcionalidad. `git config user.email` debe corresponder a un correo asociado a su cuenta; nunca se modifica la autoría de otra persona. Los Pull Requests se integran sin squash para conservar los commits.

Cada proceso debe exponer claramente `models.py`, `serializers.py`, `views.py` y `urls.py`, además de reglas de negocio y pruebas donde corresponda. Los serializers validan datos; permisos y servicios verifican autorización. No se usan templates para esta API. No introducir contraseñas, tokens, datos médicos reales ni archivos `.env` en Git.

Las apps nuevas se integran en orden de dependencias. Antes de cada commit: revisar el diff, ejecutar `manage.py check`, comprobar migraciones y ejecutar las pruebas aplicables. No rehacer ni falsificar commits ajenos.
