# Project Structure Summary

```
TLS_PKI_Experiment/
│
├── 📄 README.md                    ★ Main documentation (objective, setup, usage)
├── 📄 QUICKSTART.md                ★ 5-minute getting started guide
├── 📄 requirements.txt             ★ Python dependencies
├── 📄 .gitignore                   ★ Version control exclusions
│
├── 🔨 run.bat                      ★ Windows one-click execution
├── 🔨 run.sh                       ★ Linux/macOS one-click execution
│
├── 📁 scripts/
│   ├── __init__.py                 (Package marker)
│   │
│   ├── 📜 utils.py                 ★ Shared utilities
│   │   ├── Logging functions (log, ok, warn, hdr)
│   │   ├── CA bundle detection & download
│   │   ├── OpenSSL command builders
│   │   ├── Certificate parsing (algorithm, subject, size)
│   │   └── SSL/TLS context creation
│   │
│   ├── 📜 01_collect_data.py       ★ Data collection script
│   │   ├── Verify dependencies (OpenSSL, Python)
│   │   ├── Setup CA bundle for verification
│   │   ├── Inspect certificate chains from live servers
│   │   ├── Perform 1000 TLS handshake measurements per site
│   │   └── Export raw measurements to CSV
│   │
│   └── 📜 02_analyze_results.py    ★ Analysis & visualization script
│       ├── Parse raw data from CSV
│       ├── Calculate statistics (mean, median, p95, stdev)
│       ├── Compare RSA-2048 vs ECDSA P-256
│       ├── Generate 6 comparative plots with matplotlib
│       └── Export summary tables to CSV
│
├── 📁 data/                        ★ Raw experimental data
│   ├── raw_web_results.csv         (All 10,000+ handshake measurements)
│   ├── chains_detectadas.csv       (Summary of detected chains)
│   ├── fallos.csv                  (Error log)
│   │
│   └── 📁 logs/                    (OpenSSL debug logs)
│       ├── inspect_*.log
│       ├── client_*.log
│       └── inspect_*_fallback.log
│
│   └── 📁 certs_extraidos/         (Extracted certificates)
│       ├── example_example_com/
│       │   ├── cert_0.pem
│       │   ├── cert_1.pem
│       │   └── cert_2.pem
│       ├── google_google_com/
│       └── ... (one per site)
│
└── 📁 results/                     ★ Analysis outputs (regenerable)
    │
    ├── resumen_estadistico.csv     (Per-site statistics)
    │   ├── host, algorithm, depth
    │   ├── n, mean_ms, median_ms, stdev_ms
    │   ├── p95_ms, min_ms, max_ms
    │   └── pem_bytes, der_bytes
    │
    ├── comparativo_algoritmo.csv   (Algorithm comparison)
    │   ├── server_cert_algorithm
    │   ├── sites, total_handshakes
    │   ├── avg_median_ms, median_of_medians_ms
    │   ├── avg_p95_ms
    │   └── avg_der_bytes, avg_depth
    │
    └── 📁 plots/                   (6 Visualization PNG files)
        ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
        │   (Bar chart: median latency per site, colored by algorithm)
        │
        ├── boxplot_rsa_vs_ecdsa.png
        │   (Boxplot: latency distribution by algorithm)
        │
        ├── promedio_medianas_por_algoritmo.png
        │   (Bar chart: average median latency per algorithm)
        │
        ├── tamano_der_promedio_rsa_vs_ecdsa.png
        │   (Bar chart: average DER chain size per algorithm)
        │
        ├── scatter_latencia_vs_der_por_algoritmo.png
        │   (Scatter: latency vs DER size, colored by algorithm)
        │
        └── scatter_latencia_vs_profundidad_por_algoritmo.png
            (Scatter: latency vs chain depth, colored by algorithm)
```

## Key Design Decisions

### ✓ Separation of Concerns
- **utils.py**: Reusable utilities (CA bundle, OpenSSL, certificate parsing)
- **01_collect_data.py**: Exclusive focus on data collection
- **02_analyze_results.py**: Exclusive focus on analysis & visualization

### ✓ Data Organization
- **data/**: Raw, generated data (reproducible starting point)
- **results/**: Processed outputs (regenerable from data/)
- **data/logs/**: Debug information for troubleshooting

### ✓ Reproducibility
- All dependencies listed in `requirements.txt`
- Scripts are independent but sequential
- No external hardcoded paths
- CA bundle auto-detection + download fallback
- Complete logging of errors and decisions

### ✓ Documentation
- **README.md**: Comprehensive technical reference
- **QUICKSTART.md**: 5-minute getting started
- **run.bat/run.sh**: One-command execution
- Inline comments in code

### ✓ Cross-Platform
- Works on Windows, Linux, macOS
- Uses Python 3.7+ compatibility
- Platform-specific run scripts provided

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User: python run.bat  (or run.sh on Linux/macOS)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │ 01_collect_data.py             │
        ├────────────────────────────────┤
        │ 1. Verify OpenSSL + Python     │
        │ 2. Setup CA bundle             │
        │ 3. Inspect 10 HTTPS sites      │
        │ 4. Run 1000 handshakes × 10    │
        │ 5. Generate data/*.csv         │
        └────────────┬───────────────────┘
                     │ (outputs: data/*.csv)
                     ▼
        ┌────────────────────────────────┐
        │ 02_analyze_results.py          │
        ├────────────────────────────────┤
        │ 1. Read data/raw_web_results   │
        │ 2. Calculate statistics        │
        │ 3. Group by algorithm          │
        │ 4. Generate matplotlib plots   │
        │ 5. Export results/*.csv        │
        └────────────┬───────────────────┘
                     │ (outputs: results/*.csv + results/plots/*.png)
                     ▼
                ┌─────────────┐
                │ ✓ Complete  │
                └─────────────┘
```

---

## File Size Estimates

| File | Size | Notes |
|------|------|-------|
| data/raw_web_results.csv | ~2-5 MB | 10,000+ measurements |
| data/chains_detectadas.csv | ~10 KB | 10 site summaries |
| data/fallos.csv | ~1-50 KB | Error records |
| results/resumen_estadistico.csv | ~15 KB | 10 sites × 15 columns |
| results/comparativo_algoritmo.csv | ~1 KB | 2-3 algorithm rows |
| results/plots/*.png | ~200-400 KB | 6 plots @ 150 DPI |

**Total disk usage**: ~10-15 MB (mostly raw CSV data)

---

## Next Steps for User

1. ✓ Review README.md for full documentation
2. ✓ Install dependencies: `pip install -r requirements.txt`
3. ✓ Run experiment: `python run.bat` (Windows) or `bash run.sh` (Linux/macOS)
4. ✓ View results in `results/` folder
5. ✓ Customize in `scripts/01_collect_data.py` (TARGETS list, REPETITIONS, etc.)

