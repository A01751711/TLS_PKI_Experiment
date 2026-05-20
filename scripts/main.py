"""
tls_experiment_websites_tls13_rsa_ecdsa_comparative.py

Proyecto: Medición de handshakes TLS 1.3 contra páginas reales
Comparación: certificados RSA-2048 vs ECDSA P-256 cuando el sitio los use.

Qué hace:
- Se conecta a dominios HTTPS reales con TLS 1.3.
- Inspecciona la cadena de certificados con OpenSSL s_client -showcerts.
- Detecta profundidad de cadena.
- Detecta algoritmo del certificado del servidor: rsa2048, ecdsa_p256 u other.
- Mide latencia TCP + TLS handshake usando sockets Python.
- Guarda CSVs completos.
- Genera plots generales y comparativos RSA vs ECDSA.

Compatible con Windows + Python 3.7+ + OpenSSL en PATH.
Recomendado: tener cacert.pem junto al script.
"""

import csv
import math
import os
import platform
import re
import shutil
import socket
import ssl
import statistics
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# =============================================================================
# UI helpers
# =============================================================================

if platform.system() == "Windows":
    os.system("color")

R   = "\033[0;31m"
G   = "\033[0;32m"
Y   = "\033[1;33m"
C   = "\033[0;36m"
B   = "\033[1m"
RST = "\033[0m"

def log(msg):  print(f"{C}[•]{RST} {msg}")
def ok(msg):   print(f"{G}[✓]{RST} {msg}")
def warn(msg): print(f"{Y}[!]{RST} {msg}")
def die(msg):  print(f"{R}[✗]{RST} {msg}", file=sys.stderr); sys.exit(1)

def hdr(msg):
    bar = "═" * 64
    print(f"\n{B}{C}{bar}{RST}")
    print(f"{B}  {msg}{RST}")
    print(f"{B}{C}{bar}{RST}")

# =============================================================================
# CONFIG
# =============================================================================

# Nota:
# En sitios reales NO puedes forzar si el certificado es RSA o ECDSA.
# El script lo detecta. Puedes agregar/quitar hosts según lo que necesites.
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
# PASO 0
# =============================================================================

hdr("0. Verificar dependencias")

ok(f"Python {sys.version.split()[0]}")

if shutil.which("openssl") is None:
    die("openssl no encontrado en PATH.")

res = subprocess.run(["openssl", "version"], capture_output=True, text=True)
ok(f"OpenSSL: {res.stdout.strip()}")

SCRIPT_DIR = Path(__file__).resolve().parent

def find_ca_bundle() -> Path | None:
    candidates = [
        SCRIPT_DIR / "cacert.pem",
        Path.cwd() / "cacert.pem",
    ]
    for p in candidates:
        if p.exists() and p.stat().st_size > 10_000:
            return p

    try:
        cafile = ssl.get_default_verify_paths().cafile
        if cafile and Path(cafile).exists():
            return Path(cafile)
    except Exception:
        pass

    win_candidates = [
        Path(r"C:\Program Files\Git\usr\ssl\certs\ca-bundle.crt"),
        Path(r"C:\Program Files\Git\mingw64\etc\ssl\certs\ca-bundle.crt"),
        Path(os.environ.get("CURL_CA_BUNDLE", "___none___")),
        Path(os.environ.get("SSL_CERT_FILE", "___none___")),
    ]
    for p in win_candidates:
        if p.exists() and p.stat().st_size > 10_000:
            return p

    return None

CA_BUNDLE = find_ca_bundle()

if CA_BUNDLE:
    ok(f"CA bundle encontrado: {CA_BUNDLE}")
    VERIFY_ARGS = ["-CAfile", str(CA_BUNDLE)]
    VERIFY_MODE = "CAfile"
else:
    warn("No encontré CA bundle. Intentando descargar cacert.pem desde curl.se...")
    try:
        ca_dest = SCRIPT_DIR / "cacert.pem"
        ctx_download = ssl.create_default_context()
        with urllib.request.urlopen("https://curl.se/ca/cacert.pem", context=ctx_download, timeout=30) as r:
            ca_dest.write_bytes(r.read())
        CA_BUNDLE = ca_dest
        VERIFY_ARGS = ["-CAfile", str(CA_BUNDLE)]
        VERIFY_MODE = "CAfile"
        ok(f"CA bundle descargado: {CA_BUNDLE}")
    except Exception as e:
        warn(f"No pude descargar cacert.pem: {e}")
        warn("Modo inseguro: se medirá handshake sin verificación de certificados.")
        VERIFY_ARGS = ["-verify", "0"]
        VERIFY_MODE = "insecure"

# =============================================================================
# PASO 1: directorios
# =============================================================================

hdr("1. Crear directorios de trabajo")

timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
BASE_DIR    = Path(f"tls_web_tls13_rsa_ecdsa_{timestamp}")
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR   = BASE_DIR / "plots"
LOGS_DIR    = BASE_DIR / "logs"
CERTS_DIR   = BASE_DIR / "certs_extraidos"

for d in [RESULTS_DIR, PLOTS_DIR, LOGS_DIR, CERTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
    ok(f"Creado: {d}")

RAW_CSV       = RESULTS_DIR / "raw_web_results.csv"
SUMMARY_CSV   = RESULTS_DIR / "resumen_web_estadistico.csv"
CHAINS_CSV    = RESULTS_DIR / "chains_detectadas.csv"
ALGO_CSV      = RESULTS_DIR / "comparativo_algoritmo.csv"
FAILURES_CSV  = RESULTS_DIR / "fallos.csv"

with open(RAW_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([
        "label", "host", "port", "repetition", "latency_ms",
        "detected_depth", "cert_count", "server_cert_algorithm",
        "chain_size_pem_bytes", "chain_size_der_bytes",
        "tls_version", "verify_mode", "returncode",
    ])

with open(CHAINS_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([
        "label", "host", "port",
        "detected_depth", "cert_count", "server_cert_algorithm",
        "chain_size_pem_bytes", "chain_size_der_bytes",
        "subjects",
    ])

with open(FAILURES_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["stage", "label", "host", "port", "repetition", "error"])

# =============================================================================
# Helpers
# =============================================================================

def write_failure(stage, label, host, port, rep, error):
    with open(FAILURES_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([stage, label, host, port, rep, str(error)])

def openssl_run(args, input_data=None, timeout=TIMEOUT_SECONDS):
    return subprocess.run(
        ["openssl"] + args,
        input=input_data,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )

def extract_pem_certs(text: str) -> list[str]:
    return re.findall(
        r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
        text,
        flags=re.DOTALL,
    )

def pem_to_der_size(pem: str) -> int:
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-outform", "DER"],
            input=pem.encode("utf-8"),
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
        )
        return len(proc.stdout) if proc.returncode == 0 else 0
    except Exception:
        return 0

def cert_subject(pem: str) -> str:
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-noout", "-subject", "-nameopt", "RFC2253"],
            input=pem,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        if proc.returncode == 0:
            return proc.stdout.strip().replace("subject=", "").strip()
    except Exception:
        pass
    return "unknown"

def server_cert_algorithm(pem: str) -> str:
    """
    Clasificación del certificado del servidor.
    Objetivo del proyecto: rsa2048 vs ecdsa_p256.
    Si no cae en esos casos, regresa 'other'.
    """
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-noout", "-text"],
            input=pem,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        txt = (proc.stdout or "") + "\n" + (proc.stderr or "")

        # RSA
        rsa_bits = re.search(r"Public-Key:\s*\((\d+)\s*bit\)", txt, flags=re.I)
        if "rsaEncryption" in txt or "RSA Public-Key" in txt or "Public Key Algorithm: rsa" in txt:
            if rsa_bits and int(rsa_bits.group(1)) == 2048:
                return "rsa2048"
            if rsa_bits:
                return f"rsa{rsa_bits.group(1)}"
            return "rsa_unknown"

        # ECDSA / EC
        if "id-ecPublicKey" in txt or "Public Key Algorithm: EC" in txt:
            if "prime256v1" in txt or "secp256r1" in txt or "NIST CURVE: P-256" in txt:
                return "ecdsa_p256"
            curve = re.search(r"(?:ASN1 OID|NIST CURVE):\s*([A-Za-z0-9\-\_]+)", txt)
            if curve:
                return "ecdsa_" + curve.group(1).lower()
            return "ecdsa_unknown"

    except Exception:
        pass

    return "other"

def build_s_client_cmd(host: str, port: int, extra_flags: list[str] | None = None) -> list[str]:
    # Para inspección: NO usar -brief con -showcerts porque en algunos builds reduce demasiado la salida.
    cmd = [
        "s_client",
        "-connect", f"{host}:{port}",
        "-servername", host,
        TLS_VERSION_FLAG,
        "-nocommands",
    ]
    cmd += VERIFY_ARGS
    if extra_flags:
        cmd += extra_flags
    return cmd

# =============================================================================
# Inspección
# =============================================================================

def inspect_chain(label: str, host: str, port: int) -> dict | None:
    log(f"Inspeccionando cadena TLS 1.3: {host}:{port}")

    try:
        proc = openssl_run(
            build_s_client_cmd(host, port, ["-showcerts"]),
            input_data="Q\n",
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as e:
        warn(f"Timeout inspeccionando {host}")
        write_failure("inspect", label, host, port, "", e)
        return None
    except Exception as e:
        warn(f"Error inspeccionando {host}: {e}")
        write_failure("inspect", label, host, port, "", e)
        return None

    full_output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    (LOGS_DIR / f"inspect_{label}.log").write_text(full_output, encoding="utf-8", errors="ignore")

    pems = extract_pem_certs(full_output)

    # Fallback: sin verificación para extraer cadena si falló por CA local.
    if not pems and VERIFY_MODE != "insecure":
        warn(f"No se extrajo cadena con verificación en {host}; probando fallback -verify 0 solo para extraer certs.")
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
            write_failure("inspect_fallback", label, host, port, "", e)

    if not pems:
        warn(f"No pude extraer certificados de {host}. Revisa logs.")
        write_failure("inspect", label, host, port, "", "no PEM certificates extracted")
        return None

    subjects = [cert_subject(p) for p in pems]
    pem_size = sum(len((p + "\n").encode("utf-8")) for p in pems)
    der_size = sum(pem_to_der_size(p) for p in pems)
    detected_depth = max(len(pems) - 1, 0)
    alg = server_cert_algorithm(pems[0])

    site_dir = CERTS_DIR / f"{label}_{host.replace('.', '_')}"
    site_dir.mkdir(exist_ok=True)
    for i, pem in enumerate(pems):
        (site_dir / f"cert_{i}.pem").write_text(pem + "\n", encoding="utf-8")

    with open(CHAINS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            label, host, port,
            detected_depth, len(pems), alg,
            pem_size, der_size,
            " | ".join(subjects),
        ])

    ok(f"{host}: algoritmo={alg}, certs={len(pems)}, depth={detected_depth}, DER≈{der_size}B")
    for i, s in enumerate(subjects):
        log(f"  cert[{i}]: {s[:90]}")

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
# Medición
# =============================================================================

def make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    if CA_BUNDLE:
        ctx.load_verify_locations(str(CA_BUNDLE))

    if VERIFY_MODE == "insecure":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    return ctx

def write_raw_row(label, host, port, rep, latency_ms, chain_info, returncode):
    with open(RAW_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            label, host, port, rep, latency_ms,
            chain_info["detected_depth"], chain_info["cert_count"],
            chain_info["server_cert_algorithm"],
            chain_info["pem_size"], chain_info["der_size"],
            "TLS1.3", VERIFY_MODE, returncode,
        ])

def measure_site(target: dict) -> list[float]:
    label = target["label"]
    host  = target["host"]
    port  = int(target.get("port", 443))

    chain_info = inspect_chain(label, host, port)
    if chain_info is None:
        return []

    ctx = make_ssl_context()
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

            if rep % 10 == 0:
                log(f"  {host}: {rep}/{REPETITIONS} último={elapsed_ms:.1f}ms")

        except Exception as e:
            warn(f"{host} rep={rep}: {e}")
            write_failure("measure", label, host, port, rep, e)
            write_raw_row(label, host, port, rep, "TIMEOUT", chain_info, "ERROR")
            continue

    return results

# =============================================================================
# Ejecutar mediciones
# =============================================================================

hdr("2. Medir sitios reales con TLS 1.3")

for target in TARGETS:
    log(f"\nIniciando: {target['label']} → {target['host']}:{target.get('port', 443)}")
    vals = measure_site(target)
    if vals:
        ok(f"{target['host']}: n={len(vals)}, mediana={statistics.median(vals):.1f}ms")
    else:
        warn(f"Sin mediciones válidas para {target['host']}")

# =============================================================================
# Resumen
# =============================================================================

hdr("3. Resumen estadístico")

raw_data: dict[tuple, list[float]] = {}
meta: dict[tuple, dict] = {}

with open(RAW_CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["latency_ms"] in ("TIMEOUT", "", "ERROR"):
            continue
        key = (row["label"], row["host"])
        raw_data.setdefault(key, []).append(float(row["latency_ms"]))
        meta[key] = row

summary_rows = []
fields = [
    "label", "host", "server_cert_algorithm", "detected_depth", "cert_count",
    "n", "mean_ms", "median_ms", "stdev_ms", "p95_ms", "min_ms", "max_ms",
    "pem_bytes", "der_bytes",
]

with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    sorted_keys = sorted(
        raw_data.keys(),
        key=lambda k: (meta[k].get("server_cert_algorithm", ""), int(meta[k].get("detected_depth", 0)), k[1])
    )

    print(f"\n  {'Host':22s} {'Algoritmo':12s} {'depth':>5} {'n':>4} {'median(ms)':>10} {'p95(ms)':>9} {'DER(B)':>8}")
    print("  " + "─" * 82)

    for key in sorted_keys:
        vals = raw_data[key]
        vs = sorted(vals)
        p95 = vs[math.ceil(0.95 * len(vs)) - 1]
        m = meta[key]
        row = {
            "label": m["label"],
            "host": m["host"],
            "server_cert_algorithm": m["server_cert_algorithm"],
            "detected_depth": int(m["detected_depth"]),
            "cert_count": int(m["cert_count"]),
            "n": len(vals),
            "mean_ms": round(statistics.mean(vals), 3),
            "median_ms": round(statistics.median(vals), 3),
            "stdev_ms": round(statistics.stdev(vals) if len(vals) > 1 else 0, 3),
            "p95_ms": round(p95, 3),
            "min_ms": round(min(vals), 3),
            "max_ms": round(max(vals), 3),
            "pem_bytes": int(m["chain_size_pem_bytes"]),
            "der_bytes": int(m["chain_size_der_bytes"]),
        }
        writer.writerow(row)
        summary_rows.append(row)

        print(f"  {row['host']:22s} {row['server_cert_algorithm']:12s} {row['detected_depth']:>5} "
              f"{row['n']:>4} {row['median_ms']:>10.1f} {row['p95_ms']:>9.1f} {row['der_bytes']:>8}")

ok(f"Raw → {RAW_CSV}")
ok(f"Resumen → {SUMMARY_CSV}")
ok(f"Cadenas → {CHAINS_CSV}")
ok(f"Fallos → {FAILURES_CSV}")

# =============================================================================
# Comparativo por algoritmo
# =============================================================================

hdr("4. Comparativo RSA vs ECDSA")

comparison_rows = []
by_algorithm: dict[str, list[dict]] = {}

for r in summary_rows:
    by_algorithm.setdefault(r["server_cert_algorithm"], []).append(r)

with open(ALGO_CSV, "w", newline="", encoding="utf-8") as f:
    fields_algo = [
        "server_cert_algorithm", "sites", "total_handshakes",
        "avg_median_ms", "median_of_medians_ms", "avg_p95_ms",
        "avg_der_bytes", "avg_depth",
    ]
    writer = csv.DictWriter(f, fieldnames=fields_algo)
    writer.writeheader()

    print(f"\n  {'Algoritmo':14s} {'sites':>5} {'handshakes':>10} {'avg median':>12} {'median-med':>12} {'avg DER':>10} {'avg depth':>10}")
    print("  " + "─" * 84)

    for alg, rows in sorted(by_algorithm.items()):
        medians = [float(r["median_ms"]) for r in rows]
        p95s    = [float(r["p95_ms"]) for r in rows]
        ders    = [float(r["der_bytes"]) for r in rows]
        depths  = [float(r["detected_depth"]) for r in rows]
        total_n = sum(int(r["n"]) for r in rows)

        row = {
            "server_cert_algorithm": alg,
            "sites": len(rows),
            "total_handshakes": total_n,
            "avg_median_ms": round(statistics.mean(medians), 3),
            "median_of_medians_ms": round(statistics.median(medians), 3),
            "avg_p95_ms": round(statistics.mean(p95s), 3),
            "avg_der_bytes": round(statistics.mean(ders), 1),
            "avg_depth": round(statistics.mean(depths), 3),
        }
        writer.writerow(row)
        comparison_rows.append(row)

        print(f"  {alg:14s} {row['sites']:>5} {row['total_handshakes']:>10} "
              f"{row['avg_median_ms']:>12.1f} {row['median_of_medians_ms']:>12.1f} "
              f"{row['avg_der_bytes']:>10.0f} {row['avg_depth']:>10.2f}")

ok(f"Comparativo algoritmo → {ALGO_CSV}")

if "rsa2048" not in by_algorithm or "ecdsa_p256" not in by_algorithm:
    warn("No se encontraron ambos grupos rsa2048 y ecdsa_p256 en los sitios probados.")
    warn("Esto es normal en internet real: el servidor decide qué certificado entrega.")
    warn("Agrega más dominios a TARGETS hasta tener ambos grupos, o usa el experimento local para control total.")

# =============================================================================
# Plots
# =============================================================================

hdr("5. Generar visualizaciones")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not summary_rows:
        warn("No hay datos en summary_rows; no se pueden generar plots.")
    else:
        # Mantengo colores específicos porque son comparativos por categoría.
        alg_colors = {
            "rsa2048": "#e05c5c",
            "ecdsa_p256": "#5c9ee0",
            "other": "#aaaaaa",
        }
        def color_for_alg(alg):
            return alg_colors.get(alg, "#aaaaaa")

        # 1. Latencia mediana por sitio, coloreado por algoritmo
        rows = sorted(summary_rows, key=lambda r: (r["server_cert_algorithm"], r["host"]))
        xlabels = [f"{r['host']}\n{r['server_cert_algorithm']}\nd={r['detected_depth']}" for r in rows]
        medians = [r["median_ms"] for r in rows]
        colors  = [color_for_alg(r["server_cert_algorithm"]) for r in rows]

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(xlabels, medians, color=colors, edgecolor="white", linewidth=0.6)
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
        ax.set_ylabel("Latencia mediana TLS 1.3 (ms)")
        ax.set_title("Latencia mediana por sitio — RSA-2048 vs ECDSA P-256")
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()
        out = PLOTS_DIR / "comparativo_latencia_sitio_rsa_vs_ecdsa.png"
        fig.savefig(out, dpi=150); plt.close(fig)
        ok(f"→ {out}")

        # 2. Boxplot comparativo RSA vs ECDSA usando datos crudos
        raw_by_alg: dict[str, list[float]] = {}
        with open(RAW_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["latency_ms"] not in ("TIMEOUT", "", "ERROR"):
                    raw_by_alg.setdefault(row["server_cert_algorithm"], []).append(float(row["latency_ms"]))

        preferred_order = [a for a in ["rsa2048", "ecdsa_p256"] if a in raw_by_alg]
        preferred_order += [a for a in sorted(raw_by_alg) if a not in preferred_order]

        if raw_by_alg:
            fig, ax = plt.subplots(figsize=(8, 5))
            bp = ax.boxplot([raw_by_alg[a] for a in preferred_order], labels=preferred_order, patch_artist=True)
            for patch, alg in zip(bp["boxes"], preferred_order):
                patch.set_facecolor(color_for_alg(alg))
                patch.set_alpha(0.7)
            ax.set_ylabel("Latencia TLS 1.3 (ms)")
            ax.set_title("Boxplot comparativo — RSA-2048 vs ECDSA P-256")
            ax.grid(True, axis="y", alpha=0.3)
            fig.tight_layout()
            out = PLOTS_DIR / "boxplot_rsa_vs_ecdsa.png"
            fig.savefig(out, dpi=150); plt.close(fig)
            ok(f"→ {out}")

        # 3. Promedio de medianas por algoritmo
        if comparison_rows:
            comp = sorted(comparison_rows, key=lambda r: r["server_cert_algorithm"])
            labels = [r["server_cert_algorithm"] for r in comp]
            avg_med = [r["avg_median_ms"] for r in comp]
            colors = [color_for_alg(a) for a in labels]

            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(labels, avg_med, color=colors, edgecolor="white", linewidth=0.6)
            ax.bar_label(bars, fmt="%.1f ms", padding=3, fontsize=9)
            ax.set_ylabel("Promedio de medianas (ms)")
            ax.set_title("Promedio de latencia mediana por algoritmo")
            ax.grid(True, axis="y", alpha=0.3)
            fig.tight_layout()
            out = PLOTS_DIR / "promedio_medianas_por_algoritmo.png"
            fig.savefig(out, dpi=150); plt.close(fig)
            ok(f"→ {out}")

        # 4. Tamaño DER por algoritmo
        if comparison_rows:
            comp = sorted(comparison_rows, key=lambda r: r["server_cert_algorithm"])
            labels = [r["server_cert_algorithm"] for r in comp]
            avg_der = [r["avg_der_bytes"] for r in comp]
            colors = [color_for_alg(a) for a in labels]

            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(labels, avg_der, color=colors, edgecolor="white", linewidth=0.6)
            ax.bar_label(bars, fmt="%.0f B", padding=3, fontsize=9)
            ax.set_ylabel("Tamaño DER promedio de cadena (bytes)")
            ax.set_title("Tamaño promedio de cadena — RSA-2048 vs ECDSA P-256")
            ax.grid(True, axis="y", alpha=0.3)
            fig.tight_layout()
            out = PLOTS_DIR / "tamano_der_promedio_rsa_vs_ecdsa.png"
            fig.savefig(out, dpi=150); plt.close(fig)
            ok(f"→ {out}")

        # 5. Scatter latencia vs DER, color por algoritmo
        fig, ax = plt.subplots(figsize=(8, 5))
        for alg in sorted(set(r["server_cert_algorithm"] for r in summary_rows)):
            subset = [r for r in summary_rows if r["server_cert_algorithm"] == alg]
            ax.scatter(
                [r["der_bytes"] for r in subset],
                [r["median_ms"] for r in subset],
                s=90,
                label=alg,
                color=color_for_alg(alg),
                edgecolors="white",
            )
            for r in subset:
                ax.annotate(r["host"], (r["der_bytes"], r["median_ms"]),
                            textcoords="offset points", xytext=(6, 4), fontsize=7)

        ax.set_xlabel("Tamaño de cadena DER (bytes)")
        ax.set_ylabel("Latencia mediana TLS 1.3 (ms)")
        ax.set_title("Latencia vs tamaño DER — comparativo por algoritmo")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = PLOTS_DIR / "scatter_latencia_vs_der_por_algoritmo.png"
        fig.savefig(out, dpi=150); plt.close(fig)
        ok(f"→ {out}")

        # 6. Scatter latencia vs profundidad, color por algoritmo
        fig, ax = plt.subplots(figsize=(8, 5))
        for alg in sorted(set(r["server_cert_algorithm"] for r in summary_rows)):
            subset = [r for r in summary_rows if r["server_cert_algorithm"] == alg]
            ax.scatter(
                [r["detected_depth"] for r in subset],
                [r["median_ms"] for r in subset],
                s=90,
                label=alg,
                color=color_for_alg(alg),
                edgecolors="white",
            )
            for r in subset:
                ax.annotate(r["host"], (r["detected_depth"], r["median_ms"]),
                            textcoords="offset points", xytext=(6, 4), fontsize=7)

        ax.set_xlabel("Profundidad detectada")
        ax.set_ylabel("Latencia mediana TLS 1.3 (ms)")
        ax.set_title("Latencia vs profundidad — comparativo por algoritmo")
        ax.set_xticks(sorted(set(r["detected_depth"] for r in summary_rows)))
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = PLOTS_DIR / "scatter_latencia_vs_profundidad_por_algoritmo.png"
        fig.savefig(out, dpi=150); plt.close(fig)
        ok(f"→ {out}")

except ImportError:
    warn("matplotlib no disponible. Instala con:")
    warn("py -m pip install matplotlib")

# =============================================================================
# Conclusión
# =============================================================================

hdr("6. Conclusión")

print(f"""
  ╔══════════════════════════════════════════════════════════════════════╗
  ║  HALLAZGOS: TLS 1.3 en sitios reales                                ║
  ╠══════════════════════════════════════════════════════════════════════╣""")

for r in comparison_rows:
    print(f"  ║  {r['server_cert_algorithm']:14s} sitios={r['sites']:2d} "
          f"avg-mediana={r['avg_median_ms']:7.1f}ms  "
          f"avg-DER={r['avg_der_bytes']:7.0f}B  avg-depth={r['avg_depth']:4.2f}")

print(f"""  ╠══════════════════════════════════════════════════════════════════════╣
  ║  Nota metodológica: en sitios reales detectamos RSA/ECDSA; no       ║
  ║  podemos obligar al servidor a entregar uno u otro certificado.     ║
  ║  Para control total de RSA-2048 vs ECDSA P-256 usa el benchmark     ║
  ║  local con certificados generados por el script.                    ║
  ╚══════════════════════════════════════════════════════════════════════╝
""")

print(f"  {B}Directorio:{RST} {BASE_DIR.resolve()}\n")
print(f"  {B}Resultados:{RST}")
for f in sorted(RESULTS_DIR.iterdir()):
    print(f"    {f.name:<45s} {f.stat().st_size:>8,} bytes")

if any(PLOTS_DIR.iterdir()):
    print(f"\n  {B}Gráficas:{RST}")
    for f in sorted(PLOTS_DIR.iterdir()):
        print(f"    {f.name}")

print()
ok("Todo listo.")
