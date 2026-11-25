# Bloque 3 — Validación, evidencia y paquetes para tres integrantes

Actualización posterior: V02 se cerró en la guía 86. El estado y los paquetes de este documento son el cierre histórico de 48/57; la versión de trabajo posterior está documentada allí.

Fecha: 25 de noviembre de 2026. Repositorio de destino: `Jce-C/Little-paws-net-backend-`. Se conserva el HEAD local `795c413` como base; no se crearon commits, ramas ni push.

## Verificación local

- Backend: 468 pruebas integrales aprobadas, con 11 focales de los fallos encontrados.
- Cliente canónico: 301 pruebas integrales aprobadas y nueve optativas omitidas; 32 focales finales aprobadas después del ajuste de navegación y dos pruebas adicionales de carga→vacío. Estas últimas comprueban una sola petición y la resolución del estado a texto normal/ampliado.
- Demo: 401 pruebas aprobadas al habilitar las capturas optativas; dos pruebas de carga→vacío ejecutadas después. Web: 32 focales y dos de estados aprobadas.
- Análisis sin observaciones en las tres copias. APK debug y web release compilados localmente. Persiste la advertencia previa de CupertinoIcons no empaquetada; se mantiene en la auditoría global, no se silencia agregando una dependencia sin verificar su uso.
- 92 capturas, en 46 vistas/estados a escala normal y al 200 %. Ocho mosaicos. Son renderizados Flutter sintéticos, no capturas de emulador o dispositivo físico.
- Se corrigió el montaje aislado del componente de cuenta sin sesión en la prueba visual para darle el Scaffold que sí tiene en Home. No se confundió ese fallo del arnés de capturas con un fallo de la app.

Evidencia del workspace: `output/correcciones-app-2026-11-24/cierre-tres-bloques`. El nombre de carpeta conserva la fecha de inicio; este cierre ocurrió el día 25. Métricas e inventario sin secretos también están en `docs/evidencias/2026-11-25`.

## Paquetes del grupo

Se preparan parches independientes por archivos, contra el HEAD anterior. Incluyen todos los cambios locales de las áreas activas de la entrega, no solo las líneas de este último turno. No incluyen `.env`, claves, credenciales de QA, bases, medios privados, cachés ni compilados.

| Paquete | Responsable | Contenido |
|---|---|---|
| 01-jose-backend | José | Backend activo, modelos/APIs, RBAC, pruebas y configuración de ejecución de ejemplo |
| 02-sally-app-movil | Sally | Proyecto Flutter activo, pantallas, formularios, navegación, recursos y pruebas móviles |
| 03-majo-diseno-panel-documentacion | Majo | Estáticos y plantillas del panel, documentación y evidencia sanitizada |

Los archivos de las tres áreas no se superponen. Los parches pueden aplicarse por separado, pero la validación funcional corresponde al conjunto integrado. No se afirma que un estado intermedio sin los otros módulos sea una entrega completa. Los cambios de la demo web del workspace son locales y no se publican; el código de producto sigue en `frontend/mobile`.

El generador usa un índice Git temporal: no modifica el índice de trabajo. Exporta HEAD a un directorio temporal, comprueba y aplica los tres parches y compara las huellas de los archivos reconstruidos. La verificación y SHA-256 de los ZIP quedan junto a los paquetes. Antes de usarlos en otra PC hay que comprobar que la base coincide y que no hay cambios locales; si no coincide, revisar/integrar, sin usar `reset --hard` ni forzar la aplicación.

Nombres propuestos para el trabajo posterior: `fix/integracion-backend`, `feature/app-movil-integrada`, `feature/diseno-panel-y-trazabilidad`. No se crean ahora ni se usa el prefijo rechazado por el propietario. Las instrucciones de revisión/commit se incluyen en cada ZIP; ejecutar un commit o publicarlo sigue siendo un paso posterior del integrante.

## Qué se cierra y qué permanece abierto

Q06: trazabilidad por ID, ruta, componente, permiso, prueba y evidencia en las guías 76-85 y JSON de inventario. Q07: atlas y contraste visual del alcance existente con el PDF y los principios de los vídeos, incluyendo estados representativos. Q08: regresión, análisis y compilados, distinguiendo aceptación automatizada de física. Q09: paquetes por integrante y notas de integración con verificación del conjunto.

**Resultado: 48/57 unidades (84,2 %), conteo simple de esta lista.** Se acerca al 85 % pedido sin declarar terminado V02, que conserva un pendiente real. No es un porcentaje ponderado del esfuerzo ni una certificación del producto.

Pendientes completos:

1. V02: etiquetas visuales persistentes del acceso y cierre integral de tipografía; la escala común ya existe.
2. S04: necesidad/momento de adjuntos de identidad y recibo, según D02.
3. S05: minimización y tratamiento de información sensible/de terceros del hogar.
4. S08: condiciones de adopción y tratamiento informado con versiones, registro y revisión jurídica.
5. S12: carga/descarga privada, límites, retención y borrado de documentos.
6. Q01: aceptación completa en tamaños, orientación, teclado, claro/oscuro y dispositivo físico.
7. Q02: lector de pantalla, teclado/foco web y auditoría completa de accesibilidad.
8. Q03: carga/recursos/memoria representativos y presupuesto con alojamiento real; ya hay mediciones locales base.
9. Q10: puertas de publicación: auditoría de seguridad/security-audit por identificar, licencias (incluidas fotos de referencia), privacidad/derechos, respaldo/restauración, firma Android y presupuesto gratuito/VPS.

No hay publicación, cargos, cambios productivos ni datos reales añadidos. No se debe anunciar la versión como lista para vender hasta cerrar esas puertas.
