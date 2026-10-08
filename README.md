# Little Paws Net — backend colaborativo

Backend Django REST Framework sobre una **base MySQL nueva**. Este repositorio se construye por funcionalidades mediante commits reales de José Carlos, María José y Sally Andrea. El repositorio anterior sirve solo como referencia; no se reutiliza su historial ni su base de datos.

## Estado

Incluye la estructura Django, configuración local segura, `GET /api/health/`, autenticación por correo/contraseña con JWT, el modelo compartido de roles y entidades, y `GET /api/catalogos/`. Los demás procesos se incorporan en commits posteriores. No aplicar las migraciones hasta configurar una base MySQL nueva y vacía.

## Desarrollo local

En `backend/`, crear un entorno virtual e instalar `requirements.txt`. Copiar `.env.example` a `.env` y asignar claves propias; `.env` está excluido de Git. Cada integrante utilizará una base MySQL local independiente y no compartirá contraseñas.

Las responsabilidades y reglas de colaboración están en [CONTRIBUTING.md](CONTRIBUTING.md).
