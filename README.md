# Little Paws Net — backend colaborativo

Backend Django REST Framework sobre una **base MySQL nueva**. Este repositorio se construye por funcionalidades mediante commits reales de José Carlos, María José y Sally Andrea. El repositorio anterior sirve solo como referencia; no se reutiliza su historial ni su base de datos.

## Estado

Primera etapa: estructura Django, configuración local segura y endpoint `GET /api/health/`. Los modelos de negocio, migraciones y demás APIs se incorporarán en commits posteriores. **No ejecutar `migrate` hasta que se incorpore el modelo de usuario propio.**

## Desarrollo local

En `backend/`, crear un entorno virtual e instalar `requirements.txt`. Copiar `.env.example` a `.env` y asignar claves propias; `.env` está excluido de Git. Cada integrante utilizará una base MySQL local independiente y no compartirá contraseñas.

Las responsabilidades y reglas de colaboración están en [CONTRIBUTING.md](CONTRIBUTING.md).
