#!/usr/bin/env python3
"""
verify_environment.py

Verify that the environment is properly set up for the experiment.
Run this BEFORE executing the main scripts.

Usage:
    python verify_environment.py
"""

import sys
import shutil
import subprocess
from pathlib import Path

def check(condition: bool, message: str) -> None:
    """Print check result."""
    status = "✓" if condition else "✗"
    print(f"  [{status}] {message}")
    if not condition:
        print(f"       ↳ This is required. See README.md for installation instructions.")

print("\n" + "=" * 70)
print(" Environment Verification for TLS PKI Experiment")
print("=" * 70 + "\n")

all_ok = True

# Python version
print("Python:")
py_version = sys.version_info
check(py_version >= (3, 7), f"Python 3.7+ (found {py_version.major}.{py_version.minor})")

# OpenSSL
print("\nSystem Dependencies:")
openssl_available = shutil.which("openssl") is not None
check(openssl_available, "OpenSSL in PATH")
all_ok &= openssl_available

if openssl_available:
    try:
        result = subprocess.run(["openssl", "version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"       → {version}")
    except Exception:
        pass

# Python packages
print("\nPython Packages:")
packages = ["pandas", "matplotlib"]
for pkg in packages:
    try:
        __import__(pkg)
        check(True, f"{pkg}")
    except ImportError:
        check(False, f"{pkg}")
        all_ok = False

# Writable directories
print("\nFile System:")
project_root = Path(__file__).parent
check((project_root / "data").is_dir(), "data/ directory exists")
check((project_root / "results").is_dir(), "results/ directory exists")
check((project_root / "scripts").is_dir(), "scripts/ directory exists")

# CA Bundle
print("\nCertificate Verification:")
ca_paths = [
    project_root / "cacert.pem",
    Path.home() / ".ssl" / "cacert.pem",
]
ca_found = any(p.exists() for p in ca_paths)
if ca_found:
    check(True, "CA bundle available (or will be auto-downloaded)")
else:
    print(f"  [i] CA bundle not found locally (auto-download will attempt on first run)")

# Summary
print("\n" + "=" * 70)
if all_ok:
    print(" ✓ All checks passed! Ready to run.")
    print("\n   Execute:")
    print("     python run.bat      (Windows)")
    print("     bash run.sh         (Linux/macOS)")
else:
    print(" ✗ Some checks failed. See above for required installations.")
    print("\n   Installation help:")
    print("     pip install -r requirements.txt")
    print("     See README.md for OpenSSL installation.")

print("=" * 70 + "\n")

sys.exit(0 if all_ok else 1)

