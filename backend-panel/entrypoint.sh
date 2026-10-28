#!/bin/sh
set -eu
# Railway monta el volumen después de construir la imagen. Preparar únicamente
# el directorio privado y ejecutar el servidor sin privilegios de root.
if [ "$(id -u)" = "0" ]; then
    : "${LPN_PRIVATE_ROOT:?Configure el directorio privado persistente}"
    mkdir -p "$LPN_PRIVATE_ROOT"
    chown app:app "$LPN_PRIVATE_ROOT"
    chmod 700 "$LPN_PRIVATE_ROOT"
    exec gosu app "$@"
fi
exec "$@"
