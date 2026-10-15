# Panel interno de Django Admin

El panel `/admin/` es una herramienta de soporte y demostración, no la interfaz
de los usuarios de Little Paws Net. La copia de evaluación se conecta a MySQL
de Railway y usa la cuenta temporal de superusuario indicada por el equipo.
No utilizar esa cuenta como cuenta cotidiana.

## Qué se puede cargar desde el panel

1. **Catálogos básicos:** `TipoMaestro`, `ValorMaestro`, `Ciudad`, `Zona`,
   `Especie` y `Raza`. No se permite borrarlos desde Admin. Los valores de
   estado y tipo cargados por las migraciones son utilizados por el código;
   no se deben renombrar sin ajustar las reglas correspondientes.
2. **Usuarios:** el formulario de alta exige dos veces la contraseña, aplica
   los validadores de Django y guarda únicamente el hash. Una cuenta creada
   allí es un usuario normal, sin acceso a Admin ni privilegios de plataforma.
3. **Reportes:** el alta solicita tipo, descripción y coordenadas. El estado
   inicial `Pendiente`, el usuario reportante, la ubicación y el primer evento
   del historial se guardan juntos. Si faltan los catálogos sembrados por las
   migraciones, primero ejecutar `python manage.py migrate`.

Los modelos de rescate, expediente, adopciones, fondos y comercio registrados
como **solo consulta** permiten revisar los resultados. Aprobar, cerrar,
confirmar o cambiar estados se hace por las API/servicios del proceso, ya que
editar esas tablas directamente omitiría permisos y trazabilidad.

## Comprobación rápida

Con el entorno virtual activo y el `.env` de demostración configurado, desde `backend/`:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --settings=config.test_settings
python manage.py runserver
```

Entrar en `http://127.0.0.1:8000/admin/` y probar en este orden:

1. Revisar los usuarios ficticios en **Accounts → Usuarios**.
2. Revisar los reportes en **Rescue → Reportes** y sus detalles.
3. Añadir una especie o un usuario de prueba y confirmar que aparece en la lista.
4. Revisar mascotas, casos y apadrinamientos. Sus estados sensibles solo cambian
   mediante las API y servicios previstos; no fuerce cambios directos desde Admin.

Los cambios de `admin.py` no alteran el esquema de MySQL ni requieren nuevas
migraciones. El modelo `Usuario` actual solo concede permisos de Django Admin
a superusuarios; habilitar personal de soporte con permisos diferenciados
requiere integrar cuidadosamente el sistema de permisos de Django con el RBAC
de la plataforma.
