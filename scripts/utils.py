"""
Shared utilities for TLS PKI Certificate Verification Experiment

Functions:
- Logging utilities (log, ok, warn, die, hdr)
- CA bundle detection and download
- OpenSSL operations (extract PEM, convert to DER, parse certificates)
- Helpers for certificate analysis
"""

import os
import platform
import re
import socket
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Optional, List

# =============================================================================
# ANSI Colors and UI Helpers
# =============================================================================

if platform.system() == "Windows":
    os.system("color")

R   = "\033[0;31m"
G   = "\033[0;32m"
Y   = "\033[1;33m"
C   = "\033[0;36m"
B   = "\033[1m"
RST = "\033[0m"

def log(msg: str) -> None:
    """Print informational message."""
    print(f"{C}[•]{RST} {msg}")

def ok(msg: str) -> None:
    """Print success message."""
    print(f"{G}[✓]{RST} {msg}")

def warn(msg: str) -> None:
    """Print warning message."""
    print(f"{Y}[!]{RST} {msg}")

def die(msg: str) -> None:
    """Print error and exit."""
    print(f"{R}[✗]{RST} {msg}", file=sys.stderr)
    sys.exit(1)

def hdr(msg: str) -> None:
    """Print section header."""
    bar = "═" * 64
    print(f"\n{B}{C}{bar}{RST}")
    print(f"{B}  {msg}{RST}")
    print(f"{B}{C}{bar}{RST}")

# =============================================================================
# CA Bundle Detection
# =============================================================================

def find_ca_bundle() -> Optional[Path]:
    """
    Search for CA bundle in standard locations.
    Returns Path if found, None otherwise.
    """
    script_dir = Path(__file__).resolve().parent.parent
    
    candidates = [
        script_dir / "cacert.pem",
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

    # Windows-specific paths
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

def download_ca_bundle(output_path: Path) -> bool:
    """
    Attempt to download cacert.pem from curl.se.
    Returns True if successful, False otherwise.
    """
    try:
        warn("No encontré CA bundle. Intentando descargar cacert.pem desde curl.se...")
        ctx_download = ssl.create_default_context()
        with urllib.request.urlopen("https://curl.se/ca/cacert.pem", context=ctx_download, timeout=30) as r:
            output_path.write_bytes(r.read())
        ok(f"CA bundle descargado: {output_path}")
        return True
    except Exception as e:
        warn(f"No pude descargar cacert.pem: {e}")
        return False

def setup_ca_bundle() -> tuple[List[str], str]:
    """
    Set up CA bundle for OpenSSL verification.
    Returns: (verify_args, verify_mode)
    
    verify_args: list of OpenSSL flags
    verify_mode: "CAfile" or "insecure"
    """
    script_dir = Path(__file__).resolve().parent.parent
    ca_bundle = find_ca_bundle()

    if ca_bundle:
        ok(f"CA bundle encontrado: {ca_bundle}")
        return ["-CAfile", str(ca_bundle)], "CAfile"

    # Try to download
    ca_dest = script_dir / "cacert.pem"
    if download_ca_bundle(ca_dest):
        return ["-CAfile", str(ca_dest)], "CAfile"

    # Fallback to insecure
    warn("Modo inseguro: se medirá handshake sin verificación de certificados.")
    return ["-verify", "0"], "insecure"

# =============================================================================
# OpenSSL Operations
# =============================================================================

def openssl_run(args: List[str], input_data: Optional[str] = None, timeout: int = 10) -> subprocess.CompletedProcess:
    """
    Run OpenSSL command with given arguments.
    """
    return subprocess.run(
        ["openssl"] + args,
        input=input_data,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )

def extract_pem_certs(text: str) -> List[str]:
    """
    Extract all PEM-formatted certificates from text.
    Returns list of PEM strings.
    """
    return re.findall(
        r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
        text,
        flags=re.DOTALL,
    )

def pem_to_der_size(pem: str, timeout: int = 10) -> int:
    """
    Convert PEM certificate to DER and return size in bytes.
    Returns 0 on error.
    """
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-outform", "DER"],
            input=pem.encode("utf-8"),
            capture_output=True,
            timeout=timeout,
        )
        return len(proc.stdout) if proc.returncode == 0 else 0
    except Exception:
        return 0

# =============================================================================
# Certificate Parsing
# =============================================================================

def cert_subject(pem: str, timeout: int = 10) -> str:
    """
    Extract subject (DN) from PEM certificate.
    Returns subject string or "unknown" on error.
    """
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-noout", "-subject", "-nameopt", "RFC2253"],
            input=pem,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode == 0:
            return proc.stdout.strip().replace("subject=", "").strip()
    except Exception:
        pass
    return "unknown"

def server_cert_algorithm(pem: str, timeout: int = 10) -> str:
    """
    Classify certificate algorithm.
    
    Returns:
    - "rsa2048" for RSA-2048
    - "ecdsa_p256" for ECDSA P-256
    - "rsa<bits>" for other RSA
    - "ecdsa_<curve>" for other ECDSA
    - "other" for unknown algorithms
    """
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-noout", "-text"],
            input=pem,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        txt = (proc.stdout or "") + "\n" + (proc.stderr or "")

        # RSA detection
        rsa_bits = re.search(r"Public-Key:\s*\((\d+)\s*bit\)", txt, flags=re.I)
        if "rsaEncryption" in txt or "RSA Public-Key" in txt or "Public Key Algorithm: rsa" in txt:
            if rsa_bits and int(rsa_bits.group(1)) == 2048:
                return "rsa2048"
            if rsa_bits:
                return f"rsa{rsa_bits.group(1)}"
            return "rsa_unknown"

        # ECDSA detection
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

# =============================================================================
# OpenSSL s_client Command Building
# =============================================================================

def build_s_client_cmd(
    host: str,
    port: int,
    verify_args: List[str],
    tls_version_flag: str = "-tls1_3",
    extra_flags: Optional[List[str]] = None
) -> List[str]:
    """
    Build OpenSSL s_client command for certificate inspection.
    """
    cmd = [
        "s_client",
        "-connect", f"{host}:{port}",
        "-servername", host,
        tls_version_flag,
        "-nocommands",
    ]
    cmd += verify_args
    if extra_flags:
        cmd += extra_flags
    return cmd

# =============================================================================
# Verification Helpers
# =============================================================================

def verify_openssl() -> bool:
    """
    Check if OpenSSL is available in PATH.
    Returns True if found, False otherwise.
    """
    import shutil
    if shutil.which("openssl") is None:
        return False
    return True

def create_ssl_context(ca_bundle: Optional[Path] = None, verify_mode: str = "CAfile") -> ssl.SSLContext:
    """
    Create SSL context for TLS 1.3 connections.
    """
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    if ca_bundle:
        ctx.load_verify_locations(str(ca_bundle))

    if verify_mode == "insecure":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    return ctx

