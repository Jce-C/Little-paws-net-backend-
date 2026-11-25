# Base local para integrar y preparar commits

Estado: base técnica consolidada y comprobada en local. No hay commits, ramas nuevas, push, tag ni despliegue realizados por este cierre. No se cambió la base productiva.

## Qué queda preparado

- Backend y panel: usuarios, roles múltiples, permisos/excepciones, menú dinámico, auditoría y áreas de negocio conservados. La suite completa comprueba también adopciones, reportes, pedidos y límites de acceso.
- Tienda: búsqueda y categorías en el servidor, páginas de veinte productos y carga adicional explícita; se comprobó recuperar 500 productos sin duplicados. El primer JSON de esa muestra baja de 26.928 a 5.385 bytes. Los clientes anteriores mantienen el listado limitado compatible.
- App: recuperación de errores y respuestas antiguas, tarjetas existentes y adaptación al texto ampliado conservadas. La dirección del backend debe configurarse al compilar; no se usa Railway por omisión ni se conecta una versión sin configuración.
- Integración: GitHub Actions queda preparado para todas las aplicaciones Django y las pruebas de herramientas. Su ejecución remota se verificará después del push; no se anuncia como ejecutada en GitHub.

Verificación final de este cierre: **476 pruebas backend aprobadas en MySQL aislado; 370 pruebas del cliente aprobadas y nueve optativas omitidas; siete pruebas de herramientas; análisis limpio en tres copias; 18 focales por demo; compilaciones Android debug y web release correctas.** Django check sin incidencias y sin nuevas migraciones pendientes de generar.

## Código y separación para el equipo

Repositorio oficial: `https://github.com/Jce-C/Little-paws-net-backend-`.

| Orden | Persona | Paquete | Rama sugerida, aún no creada |
|---|---|---|---|
| 1 | José | `01-jose-backend.zip` | `fix/integracion-backend` |
| 2 | Sally | `02-sally-app-movil.zip` | `feature/app-movil-integrada` |
| 3 | Majo | `03-majo-diseno-panel-documentacion.zip` | `feature/diseno-panel-y-trazabilidad` |

Paquetes actuales: `output/base-solida-2026-11-25/paquetes`. Cada ZIP contiene `LEEME.txt`, `cambios.patch` y `manifest.json`. Son cambios acumulados sobre la base indicada en el manifiesto, no parches para superponer a los ZIP anteriores. Las credenciales, bases, archivos privados y compilados no forman parte de estos paquetes.

Primero se comprueba el conjunto en una copia de integración; después cada integrante prepara su bloque en su rama. Backend primero, cliente después y diseño/documentación al final. El cliente conserva compatibilidad durante la transición, pero el resultado completo requiere integrar las tres áreas.

## Aplicar sin perder trabajo

En cada PC, entrar al repositorio correcto y revisar:

```powershell
git remote -v
git status --short
git rev-parse HEAD
```

La copia debe estar limpia y la base debe coincidir con el `LEEME`/manifiesto del paquete. Si cambió main o hay trabajo local, revisar la integración y regenerar el parche cuando sea necesario; no usar `reset --hard`, no forzar el parche y no reemplazar el repositorio completo a ciegas.

Con la ruta real del paquete descomprimido:

```powershell
git apply --check "C:\ruta\paquete\cambios.patch"
git apply "C:\ruta\paquete\cambios.patch"
git diff --stat
git status --short
```

Comparar con el manifiesto. Una copia de validación debe recibir los tres parches en orden y repetir los controles. Después de integrar un PR, volver a comprobar la base antes del siguiente; no asumir que un parche validado sobre otra revisión se aplica sin revisar. Los comandos de commit/push se preparan tras esta comprobación; no se ejecutan automáticamente ni se recomienda `git add .` para mezclar responsabilidades.

## Comprobar el conjunto

Backend, en su entorno y base local aislada:

```powershell
python manage.py check --settings=config.settings_test_mysql
python manage.py makemigrations --check --dry-run --settings=config.settings_test_mysql
python manage.py test --settings=config.settings_test_mysql --noinput
```

Las variables `LPN_TEST_MYSQL_*` deben señalar una instancia local dedicada; la configuración rechaza reutilizar el puerto habitual. Desde `scripts`: `python -m unittest discover -p 'test_*.py' -v`.

Desde `frontend/mobile`:

```powershell
flutter pub get
flutter analyze
flutter test --no-pub
```

Para un emulador y un backend QA local en 8016:

```powershell
flutter run --dart-define=LPN_API_BASE_URL=http://10.0.2.2:8016
```

No incluir cuentas o contraseñas dentro del APK. La demo visual usa datos ficticios en memoria y no sustituye la conexión real al backend.

## Preparar el despliegue después de integrar

1. Elegir alojamiento y revisar cuotas/costes actuales antes de crear recursos de pago. Mantener un proceso inicial y comprobar memoria/transferencia en ese host; las cifras locales no garantizan una factura cero.
2. El servicio vigente usa **`backend-panel/` como directorio raíz**. El Dockerfile de la raíz del repositorio pertenece al backend anterior y se conserva por compatibilidad; no utilizarlo accidentalmente para desplegar este panel. El contexto de construcción del panel es `backend-panel`.
3. Configurar host, origen CSRF, base nueva, usuario SQL limitado, clave secreta, clave de cifrado y volumen privado persistente. Respaldar y conservar la clave de cifrado con la base y los archivos privados.
4. Revisar `migrate --plan`, respaldo y restauración antes de aplicar migraciones al destino correcto. Este bloque de paginación no crea migraciones nuevas; los paquetes acumulados sí incluyen las anteriores pendientes de integración. No cargar datos demo en una base real.
5. Verificar HTTPS, proxy del proveedor y acceso al panel/API. La configuración existente `settings_railway` es específica de ese entorno; revisar sus supuestos si se elige otro proveedor. No copiar cabeceras de confianza sin comprobar el proxy.
6. Compilar Android con el origen HTTPS elegido, firma privada y versión acordada después de integrar. El APK debug y las capturas sirven para pruebas; no son una publicación en la tienda.

En este cierre se validó el código y sus compilaciones de app, no una construcción/publicación nueva del contenedor ni un despliegue remoto. `/api/health/` comprueba que responde el proceso; el recorrido de aceptación debe comprobar también base, login, autorización, archivos y una operación de negocio.

## Lo que sigue pendiente de publicación

La lista original mantiene 49/57 (86,0 %): privacidad/documentos y condiciones de adopción; aceptación completa de pantallas/TalkBack/teléfono físico; rendimiento en móvil/red/alojamiento; licencias, seguridad, restauración y firma. Son pendientes de aceptación comercial, no una razón para mezclar o posponer la revisión de estos commits locales.

La tienda inicia pedidos sin cobro y los aportes son compromisos; no se anuncia una pasarela real. La automatización de recuperación por correo y otros pendientes operativos deben validarse en su alcance antes de ofrecerlos. No se declara el producto listo para vender por pasar pruebas locales.
