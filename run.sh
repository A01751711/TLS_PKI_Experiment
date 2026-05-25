#!/bin/bash
# run.sh - Ejecuta el experimento TLS PKI completo en Linux/macOS

set -e

echo ""
echo "============================================================================"
echo " Experimento TLS PKI - Medicion de handshakes TLS 1.3"
echo "============================================================================"
echo ""

python3 scripts/main.py

echo ""
echo "============================================================================"
echo " Experimento completado exitosamente!"
echo " Resultados disponibles en la carpeta de timestamp mas reciente"
echo "============================================================================"
echo ""

