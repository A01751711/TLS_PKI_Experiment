@echo off
REM run.bat - Execute the complete TLS PKI experiment pipeline on Windows

echo.
echo ============================================================================
echo  TLS PKI Experiment - Recoleccion y Analisis
echo ============================================================================
echo.

echo [1/2] Recolectando datos de mediciones TLS 1.3...
python scripts/01_collect_data.py
if errorlevel 1 (
    echo Error en recoleccion de datos. Abortando.
    exit /b 1
)

echo.
echo [2/2] Analizando resultados y generando graficas...
python scripts/02_analyze_results.py
if errorlevel 1 (
    echo Error en analisis. Abortando.
    exit /b 1
)

echo.
echo ============================================================================
echo  Experimento completado exitosamente!
echo  Resultados disponibles en: results/
echo ============================================================================
echo.

