# Actualizar las PCs de Sally y Majo

Los seis bloques están integrados. Ya no copiar ZIP encima del repositorio: actualizar desde GitHub conserva la historia y las eliminaciones de la limpieza.

1. En la raíz de su repositorio, ejecutar `git status --short`. Si muestra cambios, conservarlos y pedir revisión antes de cambiar de rama. No usar `reset --hard`, `clean` ni `stash pop` a ciegas.
2. Con el árbol limpio, ejecutar:

```powershell
git fetch origin
git switch --track origin/entrega-panel
```

Si `entrega-panel` ya existe localmente, usar en su lugar:

```powershell
git switch entrega-panel
git pull --ff-only origin entrega-panel
```

Si Git avisa divergencia o conflicto, parar y compartir el mensaje. No forzar.

3. Comprobar `git log -1 --oneline` y `git status --short`.
4. Para entrar al panel publicado, usar su enlace y la cuenta individual. No necesitan MySQL, secretos SQL, Node o ejecutar Django en su PC para usar la web.
5. Para desarrollar, crear una rama desde esta versión y seguir README/CONTRIBUTING. No conectar pruebas automáticas a Railway.

## Respaldo de Majo

El README anterior sigue en un stash local, no en GitHub. Revisarlo con `git stash list` y `git stash show -p 'stash@{0}'` (confirmar primero cuál es el respaldo correcto). Comparar y recuperar solo texto útil en una rama separada; no aplicar el archivo completo sobre el README nuevo. Conservarlo hasta confirmar que no falta información.

## Configuración retirada

El `.env` anterior dejó de estar versionado. Guardar cualquier configuración local autorizada fuera del seguimiento y coordinar sus claves con el propietario. Las credenciales antiguas publicadas no se deben reutilizar. Nunca volver a añadir `.env` con `git add -f`.
