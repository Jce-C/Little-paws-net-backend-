# Cómo está construido el backend y qué hace cada archivo

Esta guía explica la etapa 2 en términos de Little Paws Net. El informe del bloque 1 conserva la entrega inicial; el documento `06-cierre-etapa-2.md` recoge la ampliación posterior.

## La petición completa, con un ejemplo

Una gestora pulsa «Rechazar adopción» en el futuro panel:

1. El navegador envía una petición HTTP a una dirección de la API, con los datos de la decisión y su identificación.
2. `config/urls.py` dirige la petición al módulo correspondiente. Su `urls.py` selecciona la vista.
3. La vista verifica la autenticación. El serializador acepta los campos de esa operación y comprueba su formato.
4. El servicio consulta los permisos actuales: cuenta activa, membresía, rol, entidad custodiante y asignación individual.
5. La transacción bloquea los registros necesarios y comprueba que la solicitud siga pendiente. No basta con que estuviera pendiente cuando se dibujó el botón.
6. Django guarda el estado y el historial en MySQL. Si falla una condición, se revierte la transacción y no se guarda una decisión a medias.
7. La API devuelve JSON. El frontend actualizará la pantalla con el resultado. El mismo backend podrá atender a la aplicación móvil.

El navegador muestra la interfaz. Django toma la decisión de acceso. MySQL conserva los datos. Estas responsabilidades son distintas.

## Los archivos principales de seguridad

Todos estos archivos están dentro de `backend-panel/seguridad/`.

| Archivo | Qué significa y para qué sirve |
| --- | --- |
| `__init__.py` | Indica que la carpeta es un paquete de Python. Puede estar vacío; no es una pantalla ni una tabla. |
| `apps.py` | Registra el módulo de seguridad como una aplicación interna de Django. |
| `models.py` | Describe las tablas nuevas: responsables, transferencias, asignaciones, auditoría, propuestas de cuentas, excepciones, documentos, enmiendas, versiones y reclamaciones. Los modelos representan datos; no conceden acceso por existir. |
| `politicas.py` | Lista los códigos de operación que el servidor reconoce, sus alcances y las plantillas de roles. Una fila inventada desde el panel no crea una operación ejecutable. |
| `autorizacion.py` | Decide si una persona puede hacer algo. `tiene_base` comprueba el rol y permiso; `puede` añade el contexto; `exigir` interrumpe la operación si falta autorización. Consulta la base actual, por lo que una revocación no espera a que venza el token. |
| `objetos.py` | Averigua a qué entidad pertenece realmente una solicitud, aporte, pedido o fondo. Evita confiar en una entidad que el cliente podría enviar cambiada. |
| `servicios.py` | Realiza las operaciones administrativas: integrantes, cargos, responsables, transferencias y asignaciones. Coordina los bloqueos y escribe auditoría. |
| `serializers.py` | Define los campos administrativos admitidos y su validación. Por ejemplo, crear un usuario admite contraseña, pero no permite que el cliente se marque como superusuario. La contraseña se guarda como hash y no se devuelve. |
| `views.py` | Recibe las peticiones administrativas y construye sus respuestas. Conecta las entradas validadas con los servicios y permisos. |
| `urls.py` | Publica las direcciones administrativas bajo `/api/seguridad/` e incluye los recorridos de negocio. |
| `flujos.py` | Implementa los recorridos restantes: preparar/aprobar cuentas, accesos excepcionales, enmiendas, correcciones, publicidad, verificaciones y reclamaciones. Cada acción tiene comprobaciones específicas; no hay un cambio libre de cualquier estado. |
| `flujos_serializers.py` | Describe los formularios de entrada de esos recorridos. Limita fechas, importes, texto, identificadores y campos aceptados. |
| `flujos_views.py` | Ofrece la API de esos recorridos. Selecciona los datos que cada actor puede consultar y aplica `no-store` a las respuestas privadas. |
| `flujos_urls.py` | Agrupa esas rutas bajo `/api/seguridad/operaciones/`. Su ubicación no convierte todas las operaciones en funciones exclusivas de administradores: cada una comprueba su actor y alcance. |
| `documentos.py` | Guarda y localiza los archivos privados con nombres aleatorios fuera de las rutas públicas. Acepta PDF, PNG y JPEG, con límite de 10 MB y comprobación inicial del formato. La descarga pasa por autorización. |
| `tests.py` | Prueba la administración, la separación entre entidades, las transferencias, las revocaciones y las asignaciones iniciales. |
| `tests_flujos.py` | Prueba las aprobaciones, documentos, excepciones, enmiendas, versiones, reclamaciones y concurrencia de los nuevos recorridos. No forma parte de la interfaz. |
| `management/commands/iniciar_seguridad.py` | Comando para inicializar explícitamente al primer Administrador de seguridad. Pide la contraseña de forma oculta; no publica una cuenta por defecto. |
| `management/__init__.py`, `management/commands/__init__.py` | Permiten que Django encuentre el comando anterior. |

## Migraciones: instrucciones para evolucionar la base

Los archivos de `migrations/` se ejecutan en orden y Django registra cuáles ya se aplicaron. Crear un modelo en Python no modifica por sí solo una base existente: primero se genera la migración y después se aplica con `manage.py migrate`.

| Archivo | Cambio |
| --- | --- |
| `core/migrations/0007_recursos_y_autorizacion.py` | Añade Recursos, metadatos de permisos, estados de roles y revocación de roles de entidad. |
| `seguridad/migrations/0001_recursos_y_autorizacion.py` | Crea responsables, transferencias, asignaciones y auditoría. |
| `seguridad/migrations/0002_catalogo_seguridad.py` | Carga las plantillas iniciales y deshabilita los roles amplios sustituidos, conservando asignaciones históricas. |
| `seguridad/migrations/_catalogo_v1.py` | Copia fija del catálogo que utiliza la migración 0002. No es una migración independiente. Conserva la definición histórica aunque cambie `politicas.py`. |
| `seguridad/migrations/0003_asignaciones_fondo.py` | Permite asignar varios gestores a un fondo. |
| `seguridad/migrations/0004_flujos_etapa_dos.py` | Crea los modelos de los recorridos adicionales. |
| `seguridad/migrations/0005_estados_flujos.py` | Añade los estados Retirada, Correcciones y Con dueño. |
| `seguridad/migrations/0006_catalogo_flujos.py` | Añade permisos de cuentas receptoras y reclamaciones sin reemplazar personalizaciones existentes de otros roles. El principal puede autorizar atención veterinaria en custodia; esto no le concede lectura ni escritura clínica. |
| `migrations/__init__.py` | Hace reconocible el paquete de migraciones. |

Las migraciones no crean administradores, no deciden quién eres y no reactivan usuarios de demostración. No deben borrarse para «reiniciar» una base con información.

## Otros archivos del proyecto que participan

| Ubicación | Función |
| --- | --- |
| `backend-panel/manage.py` | Entrada de comandos: comprobaciones, migraciones, pruebas y servidor de desarrollo. |
| `backend-panel/config/settings.py` | Activa módulos y configura base, autenticación, zona horaria y almacenamiento privado. Lee las credenciales locales; no contiene una contraseña pública de acceso. |
| `backend-panel/config/urls.py` | Mapa principal de rutas del proyecto, incluido Django Admin técnico y las API de negocio. |
| `backend-panel/config/settings_test_mysql.py` | Configuración para ejecutar pruebas en otra instancia MySQL y otro puerto. Evita usar la base habitual como base de pruebas. |
| `backend-panel/core/models.py` | Tablas compartidas del negocio, entidades, usuarios por entidad, roles, permisos y recursos. |
| `backend-panel/core/api.py` | Catálogos, publicidad aprobada visible y notificaciones. Incorpora las versiones aprobadas nuevas a la consulta pública de publicidad. |
| `backend-panel/core/crypto.py` | Cifrado y descifrado de números de cuenta y referencias privadas con la clave local. |
| `backend-panel/accounts/serializers.py` | Registro de cuentas y validación de sus datos. El registro público concede únicamente el rol Ciudadano. |
| `backend-panel/adoption/services.py` | Resolución de adopciones con custodia, asignación y estado vigentes. Comparte el orden de bloqueo con retirada/edición para evitar decisiones incompatibles. |
| `backend-panel/animals/services.py` | Autorización veterinaria, QR y anotaciones. Un QR válido no concede por sí solo acceso clínico. |
| `backend-panel/rescue/services.py`, `rescue/views.py` | Aceptación y consulta de rescates respetando el rol y la fundación. |
| `backend-panel/rescue/sponsorship.py`, `sponsorship_views.py` | Compromisos, consulta de cuenta y confirmaciones. La ruta histórica de publicación directa de cuentas sigue cerrada para que no omita la aprobación. |
| `backend-panel/funds/api.py` | Registro informativo de distribuciones, sujeto a permiso y asignación al fondo. No ejecuta transferencias bancarias. |
| `backend-panel/core/management/commands/seed_demo.py` | Carga datos sintéticos para demostraciones y pruebas. Rechaza reactivar cuentas demo dadas de baja. |
| `backend-panel/core/management/commands/verify_demo.py` | Comprueba los recorridos sintéticos existentes con las nuevas asignaciones. |
| `backend-panel/requirements.txt` | Dependencias Python fijadas del backend. |
| `.gitignore` | Excluye secretos, entornos, archivos privados y artefactos locales del seguimiento de Git. |
| `docs/rbac/` | Reglas aprobadas, matriz, plan técnico e informes. Documentar una función no significa que ya esté implementada; debe revisarse el estado del informe correspondiente. |

La separación previa de las antiguas `api.py` de cuentas, animales y rescates en `views.py`, `serializers.py` y `urls.py` ya estaba en el espacio de trabajo. Se preservó y se integró con ella; no es un frontend nuevo.

## Qué tecnologías usamos y cómo se comportan

Las versiones instaladas están fijadas en `requirements.txt`.

| Tecnología | Papel en Little Paws Net |
| --- | --- |
| **Python** | Lenguaje en el que están escritas las reglas y el servidor. El navegador no ejecuta estos archivos Python. |
| **Django 5.2.18** | Organiza módulos, usuarios, configuración, modelos, migraciones y transacciones. Su ORM convierte operaciones de modelos en consultas SQL parametrizadas. |
| **Django REST Framework 3.18.3** | Facilita las API HTTP, serializadores, validación, permisos y respuestas JSON que consumirán web y móvil. No diseña por sí solo el panel. |
| **Simple JWT 5.5.1** | Identifica al usuario de la API mediante tokens firmados. El access token actual dura 15 minutos; la renovación tiene rotación y lista de revocación. El token no contiene una autorización permanente a todos los recursos: se comprueban los accesos actuales. |
| **MySQL 8** | Guarda usuarios, entidades, relaciones e historiales. Las transacciones y bloqueos impiden, por ejemplo, que dos revisores se adjudiquen simultáneamente el mismo trabajo. |
| **mysqlclient 2.3.0** | Conector que permite a Django comunicarse con MySQL. |
| **cryptography 50.0.2 / Fernet** | Cifra datos bancarios para poder recuperarlos solo mediante la clave y una operación autorizada. Esto es diferente del hash de una contraseña: la contraseña se compara, no se descifra para mostrarla. |
| **python-dotenv 1.2.4 y `.env` local** | Cargan la configuración privada del entorno. El archivo `.env` y las claves quedan fuera de Git. |
| **HTTP y JSON** | Son el medio de comunicación y el formato de datos entre el frontend y el backend. Un endpoint es una dirección que acepta una operación concreta. |
| **Pruebas Django sobre otro MySQL** | Ejecutan escenarios permitidos y rechazados con datos sintéticos; también se usan hilos y conexiones separadas para comprobar competencia entre operaciones. |

RBAC es el modelo de acceso por roles; no es una librería adicional instalada. Aquí se combina con relaciones y condiciones: dueño, entidad, asignación, custodia, estado y expiración. Por eso «tener un rol» no basta en todos los recorridos.

## Qué vendrá en la etapa 3

Se conectará el acceso web al backend existente: inicio y cierre de sesión, captcha aritmético básico, límites de intentos, errores y consulta de los accesos del usuario. Si se utilizan sesiones del navegador, se aplicará CSRF. Se concretará el contrato web antes de guardar credenciales o tokens en el cliente.

El captcha de una suma no es una defensa suficiente contra DDoS. Los límites de intentos, la infraestructura y la protección del despliegue son controles diferentes.

El backend sigue en `backend-panel/`. El código del futuro panel puede vivir en `frontend-admin/` dentro del mismo repositorio privado. La aplicación móvil podrá vivir en `mobile/`. Web y móvil compartirán la API y las reglas, no necesitan compartir necesariamente los mismos componentes visuales. La etapa 4 del boceto de Figma sigue separada.
