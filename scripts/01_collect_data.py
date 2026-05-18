#!/usr/bin/env python3
"""
01_collect_data.py

Recolección de datos de mediciones TLS 1.3 contra sitios HTTPS reales.

Realiza:
1. Verificación de dependencias (Python, OpenSSL)
2. Detección/descarga de CA bundle
3. Inspección de cadenas de certificados
4. Medición de latencia de handshake (múltiples repeticiones)
5. Exportación de datos crudos a CSV

Genera:
- data/raw_web_results.csv (todos los handshakes)
- data/chains_detectadas.csv (resumen de cadenas)
- data/fallos.csv (errores)
- logs/ (detalles de OpenSSL)

Uso:
    python scripts/01_collect_data.py
"""

import csv
import shutil
import socket
import ssl
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    log, ok, warn, die, hdr,
    find_ca_bundle, download_ca_bundle,
    setup_ca_bundle,
    openssl_run, extract_pem_certs, pem_to_der_size, cert_subject,
    server_cert_algorithm, build_s_client_cmd, verify_openssl,
    create_ssl_context
)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Target websites for TLS measurement
# In real internet, you cannot force RSA or ECDSA - servers decide.
# Script detects what is presented.
TARGETS = [
    {"label": "example",       "host": "example.com",       "port": 443},
    {"label": "cloudflare",    "host": "cloudflare.com",    "port": 443},
    {"label": "google",        "host": "google.com",        "port": 443},
    {"label": "github",        "host": "github.com",        "port": 443},
    {"label": "microsoft",     "host": "microsoft.com",     "port": 443},
    {"label": "amazon",        "host": "amazon.com",        "port": 443},
    {"label": "wikipedia",     "host": "wikipedia.org",     "port": 443},
    {"label": "mozilla",       "host": "mozilla.org",       "port": 443},
    {"label": "stackoverflow", "host": "stackoverflow.com", "port": 443},
    {"label": "openai",        "host": "openai.com",        "port": 443},
]

REPETITIONS      = 1000
TIMEOUT_SECONDS  = 10
TLS_VERSION_FLAG = "-tls1_3"

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
CERTS_DIR = DATA_DIR / "certs_extraidos"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CERTS_DIR.mkdir(parents=True, exist_ok=True)

RAW_CSV       = DATA_DIR / "raw_web_results.csv"
CHAINS_CSV    = DATA_DIR / "chains_detectadas.csv"
FAILURES_CSV  = DATA_DIR / "fallos.csv"

# =============================================================================
# STEP 0: Verify Dependencies
# =============================================================================

hdr("0. Verificar dependencias")

ok(f"Python {sys.version.split()[0]}")

if not verify_openssl():
    die("openssl no encontrado en PATH.")

res = subprocess.run(["openssl", "version"], capture_output=True, text=True)
ok(f"OpenSSL: {res.stdout.strip()}")

# =============================================================================
# STEP 1: Setup CA Bundle and Verification Mode
# =============================================================================

hdr("1. Configurar verificación de certificados")

VERIFY_ARGS, VERIFY_MODE = setup_ca_bundle()

# Try to find CA bundle for reference
CA_BUNDLE = None
if VERIFY_MODE == "CAfile":
    ca_bundle = find_ca_bundle()
    if ca_bundle:
        CA_BUNDLE = ca_bundle
        ok(f"CA bundle: {CA_BUNDLE}")

# =============================================================================
# STEP 2: Initialize CSV Files
# =============================================================================

hdr("2. Inicializar archivos de datos")

# Raw results
with open(RAW_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([
        "label", "host", "port", "repetition", "latency_ms",
        "detected_depth", "cert_count", "server_cert_algorithm",
        "chain_size_pem_bytes", "chain_size_der_bytes",
        "tls_version", "verify_mode", "returncode",
    ])
ok(f"Inicializado: {RAW_CSV}")

# Chains summary
with open(CHAINS_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([
        "label", "host", "port",
        "detected_depth", "cert_count", "server_cert_algorithm",
        "chain_size_pem_bytes", "chain_size_der_bytes",
        "subjects",
    ])
ok(f"Inicializado: {CHAINS_CSV}")

# Failures
with open(FAILURES_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["stage", "label", "host", "port", "repetition", "error"])
ok(f"Inicializado: {FAILURES_CSV}")

# =============================================================================
# HELPERS
# =============================================================================

def write_failure(stage: str, label: str, host: str, port: int, rep: int | str, error: str):
    """Write failure record to CSV."""
    with open(FAILURES_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([stage, label, host, port, rep, str(error)])

def write_raw_row(label: str, host: str, port: int, rep: int, latency_ms: float | str,
                  chain_info: dict, returncode: int | str):
    """Write single measurement to raw results CSV."""
    with open(RAW_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            label, host, port, rep, latency_ms,
            chain_info["detected_depth"], chain_info["cert_count"],
            chain_info["server_cert_algorithm"],
            chain_info["pem_size"], chain_info["der_size"],
            "TLS1.3", VERIFY_MODE, returncode,
        ])

# =============================================================================
# STEP 3: Inspect Certificate Chains
# =============================================================================

hdr("3. Inspeccionar cadenas de certificados")

def inspect_chain(label: str, host: str, port: int) -> dict | None:
    """
    Inspect TLS 1.3 certificate chain from live server.
    Returns dict with chain metadata or None on failure.
    """
    log(f"Inspeccionando: {host}:{port}")

    try:
        proc = openssl_run(
            build_s_client_cmd(host, port, VERIFY_ARGS, TLS_VERSION_FLAG, ["-showcerts"]),
            input_data="Q\n",
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as e:
        warn(f"Timeout inspeccionando {host}")
        write_failure("inspect", label, host, port, "", str(e))
        return None
    except Exception as e:
        warn(f"Error inspeccionando {host}: {e}")
        write_failure("inspect", label, host, port, "", str(e))
        return None

    full_output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    (LOGS_DIR / f"inspect_{label}.log").write_text(full_output, encoding="utf-8", errors="ignore")

    pems = extract_pem_certs(full_output)

    # Fallback: try without verification if first attempt failed
    if not pems and VERIFY_MODE != "insecure":
        warn(f"No se extrajo cadena; probando fallback...")
        try:
            fallback_cmd = [
                "s_client",
                "-connect", f"{host}:{port}",
                "-servername", host,
                TLS_VERSION_FLAG,
                "-nocommands",
                "-verify", "0",
                "-showcerts",
            ]
            proc2 = openssl_run(fallback_cmd, input_data="Q\n", timeout=TIMEOUT_SECONDS)
            full_output2 = (proc2.stdout or "") + "\n" + (proc2.stderr or "")
            (LOGS_DIR / f"inspect_{label}_fallback.log").write_text(full_output2, encoding="utf-8", errors="ignore")
            pems = extract_pem_certs(full_output2)
        except Exception as e:
            write_failure("inspect_fallback", label, host, port, "", str(e))

    if not pems:
        warn(f"No pude extraer certificados de {host}.")
        write_failure("inspect", label, host, port, "", "no PEM certificates extracted")
        return None

    # Parse chain metadata
    subjects = [cert_subject(p) for p in pems]
    pem_size = sum(len((p + "\n").encode("utf-8")) for p in pems)
    der_size = sum(pem_to_der_size(p) for p in pems)
    detected_depth = max(len(pems) - 1, 0)
    alg = server_cert_algorithm(pems[0])

    # Save individual certs
    site_dir = CERTS_DIR / f"{label}_{host.replace('.', '_')}"
    site_dir.mkdir(exist_ok=True)
    for i, pem in enumerate(pems):
        (site_dir / f"cert_{i}.pem").write_text(pem + "\n", encoding="utf-8")

    # Write to chains CSV
    with open(CHAINS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            label, host, port,
            detected_depth, len(pems), alg,
            pem_size, der_size,
            " | ".join(subjects),
        ])

    ok(f"{host}: algoritmo={alg}, certs={len(pems)}, depth={detected_depth}, DER≈{der_size}B")
    for i, s in enumerate(subjects[:2]):  # Show first 2
        log(f"  cert[{i}]: {s[:80]}")

    return {
        "label": label,
        "host": host,
        "port": port,
        "detected_depth": detected_depth,
        "cert_count": len(pems),
        "server_cert_algorithm": alg,
        "pem_size": pem_size,
        "der_size": der_size,
    }

# =============================================================================
# STEP 4: Measure TLS Handshakes
# =============================================================================

hdr("4. Medir handshakes TLS 1.3")

def measure_site(target: dict) -> list[float]:
    """
    Perform repeated TLS handshake measurements against target site.
    Returns list of latency values (ms).
    """
    label = target["label"]
    host  = target["host"]
    port  = int(target.get("port", 443))

    chain_info = inspect_chain(label, host, port)
    if chain_info is None:
        return []

    ctx = create_ssl_context(CA_BUNDLE, VERIFY_MODE)
    results = []
    client_log = LOGS_DIR / f"client_{label}.log"

    for rep in range(1, REPETITIONS + 1):
        try:
            t0 = time.perf_counter()
            raw_sock = socket.create_connection((host, port), timeout=TIMEOUT_SECONDS)
            tls_sock = ctx.wrap_socket(raw_sock, server_hostname=host)
            tls_sock.close()
            t1 = time.perf_counter()

            elapsed_ms = (t1 - t0) * 1000.0
            results.append(elapsed_ms)
            write_raw_row(label, host, port, rep, round(elapsed_ms, 3), chain_info, 0)

            with open(client_log, "a", encoding="utf-8") as f:
                f.write(f"REP {rep:4d}  {elapsed_ms:8.2f}ms\n")

            if rep % 100 == 0:
                log(f"  {host}: {rep}/{REPETITIONS} último={elapsed_ms:.1f}ms")

        except Exception as e:
            warn(f"{host} rep={rep}: {type(e).__name__}")
            write_failure("measure", label, host, port, rep, str(e))
            write_raw_row(label, host, port, rep, "TIMEOUT", chain_info, "ERROR")
            continue

    return results

# Perform measurements
for target in TARGETS:
    try:
        log(f"\nIniciando: {target['label']} → {target['host']}:{target.get('port', 443)}")
        vals = measure_site(target)
        if vals:
            import statistics
            ok(f"{target['host']}: n={len(vals)}, mediana={statistics.median(vals):.1f}ms")
        else:
            warn(f"Sin mediciones válidas para {target['host']}")
    except Exception as e:
        warn(f"Excepción en {target['label']}: {e}")
        import traceback
        traceback.print_exc()

# =============================================================================
# CONCLUSION
# =============================================================================

hdr("5. Recolección completada")

print(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  Datos recolectados exitosamente                            ║
  ╠══════════════════════════════════════════════════════════════╣
  ║  Próximo paso: ejecutar análisis                             ║
  ║    python scripts/02_analyze_results.py                      ║
  ╚══════════════════════════════════════════════════════════════╝
""")

print(f"  Directorio de datos: {DATA_DIR.resolve()}\n")
print(f"  Archivos generados:")
for f in sorted(DATA_DIR.glob("*.csv")):
    print(f"    {f.name:<40s} {f.stat().st_size:>8,} bytes")

print()
ok("Recolección de datos completada.")

