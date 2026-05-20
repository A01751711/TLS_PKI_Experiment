@echo off
REM run.bat - Execute the complete TLS PKI experiment pipeline on Windows

echo.
echo ============================================================================
echo  TLS PKI Experiment - TLS 1.3 Handshake Measurement
echo ============================================================================
echo.

python scripts/main.py
if errorlevel 1 (
    echo Error en la ejecucion. Abortando.
    exit /b 1
)

echo.
echo ============================================================================
echo  Experimento completado exitosamente!
echo  Resultados disponibles en la carpeta de timestamp mas reciente
echo ============================================================================
echo.

