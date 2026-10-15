# Contribuir a Little Paws Net

Las contribuciones deben mantener la coherencia entre modelos, migraciones, validación de entrada, permisos y respuestas de la API. Los cambios de reglas de negocio requieren pruebas que cubran tanto el caso permitido como el rechazado.

## Flujo de trabajo

1. Crear una rama a partir de `main` para una funcionalidad o corrección concreta.
2. Incluir en el mismo cambio las migraciones generadas por Django, si se modifica un modelo.
3. Revisar el diff y ejecutar las comprobaciones desde `backend/`:

   ```powershell
   python manage.py check
   python manage.py makemigrations --check --dry-run
   python manage.py test --settings=config.test_settings
   ```

4. Hacer commits descriptivos y abrir un pull request que explique el alcance, las pruebas y cualquier migración o limitación pendiente.
5. Antes de integrar, comprobar el comportamiento en MySQL cuando el cambio dependa de funciones específicas de ese motor, como tipos espaciales o claves foráneas compuestas.

No incluir contraseñas privadas, tokens, claves de producción ni datos personales reales. La única excepción es `backend/.env`, preparado expresamente para una base de evaluación desechable y separada de la API publicada; permite cambios de datos únicamente allí y no debe reutilizarse en otros entornos. Las pruebas deben usar información ficticia. Las traducciones deben conservar estables las rutas, claves JSON y reglas de autorización; véase [IDIOMAS.md](backend/IDIOMAS.md).
