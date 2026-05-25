@echo off
REM run.bat - Ejecuta el experimento TLS PKI completo en Windows

echo.
echo ============================================================================
echo  Experimento TLS PKI - Medicion de handshakes TLS 1.3
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

