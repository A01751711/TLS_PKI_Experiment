#!/usr/bin/env python3
"""
02_analyze_results.py

Análisis y visualización de datos TLS recolectados.

Lee datos desde:
- data/raw_web_results.csv (mediciones crudas)

Genera:
- results/resumen_estadistico.csv (estadísticas por sitio)
- results/comparativo_algoritmo.csv (comparación RSA vs ECDSA)
- results/plots/*.png (visualizaciones)

Uso:
    python scripts/02_analyze_results.py
"""

import csv
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import log, ok, warn, hdr

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

RAW_CSV = DATA_DIR / "raw_web_results.csv"
SUMMARY_CSV = RESULTS_DIR / "resumen_estadistico.csv"
ALGO_CSV = RESULTS_DIR / "comparativo_algoritmo.csv"

# =============================================================================
# STEP 1: Validate Input Data
# =============================================================================

hdr("1. Validar datos de entrada")

if not RAW_CSV.exists():
    warn(f"No encontré {RAW_CSV}")
    warn("Primero ejecuta: python scripts/01_collect_data.py")
    sys.exit(1)

ok(f"Datos encontrados: {RAW_CSV}")

# =============================================================================
# STEP 2: Read and Parse Raw Data
# =============================================================================

hdr("2. Leer datos crudos")

raw_data: dict[tuple, list[float]] = {}
meta: dict[tuple, dict] = {}

with open(RAW_CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["latency_ms"] in ("TIMEOUT", "", "ERROR"):
            continue
        try:
            key = (row["label"], row["host"])
            latency = float(row["latency_ms"])
            raw_data.setdefault(key, []).append(latency)
            meta[key] = row
        except (ValueError, KeyError) as e:
            warn(f"Línea corrupta: {e}")
            continue

if not raw_data:
    warn("No hay datos válidos en el CSV.")
    sys.exit(1)

ok(f"Parsed {sum(len(v) for v in raw_data.values())} measurements from {len(raw_data)} sites")

# =============================================================================
# STEP 3: Calculate Per-Site Statistics
# =============================================================================

hdr("3. Calcular estadísticas por sitio")

summary_rows = []
fields = [
    "label", "host", "server_cert_algorithm", "detected_depth", "cert_count",
    "n", "mean_ms", "median_ms", "stdev_ms", "p95_ms", "min_ms", "max_ms",
    "pem_bytes", "der_bytes",
]

with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    # Sort by algorithm, depth, then host
    sorted_keys = sorted(
        raw_data.keys(),
        key=lambda k: (meta[k].get("server_cert_algorithm", ""), 
                       int(meta[k].get("detected_depth", 0)), k[1])
    )

    print(f"\n  {'Host':22s} {'Algorithm':12s} {'depth':>5} {'n':>4} "
          f"{'median(ms)':>10} {'p95(ms)':>9} {'DER(B)':>8}")
    print("  " + "─" * 82)

    for key in sorted_keys:
        vals = raw_data[key]
        vs = sorted(vals)
        p95_idx = math.ceil(0.95 * len(vs)) - 1
        p95 = vs[p95_idx] if p95_idx >= 0 else vs[-1]
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

        print(f"  {row['host']:22s} {row['server_cert_algorithm']:12s} "
              f"{row['detected_depth']:>5} {row['n']:>4} "
              f"{row['median_ms']:>10.1f} {row['p95_ms']:>9.1f} {row['der_bytes']:>8}")

ok(f"Resumen → {SUMMARY_CSV}")

# =============================================================================
# STEP 4: Algorithm Comparison
# =============================================================================

hdr("4. Comparativa por algoritmo (RSA vs ECDSA)")

comparison_rows = []
by_algorithm: dict[str, list[dict]] = {}

for r in summary_rows:
    by_algorithm.setdefault(r["server_cert_algorithm"], []).append(r)

fields_algo = [
    "server_cert_algorithm", "sites", "total_handshakes",
    "avg_median_ms", "median_of_medians_ms", "avg_p95_ms",
    "avg_der_bytes", "avg_depth",
]

with open(ALGO_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields_algo)
    writer.writeheader()

    print(f"\n  {'Algorithm':14s} {'sites':>5} {'handshakes':>10} "
          f"{'avg median':>12} {'median-med':>12} {'avg DER':>10} {'avg depth':>10}")
    print("  " + "─" * 84)

    for alg in sorted(by_algorithm.keys()):
        rows = by_algorithm[alg]
        medians = [float(r["median_ms"]) for r in rows]
        p95s = [float(r["p95_ms"]) for r in rows]
        ders = [float(r["der_bytes"]) for r in rows]
        depths = [float(r["detected_depth"]) for r in rows]
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

ok(f"Comparación → {ALGO_CSV}")

if "rsa2048" not in by_algorithm or "ecdsa_p256" not in by_algorithm:
    warn("No se encontraron ambos grupos RSA-2048 y ECDSA P-256.")
    warn("En internet real, los servidores deciden qué certificado entregar.")

# =============================================================================
# STEP 5: Visualization with Matplotlib
# =============================================================================

hdr("5. Generar visualizaciones")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not summary_rows:
        warn("Sin datos para graficar.")
    else:
        # Color scheme by algorithm
        alg_colors = {
            "rsa2048": "#e05c5c",
            "ecdsa_p256": "#5c9ee0",
            "other": "#aaaaaa",
        }

        def color_for_alg(alg):
            return alg_colors.get(alg, "#aaaaaa")

        # Plot 1: Latency per site
        rows = sorted(summary_rows, key=lambda r: (r["server_cert_algorithm"], r["host"]))
        xlabels = [f"{r['host']}\n{r['server_cert_algorithm']}\nd={r['detected_depth']}" for r in rows]
        medians = [r["median_ms"] for r in rows]
        colors = [color_for_alg(r["server_cert_algorithm"]) for r in rows]

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(xlabels, medians, color=colors, edgecolor="white", linewidth=0.6)
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
        ax.set_ylabel("Latencia mediana TLS 1.3 (ms)")
        ax.set_title("Latencia mediana por sitio — RSA-2048 vs ECDSA P-256")
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()
        out = PLOTS_DIR / "comparativo_latencia_sitio_rsa_vs_ecdsa.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        ok(f"→ {out.name}")

        # Plot 2: Boxplot by algorithm (using raw data)
        raw_by_alg: dict[str, list[float]] = {}
        with open(RAW_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["latency_ms"] not in ("TIMEOUT", "", "ERROR"):
                    try:
                        raw_by_alg.setdefault(
                            row["server_cert_algorithm"], []
                        ).append(float(row["latency_ms"]))
                    except ValueError:
                        continue

        preferred_order = [a for a in ["rsa2048", "ecdsa_p256"] if a in raw_by_alg]
        preferred_order += [a for a in sorted(raw_by_alg) if a not in preferred_order]

        if raw_by_alg:
            fig, ax = plt.subplots(figsize=(8, 5))
            bp = ax.boxplot(
                [raw_by_alg[a] for a in preferred_order],
                labels=preferred_order,
                patch_artist=True
            )
            for patch, alg in zip(bp["boxes"], preferred_order):
                patch.set_facecolor(color_for_alg(alg))
                patch.set_alpha(0.7)
            ax.set_ylabel("Latencia TLS 1.3 (ms)")
            ax.set_title("Boxplot comparativo — RSA-2048 vs ECDSA P-256")
            ax.grid(True, axis="y", alpha=0.3)
            fig.tight_layout()
            out = PLOTS_DIR / "boxplot_rsa_vs_ecdsa.png"
            fig.savefig(out, dpi=150)
            plt.close(fig)
            ok(f"→ {out.name}")

        # Plot 3: Average medians by algorithm
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
            fig.savefig(out, dpi=150)
            plt.close(fig)
            ok(f"→ {out.name}")

        # Plot 4: Average DER size by algorithm
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
            fig.savefig(out, dpi=150)
            plt.close(fig)
            ok(f"→ {out.name}")

        # Plot 5: Scatter latency vs DER size
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
                ax.annotate(
                    r["host"], (r["der_bytes"], r["median_ms"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=7
                )

        ax.set_xlabel("Tamaño de cadena DER (bytes)")
        ax.set_ylabel("Latencia mediana TLS 1.3 (ms)")
        ax.set_title("Latencia vs tamaño DER — comparativo por algoritmo")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = PLOTS_DIR / "scatter_latencia_vs_der_por_algoritmo.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        ok(f"→ {out.name}")

        # Plot 6: Scatter latency vs depth
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
                ax.annotate(
                    r["host"], (r["detected_depth"], r["median_ms"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=7
                )

        ax.set_xlabel("Profundidad detectada")
        ax.set_ylabel("Latencia mediana TLS 1.3 (ms)")
        ax.set_title("Latencia vs profundidad — comparativo por algoritmo")
        ax.set_xticks(sorted(set(r["detected_depth"] for r in summary_rows)))
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = PLOTS_DIR / "scatter_latencia_vs_profundidad_por_algoritmo.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        ok(f"→ {out.name}")

except ImportError:
    warn("matplotlib no disponible. Instala con:")
    warn("  pip install matplotlib")

# =============================================================================
# STEP 6: Summary
# =============================================================================

hdr("6. Análisis completado")

print(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  RESULTADOS: Medición de TLS 1.3                            ║
  ╠══════════════════════════════════════════════════════════════╣""")

for r in comparison_rows:
    print(f"  ║  {r['server_cert_algorithm']:14s} sitios={r['sites']:2d} "
          f"avg-mediana={r['avg_median_ms']:7.1f}ms  "
          f"avg-DER={r['avg_der_bytes']:7.0f}B  avg-depth={r['avg_depth']:4.2f}")

print(f"""  ╠══════════════════════════════════════════════════════════════╣
  ║  Datos disponibles en: results/                             ║
  ║  - Tablas CSV                                               ║
  ║  - Gráficas PNG                                             ║
  ╚══════════════════════════════════════════════════════════════╝
""")

print(f"  Resultados en: {RESULTS_DIR.resolve()}\n")
if RESULTS_DIR.exists():
    print(f"  Archivos:")
    for f in sorted(RESULTS_DIR.rglob("*")):
        if f.is_file():
            rel_path = f.relative_to(RESULTS_DIR)
            print(f"    {str(rel_path):<45s} {f.stat().st_size:>8,} bytes")

print()
ok("Análisis completado exitosamente.")

