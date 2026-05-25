#!/usr/bin/env python3
"""
verify_environment.py

Verifica que el entorno esté listo para el experimento.
Ejecútalo ANTES de scripts/main.py, run.bat o run.sh.

Uso:
    python verify_environment.py
"""

import sys
import shutil
import subprocess
from pathlib import Path

# Consola Windows: intentar UTF-8 para mostrar ✓/✗/→
if hasattr(sys.stdout, "reconfigure"):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

def check(condition: bool, message: str) -> None:
    """Imprime el resultado de una comprobación."""
    status = "✓" if condition else "✗"
    print(f"  [{status}] {message}")
    if not condition:
        print("       ↳ Es obligatorio. Consulta README.md o INSTALLATION.md.")


print("\n" + "=" * 70)
print(" Verificación de entorno — Experimento TLS PKI")
print("=" * 70 + "\n")

all_ok = True

# Versión de Python
print("Python:")
py_version = sys.version_info
check(py_version >= (3, 7), f"Python 3.7+ (detectado {py_version.major}.{py_version.minor})")

# OpenSSL
print("\nDependencias del sistema:")
openssl_available = shutil.which("openssl") is not None
check(openssl_available, "OpenSSL en PATH")
all_ok &= openssl_available

if openssl_available:
    try:
        result = subprocess.run(["openssl", "version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"       → {version}")
    except Exception:
        pass

# Paquetes Python
print("\nPaquetes Python:")
packages = ["pandas", "matplotlib"]
for pkg in packages:
    try:
        __import__(pkg)
        check(True, pkg)
    except ImportError:
        check(False, pkg)
        all_ok = False

# Directorios
print("\nSistema de archivos:")
project_root = Path(__file__).parent
data_ok = (project_root / "data").is_dir()
results_ok = (project_root / "results").is_dir()
scripts_ok = (project_root / "scripts").is_dir()
check(data_ok, "existe el directorio data/")
check(results_ok, "existe el directorio results/")
check(scripts_ok, "existe el directorio scripts/")
all_ok &= data_ok and results_ok and scripts_ok
if not data_ok or not results_ok:
    print("       ↳ Crea carpetas vacías: mkdir data results  (o en Windows: mkdir data; mkdir results)")

# Bundle CA
print("\nVerificación de certificados:")
ca_paths = [
    project_root / "cacert.pem",
    Path.home() / ".ssl" / "cacert.pem",
]
ca_found = any(p.exists() for p in ca_paths)
if ca_found:
    check(True, "bundle CA disponible localmente")
else:
    print("  [i] Bundle CA no encontrado localmente (se intentará descargar en la primera ejecución)")

# Resumen
print("\n" + "=" * 70)
if all_ok:
    print(" ✓ Todas las comprobaciones pasaron. Listo para ejecutar.")
    print("\n   Ejecuta:")
    print("     python run.bat      (Windows)")
    print("     bash run.sh         (Linux/macOS)")
else:
    print(" ✗ Algunas comprobaciones fallaron. Revisa los mensajes anteriores.")
    print("\n   Ayuda de instalación:")
    print("     pip install -r requirements.txt")
    print("     Ver INSTALLATION.md para instalar OpenSSL.")

print("=" * 70 + "\n")

sys.exit(0 if all_ok else 1)
