#!/bin/bash
# run.sh - Execute the complete TLS PKI experiment pipeline on Linux/macOS

set -e

echo ""
echo "============================================================================"
echo " TLS PKI Experiment - Recoleccion y Analisis"
echo "============================================================================"
echo ""

echo "[1/2] Recolectando datos de mediciones TLS 1.3..."
python3 scripts/01_collect_data.py

echo ""
echo "[2/2] Analizando resultados y generando graficas..."
python3 scripts/02_analyze_results.py

echo ""
echo "============================================================================"
echo " Experimento completado exitosamente!"
echo " Resultados disponibles en: results/"
echo "============================================================================"
echo ""

