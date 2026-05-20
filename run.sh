#!/bin/bash
# run.sh - Execute the complete TLS PKI experiment pipeline on Linux/macOS

set -e

echo ""
echo "============================================================================"
echo " TLS PKI Experiment - TLS 1.3 Handshake Measurement"
echo "============================================================================"
echo ""

python3 scripts/main.py

echo ""
echo "============================================================================"
echo " Experimento completado exitosamente!"
echo " Resultados disponibles en la carpeta de timestamp mas reciente"
echo "============================================================================"
echo ""

