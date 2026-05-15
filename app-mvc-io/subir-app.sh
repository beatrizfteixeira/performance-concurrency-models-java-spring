#!/bin/bash
# Atalho: redireciona para subir-app da raiz do repo (modulos -http).
# Prefira: ../../maquina-a/subir-app.sh mvc 800
exec "$(dirname "$0")/../../maquina-a/subir-app.sh" "$@"
