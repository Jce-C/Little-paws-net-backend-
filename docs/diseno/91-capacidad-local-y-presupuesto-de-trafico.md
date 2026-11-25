# 91. Capacidad local y presupuesto de tráfico

Nota posterior: la guía 92 corrige la limitación de navegación de tienda detectada aquí. Las cifras de este ensayo se conservan como evidencia histórica del contrato anterior.

25 de noviembre de 2026. Continuación Q03. Estado de la lista: **49/57 (86,0 %)**; no es un porcentaje de producto publicable. Se termina el ensayo de servidor descrito aquí, no la aceptación de rendimiento completa.

## Escenario y alcance

Se preparó una base nueva y exclusiva en la instancia MySQL local aislada, sin modificar las bases anteriores. Fixture: 1.000 mascotas disponibles con custodia, 500 productos, 250 publicaciones, ocho actores ciudadanos con diez mascotas propias cada uno. Datos y cuentas sintéticos. Windows 11, ocho procesadores lógicos, Python 3.14.7 y MySQL 8.0.46.

Uvicorn/ASGI con un proceso, DEBUG desactivado, conexión de base con CONN_MAX_AGE=0. Credenciales de prueba con PBKDF2, sin reducir el hash para acelerar el acceso. Servidor ligado exclusivamente a 127.0.0.1:8021. La memoria de este proceso incluye la preparación de fixtures y cachés; no equivale al dimensionamiento de un host de producción.

Se ejecutaron 52 recorridos breves, en etapas de uno, cuatro y ocho clientes. Cada recorrido contiene cuatro lecturas (adopciones, productos, comunidad y mascotas propias) y dos escrituras (publicación y pedido sin pago). **312 peticiones de negocio, 208 respuestas 200 y 104 respuestas 201, sin códigos inesperados.** Hubo además tres autenticaciones y siete comprobaciones de identidad/memoria de la instancia: 322 solicitudes en total.

Se verificó en MySQL el resultado: 302 publicaciones (250 iniciales más 52) y 52 pedidos. No se cobró dinero ni se escribieron datos productivos. Los tokens de las ocho cuentas ya autenticadas se preparan fuera del recorrido; la medición de contraseña se registra aparte.

## Resultado HTTP observado

| Clientes concurrentes | Peticiones de negocio | p95 | Peticiones/s durante la etapa |
|---|---:|---:|---:|
| 1 | 24 | 116,17 ms | 22,51 |
| 4 | 96 | 75,21 ms | 68,67 |
| 8 | 192 | 129,77 ms | 76,81 |

Son muestras locales cortas, con calentamiento y asignación de recursos distintas entre etapas. La etapa de cuatro clientes no demuestra que añadir clientes acelere el sistema. No son cifras de Internet, una prueba sostenida, una garantía de concurrencia ni un SLA.

Tres accesos correctos con PBKDF2: mediana **155,01 ms**, máximo 155,50 ms. Tres muestras son insuficientes para caracterizar su p99. No se recomienda debilitar contraseñas para perseguir una cifra de latencia.

## Consultas, tamaño y memoria

Al pasar de un registro a los volúmenes anteriores, el catálogo de adopción mantuvo **dos consultas SQL**, productos **una** y comunidad **trece**. No apareció crecimiento de consultas por cada fila en estas muestras. Comunidad y las vistas privadas incluyen autorización, por lo que no se comparan directamente con una vista pública simple.

La consulta de mascotas propias ampliada usa un actor con diez mascotas y devuelve la página de tres: trece consultas, 508 bytes. La muestra inicial era vacía; esto se declara para no aparentar una comparación idéntica de cardinalidad.

Productos: respuesta de 26.928 bytes. Adopciones: 4.751 bytes por página. El catálogo de productos conserva el límite existente de cien filas y no ofrece cursor: esta medición no demuestra que puedan recorrerse los 500 productos. **La paginación de tienda queda como mejora funcional pendiente**, antes de ofrecer catálogos mayores; no se cambió el contrato durante el ensayo.

Al finalizar la etapa de ocho clientes, el working set del servidor fue **114.868.224 bytes (aproximadamente 109,5 MiB)**. Son instantáneas de proceso, no máximos muestreados ni memoria Android. No incluyen MySQL, el sistema operativo o el cliente. El crecimiento entre etapas puede incluir pools/cachés/asignaciones retenidas; esta prueba breve no demuestra ausencia de fugas. El esquema sintético ocupó aproximadamente 6,6 MB en la instantánea, sin imágenes ni un historial representativo.

## Tráfico y consumo de la app

Se añadió un estimador que usa los bytes reales del recorrido y mantiene separados los supuestos. Ejemplo: una descarga web fría de **10 MB por usuario al mes** y **0,2 MB de media por recorrido** son hipótesis editables, no mediciones de transferencia del navegador.

| Supuesto de uso | Peticiones API/mes | Respuestas API | Total con las dos hipótesis anteriores |
|---|---:|---:|---:|
| 100 usuarios activos, un recorrido diario | 18.000 | 0,110 GB | 1,710 GB |
| 500 usuarios activos, tres recorridos diarios | 270.000 | 1,651 GB | 15,651 GB |

GB decimales. Las peticiones indicadas son solo las seis de API del recorrido; no cuentan peticiones de imágenes o recursos web. Tampoco se incluyen subidas, cabeceras/TLS, reintentos, correo, backups, almacenamiento, CPU o cobros mínimos. Estos usuarios diarios no se convierten automáticamente en usuarios simultáneos.

En Android, los recursos incluidos en el paquete se descargan al instalar/actualizar; después consumen red las APIs y las imágenes remotas consultadas/subidas. La demo web necesita además motor y recursos en su primera carga. El directorio compilado ocupa unos 45,7 MB y contiene variantes de motor: **no significa que cada visitante descargue todo ese directorio**. La transferencia real debe medirse en Network con caché fría y caliente. La compresión y la caché del alojamiento no se dan por configuradas por hacer esta estimación.

No se ha elegido proveedor ni asumido tarifa, cuota gratuita o coste cero. Se mantiene el uso gratuito por ahora. Al final habrá que comparar el consumo real contra cuotas vigentes y presupuestar VPS/alojamiento, base, copias y transferencias.

## Herramientas reproducibles

Requieren el entorno Python del backend y una instancia MySQL de prueba dedicada con sus variables `LPN_TEST_MYSQL_*` ya configuradas de forma privada. No copiar credenciales de producción.

1. Desde la raíz del repositorio, en Windows: `python scripts/servidor_capacidad_qa.py`. Rechaza host externo y puerto 3306, crea un esquema `lpn_capacity91_*`, migra y prepara únicamente datos sintéticos. No es una entrada de despliegue. Sus credenciales aleatorias quedan en `.private-data/capacity/credentials.json`, directorio ignorado por Git.
2. En otra terminal: `python scripts/medir_capacidad_local.py --credentials .private-data/capacity/credentials.json --out output/capacidad-local/carga-http.json`.
3. El medidor exige coincidencia de instancia y nonce antes de enviar credenciales o escrituras; no sigue redirecciones, limita rutas, cuerpos y concurrencia. Si hay respuestas inesperadas, conserva el informe y termina con error. No reintenta escrituras.
4. `python scripts/estimar_trafico_local.py --measurement output/capacidad-local/carga-http.json --out output/capacidad-local/trafico.json --cold-web-mb 10 --media-mb 0.2`.
5. Pruebas de las herramientas: desde `scripts`, `python -m unittest test_medir_capacidad_local test_medir_rendimiento_local -v`. Siete pruebas aprobadas. La preparación/ensayo real también se ejecutó con estos archivos, no solo con mocks.
6. Detener exclusivamente el proceso de servidor iniciado para esta prueba. El ensayo no elimina esquemas automáticamente; conservarlos o retirarlos manualmente solo después de identificar los esquemas QA propios.

La primera preparación reproducible omitía el permiso de participación de las cuentas ficticias y produjo 403. Se corrigió el fixture aplicando los datos de permisos previstos por la migración, sin desactivar autorización. La herramienta y sus pruebas detectan ahora explícitamente ese resultado fallido. Se conserva el ensayo rechazado para trazabilidad, separado del resultado final.

## Qué falta para cerrar Q03

- Perfil de memoria/renderizado de la app en un teléfono físico o entorno representativo; no confundir un APK debug en emulador con una medición comercial.
- Transferencias reales con caché fría/caliente y redes móviles; medir también subida/lectura de imágenes.
- Prueba sostenida y métricas del alojamiento elegido, con presupuesto aprobado. Las medidas locales no prueban las cuotas de un plan gratuito ni la factura.

No se repitieron las 468 pruebas backend ni las 363 del cliente: no cambió código de negocio o interfaz. Se conserva esa evidencia y se ejecutaron las siete pruebas pertinentes de las herramientas, migraciones aisladas y el recorrido HTTP/MySQL real.

Evidencia: `output/correcciones-app-2026-11-25/capacidad-local`, con informes sanitizados y sin credenciales. Paquetes acumulados del equipo en `capacidad-local/paquetes`, sin commits, ramas, push, despliegue ni servicios de pago.
