# 68. Revisión de pantallas, navegación y aceptación pendiente

Fecha: 22 de noviembre de 2026. Trabajo local, sin commits en el repositorio oficial ni despliegues o migraciones de Railway.

## Cambios resultantes

- Tienda: fotografía a la izquierda, nombre/precio/existencias a la derecha; composición vertical en anchura reducida o texto ampliado. Un botón principal fijo. Total COP decimal exacto; el comprobante usa el total guardado por el servidor, no un cálculo supuesto del cliente. Preparar un pedido no cobra ni reserva existencias.
- Acceso: composición y colores de los SVG del usuario, fotos recortadas originales y marca de agua de bienvenida conservada por instrucción expresa. Olas vectoriales dibujadas en código. Versión compacta con formulario accesible y acción fija; sin peticiones de datos al escribir o abrir un acceso sin sesión guardada.
- Inicio: atajos circulares con destinos reales, textos más breves, decoración detrás del contenido.
- Expediente: retrato pequeño junto al nombre; disposición vertical con texto grande, información clínica privada y sin una nueva URL pública. La autorización precede al retrato; retirarlo o cambiar de custodio invalida su inclusión.
- Reporte: Situación → Ubicación → Revisión y contacto. Validación por paso, volver conserva el borrador, salida con confirmación. No envía reportes intermedios. Respuesta incierta bloquea reenvíos accidentales.
- Acciones: las tarjetas usan una indicación con texto, flecha y separador; el pie fijo no añade una cápsula alrededor del botón. Se conservan chips para filtros/elecciones y estados con significado.
- Navegación: botón central elevado contextual; cápsula con un único desenfoque acotado y tinte oscuro legible. La selección se desplaza durante 260 ms. Entrada de contenido de 220 ms sin conservar una segunda vista privada saliente. Movimiento reducido omite las animaciones y transparencia reducida/alto contraste usan fondo opaco. Es una adaptación Flutter inspirada en vidrio; no utiliza la API nativa de Apple ni simula refracción física.
- Textos de interfaz: se retiró el separador decorativo de punto medio de las cadenas del cliente y de sus datos de demostración.

## Revisión visual reproducible

`test/visual_inventory_test.dart` del proyecto de demostración compone 34 vistas con los widgets reales y datos ficticios del adaptador de la demo. Se prueban a 390×884 con escala 1 y a 320×640 con escala 2. También recorre el contenido diferido vertical hasta ocho tramos de 400 px. Son 68 casos de layout, no 68 pruebas de integración con producción.

Los PNG son renders de pruebas de widgets, no capturas del emulador o navegador. El directorio de salida se pasa por `--dart-define=LPN_VISUAL_QA_DIR=RUTA_ABSOLUTA`; no hay rutas personales obligatorias en el test.

Criterios aplicados: título de página, contexto breve, datos principales destacados, una acción principal identificable, acciones secundarias de menor peso, texto sin alturas fijas, efectos decorativos sin capturar interacción, controles con semántica y área táctil, y preferencias de accesibilidad conservadas.

### Vistas renderizadas

adoptar, aporte, ayudas, bienvenida, comunidad, consulta-privada, convocatoria, cuenta, directorio, editar-convocatoria, expediente, foto-perfil, gestionar-ayudas, historias, inicio, login, mascota, mensaje, mis-mascotas, mis-reportes, notificaciones, organizacion, pedido, perfil, producto, qr, registro, reporte, reporte-detalle, reporte-recibido, rescates, solicitud-nueva, solicitudes, tienda.

### Inventario de pantallas públicas del cliente

La misma clase puede tener distintas variantes (por ejemplo lista de productos/organizaciones y login/registro). Home aloja las cuatro pestañas; no constituye un módulo adicional del backend.

| Clase | Archivo |
| --- | --- |
| CatalogScreen | `frontend/mobile/lib/adoption/adoption_screens.dart` |
| PetScreen | `frontend/mobile/lib/adoption/adoption_screens.dart` |
| RequestDialog | `frontend/mobile/lib/adoption/adoption_screens.dart` |
| RequestsScreen | `frontend/mobile/lib/adoption/adoption_screens.dart` |
| AccountScreen | `frontend/mobile/lib/auth/account_screen.dart` |
| LoginScreen | `frontend/mobile/lib/auth/account_screen.dart` |
| ProfileScreen | `frontend/mobile/lib/auth/profile_screen.dart` |
| AvatarScreen | `frontend/mobile/lib/auth/public_avatar.dart` |
| WelcomeScreen | `frontend/mobile/lib/design/welcome_screen.dart` |
| CommunityScreen | `frontend/mobile/lib/explore/community_screen.dart` |
| ExploreScreen | `frontend/mobile/lib/explore/explore_screens.dart` |
| HelpScreen | `frontend/mobile/lib/explore/explore_screens.dart` |
| PublicListScreen | `frontend/mobile/lib/explore/explore_screens.dart` |
| ProductScreen | `frontend/mobile/lib/explore/explore_screens.dart` |
| OrderScreen | `frontend/mobile/lib/explore/explore_screens.dart` |
| ContributionScreen | `frontend/mobile/lib/explore/explore_screens.dart` |
| ManageHelpScreen | `frontend/mobile/lib/explore/help_management.dart` |
| OrganizationHelpScreen | `frontend/mobile/lib/explore/help_management.dart` |
| HelpProgramEditor | `frontend/mobile/lib/explore/help_program.dart` |
| PublicMessageScreen | `frontend/mobile/lib/explore/message_composer.dart` |
| OrganizationDetailScreen | `frontend/mobile/lib/explore/organization_public_info.dart` |
| NotificationsScreen | `frontend/mobile/lib/notifications/notifications_screen.dart` |
| OwnedPetsScreen | `frontend/mobile/lib/pets/owned_pets_screens.dart` |
| PetMedicalRecordScreen | `frontend/mobile/lib/pets/owned_pets_screens.dart` |
| PetQrScreen | `frontend/mobile/lib/pets/pet_qr_screen.dart` |
| AnonymousReportScreen | `frontend/mobile/lib/rescue/anonymous_report_screen.dart` |
| RescueScreen | `frontend/mobile/lib/rescue/rescue_screens.dart` |
| CommunityReportsScreen | `frontend/mobile/lib/rescue/rescue_screens.dart` |
| ReportDetailScreen | `frontend/mobile/lib/rescue/rescue_screens.dart` |
| MyReportsScreen | `frontend/mobile/lib/rescue/rescue_screens.dart` |
| ReportFormScreen | `frontend/mobile/lib/rescue/rescue_screens.dart` |
| ReportReceiptScreen | `frontend/mobile/lib/rescue/rescue_screens.dart` |

## Trazabilidad de esta revisión

| Necesidad | Implementación | Verificación |
| --- | --- | --- |
| Compra clara | `explore/cop_amount.dart`, `product_presentation.dart`, `commerce/api.py` | `store_presentation_test`, recorrido HTTP en `commerce.tests_acceptance_http` |
| Acceso fiel al SVG | `design/access_reference.dart`, `welcome_screen.dart`, assets/access | `reference_access_test`, acceso/responsive y renders |
| Reporte breve | `rescue/rescue_screens.dart` | `report_wizard_test`, `rescue_test` |
| Retrato privado | `animals/medical_thumbnail.py`, rama expediente de `seguridad/flujos_views.py` | `animals.tests_medical_thumbnail`, límites del parser y pruebas de revocación de sesión |
| Vidrio y navegación | `design/lpn_navigation.dart`, `main.dart` | `navigation_glass_test`, navegación contextual y reducción de efectos |
| Legibilidad general | superficies y textos compartidos | inventario visual 68 casos y regresión completa del cliente |
| RBAC vivo | autorización y menú existentes | recorrido real HTTP/JWT/SQL: conceder, renombrar recurso, revocar y comprobar dos cuentas |

## Lo que aún impide cerrar el punto 14

La regresión automática, los renders y la compilación local no reemplazan aceptación manual. Falta probar esta versión en dispositivo/emulador real, TalkBack y teclado, medir fluidez en un móvil de prestaciones limitadas y verificar cliente y backend completos en el entorno de integración acordado con dos sesiones abiertas. Las herramientas de control visual estaban desconectadas en esta sesión; no se presenta esa validación como realizada.

El recorrido HTTP con SQL sí comprueba la autorización real y la revocación inmediata en el servidor; la demo navegable usa datos ficticios y no demuestra conexión a Railway ni publicación real de pedidos. No usar cuentas reales en ella.

Estado: 13/14 puntos cerrados en implementación (92,86 %); punto 14 parcialmente validado, sin declararlo terminado.


## Resultado comprobado del cierre
244 pruebas del cliente, 317 de la demo (incluyen 68 layouts), 210 del backend aislado. Análisis estático sin incidencias. Web release y APK debug compilados. Demo v16 publicada: https://little-paws-mobile-demo.e-rios48.chatgpt.site/ . La publicación de demo no modifica Railway ni el repositorio oficial.
