# Medición HTTP local de reportes paginados

Fecha: 20 de noviembre de 2026. Servicio QA en `127.0.0.1:8016`, MySQL local aislado, Django en modo debug y datos sintéticos ya existentes. No se crean reportes, solicitudes, QR ni cuentas.

## Qué se midió

El medidor añade `--reportes`, conservando el ensayo anterior de catálogo/login. Consulta primera página, búsqueda `QA` y segunda página cuando existe cursor. Por ruta ejecuta un calentamiento excluido, seis lecturas secuenciales y cuatro simultáneas. Incluyendo la lectura inicial, consume como máximo 34 GET: no se eleva ni desactiva el límite del servidor para medirlo.

Se rechazan redirecciones y rutas ajenas al ensayo. Cada respuesta se acota a 1 MiB. Una prueba con un servidor HTTP sintético de loopback comprueba que no se sigue el destino de una redirección, que se rechaza un cuerpo excesivo y que las rutas rechazadas no generan tráfico.

## Resultado observado

| Ruta | Mediana secuencial | Máximo secuencial | Máximo con 4 clientes | Cuerpo |
|---|---:|---:|---:|---:|
| Primera página, 20 filas | 19,53 ms | 33,35 ms | 45,21 ms | 2.808 bytes |
| Búsqueda `QA` | 14,65 ms | 36,12 ms | 54,57 ms | 335 bytes |
| Segunda página | 13,44 ms | 39,49 ms | 47,76 ms | 1.283 bytes |

La primera muestra de esta ejecución tardó 35,46 ms. No representa un arranque frío del proceso: el servicio ya estaba activo. El JSON registra también tiempo hasta cabeceras y p95 por rango más cercano; con seis/cuatro observaciones ese p95 coincide con el máximo y no aporta una estimación estadística estable.

Estos datos no incluyen TLS, red del usuario, Railway, descarga de imágenes ni dibujo Android. No son una prueba de carga y no predicen la latencia de producción. El conjunto sintético es pequeño; una búsqueda `icontains` sobre una base grande necesita otra evaluación. La espera de 400 ms del buscador Android agrupa pulsaciones y es independiente del tiempo HTTP medido.

## Repetición

Con el servicio QA aislado ya iniciado y sin otro ensayo que consuma su límite anónimo, ejecutar desde la raíz:

```powershell
python scripts/medir_rendimiento_local.py --reportes
python -m unittest discover -s scripts -p test_medir_rendimiento_local.py -v
```

El primer comando crea `output/rendimiento-local-reportes.json`. No admite una URL remota como argumento. No seguir ejecutándolo en bucle: las lecturas reales sí consumen el presupuesto de 60/minuto por IP del servicio público.

Evidencia del ensayo: `output/rendimiento-local-reportes.json` y `output/adopcion-movil/medidor-reportes-barreras-20261120.log`. La comprobación del medidor usa únicamente un servidor HTTP temporal de loopback; no escribe en MySQL. No se repiten las suites Django/Flutter ni se recompila el APK, porque este bloque modifica herramientas/documentación, no la app ni su autorización.

## Reparto y continuidad

José Carlos recibe medidor y prueba de barreras. Sally recibe informe/evidencias. María José conserva Android sin cambios y el APK de 138 pruebas del bloque previo. Todo queda local y sin commits. Pendientes: medir en un dispositivo físico y en un entorno de preproducción autorizado, con red real, datos representativos, caché compartida y objetivos de rendimiento acordados.
