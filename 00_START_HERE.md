# 🚀 Welcome to TLS PKI Experiment

## What You Got

Your project has been **completely reorganized** into a **professional, reproducible research structure**. 

### ✅ Structure Created

```
TLS_PKI_Experiment/
├── 📚 Documentation/
│   ├── README.md                    ← Complete technical reference
│   ├── QUICKSTART.md                ← Get started in 5 minutes
│   ├── PROJECT_STRUCTURE.md         ← Detailed architecture
│   └── REPRODUCIBILITY_CHECKLIST.md ← Validation guide
│
├── 📦 Code/
│   ├── requirements.txt             ← All dependencies
│   └── scripts/
│       └── main.py                  ← Complete experiment (measurement + analysis)
│
├── 🔄 Execution/
│   ├── run.bat                      ← One-click Windows
│   └── run.sh                       ← One-click Linux/macOS
│
└── 📂 Generated Folders (after execution)/
    └── tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/  ← Timestamped output folder
        ├── results/                 ← CSV and analysis files
        ├── plots/                   ← 6 PNG visualizations
        ├── logs/                    ← OpenSSL debug logs
        └── certs_extraidos/         ← Extracted certificates
```

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify Environment
```bash
python verify_environment.py
```
This checks Python, OpenSSL, packages, and directories.
See [INSTALLATION.md](INSTALLATION.md) for platform-specific help.

### Step 3: Run the Experiment
```bash
# Windows:
python run.bat

# Linux/macOS:
chmod +x run.sh
bash run.sh
```

### Step 4: View Results

The script creates a **timestamped folder** with all outputs:

```
tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/
├── results/
│   ├── raw_web_results.csv           ← All 10,000 handshake measurements
│   ├── resumen_web_estadistico.csv   ← Statistics per site
│   ├── comparativo_algoritmo.csv     ← RSA vs ECDSA comparison
│   ├── chains_detectadas.csv         ← Certificate chain summary
│   └── fallos.csv                    ← Errors (if any)
├── plots/
│   ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
│   ├── boxplot_rsa_vs_ecdsa.png
│   ├── promedio_medianas_por_algoritmo.png
│   ├── tamano_der_promedio_rsa_vs_ecdsa.png
│   ├── scatter_latencia_vs_der_por_algoritmo.png
│   └── scatter_latencia_vs_profundidad_por_algoritmo.png
├── logs/
│   ├── inspect_*.log                 ← OpenSSL certificate inspection
│   └── client_*.log                  ← Handshake timing details
└── certs_extraidos/
    └── [site_certificates]/          ← PEM files per site
```

**Note:** Each run creates a NEW timestamped folder, so you can compare multiple runs.

---

## � What Happens When You Run

**Single Command:**
```bash
python scripts/main.py
```

**This does everything:**
1. ✅ Verify Python and OpenSSL
2. ✅ Find/download CA certificate bundle
3. ✅ Inspect 10 real websites (HTTPS/TLS 1.3)
4. ✅ Measure 1000 handshakes per website (~15 min)
5. ✅ Calculate statistics & comparisons
6. ✅ Generate 6 comparative plots
7. ✅ Save everything to timestamped folder

**Output:** New folder like `tls_web_tls13_rsa_ecdsa_20260519_200420/` with all results.

---

## 📋 What Each File Does

### Script (`scripts/main.py`)

Script único que hace TODO:
- Verifica dependencias (OpenSSL, Python)
- Busca/descarga CA bundle
- Inspecciona 10 sitios HTTPS reales
- Mide 1000 handshakes TLS 1.3 por sitio
- Calcula estadísticas
- Genera 6 gráficas comparativas
- Exporta resultados a CSV y PNG

### Documentation

| File | Read This For |
|------|---------------|
| **README.md** | Complete technical explanation (objective, methodology, outputs) |
| **QUICKSTART.md** | 5-minute getting started guide |
| **PROJECT_STRUCTURE.md** | Visual diagram and design decisions |
| **REPRODUCIBILITY_CHECKLIST.md** | Verification that everything is reproducible |

---

## 🔧 Configuration

### Change Target Websites
Edit `scripts/main.py`:
```python
TARGETS = [
    {"label": "google", "host": "google.com", "port": 443},
    # Add your own sites here
]
```

### Change Number of Measurements
Edit `scripts/main.py`:
```python
REPETITIONS = 1000  # Change to your value
```

### Increase Timeout (for slow networks)
Edit `scripts/main.py`:
```python
TIMEOUT_SECONDS = 15  # Default is 10
```

---

## 📊 Output Explanation

After running, you'll get:

### CSV Data Files

**results/resumen_estadistico.csv**
```
host,algorithm,n,median_ms,p95_ms,der_bytes
google.com,ecdsa_p256,1000,85.234,95.102,1892
github.com,rsa2048,1000,92.445,105.330,2145
...
```

**results/comparativo_algoritmo.csv**
```
algorithm,sites,total_handshakes,avg_median_ms,avg_der_bytes
rsa2048,5,5000,91.2,2100
ecdsa_p256,4,4000,87.5,1950
```

### PNG Visualizations

1. **comparativo_latencia_sitio_rsa_vs_ecdsa.png**
   - Bar chart: median latency per site (colored by algorithm)

2. **boxplot_rsa_vs_ecdsa.png**
   - Boxplot: latency distribution for each algorithm

3. **promedio_medianas_por_algoritmo.png**
   - Bar chart: average median latency by algorithm

4. **tamano_der_promedio_rsa_vs_ecdsa.png**
   - Bar chart: average certificate chain size

5. **scatter_latencia_vs_der_por_algoritmo.png**
   - Scatter plot: latency vs certificate size

6. **scatter_latencia_vs_profundidad_por_algoritmo.png**
   - Scatter plot: latency vs certificate chain depth

---

## ❓ Troubleshooting

### "openssl not found"
- **Windows:** Install [Git for Windows](https://git-scm.com/download/win) (includes OpenSSL)
- **Linux:** `sudo apt-get install openssl`
- **macOS:** `brew install openssl`

### "matplotlib not available"
```bash
pip install matplotlib
```

### "Network timeout"
- Edit `TIMEOUT_SECONDS` in `scripts/01_collect_data.py`
- Or verify your internet connection
- Or remove problematic sites from `TARGETS`

### "No CA bundle found"
The script will attempt automatic download. If that fails:
```bash
curl -o cacert.pem https://curl.se/ca/cacert.pem
```
Place `cacert.pem` in the project root.

---

## 🔐 Why This Structure?

### ✅ Reproducible
- Anyone can clone this repo and run the exact same experiment
- No external dependencies or manual setup
- All decisions are logged

### ✅ Professional
- Separation of concerns (collection vs. analysis)
- Reusable utilities in `utils.py`
- Comprehensive documentation

### ✅ Maintainable
- Scripts are modular and independent
- Easy to customize without breaking functionality
- Clear file organization

### ✅ Scientific
- Raw data separated from processed outputs
- All errors logged for audit trail
- Full metadata in CSV headers

---

## 📖 Next Steps

1. ✅ Read [README.md](README.md) for complete technical details
2. ✅ Run `python run.bat` (or `bash run.sh`)
3. ✅ Check `results/` folder for outputs
4. ✅ Customize `TARGETS` or `REPETITIONS` as needed
5. ✅ Share the entire `TLS_PKI_Experiment/` folder for reproducibility

---

## 📞 Support

For issues or customization questions:
- Check [QUICKSTART.md](QUICKSTART.md) for common setup problems
- Check [README.md](README.md) for detailed documentation
- Review comments in the Python scripts
- Check [REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md) for validation

---

## 📝 Project Info

**Objective:** Measure the operational cost of X.509 certificate verification in TLS 1.3 under different algorithms (RSA-2048 vs ECDSA P-256) and chain depths.

**Methodology:** Empirical measurements of real-world HTTPS connections treated as a black box, collecting latency, message sizes, and certificate chain metadata.

**Output:** Statistical analysis and comparative visualizations for RSA vs ECDSA performance.

**Data:** 10,000+ measurements across 10 major websites.

---

**Status:** ✅ Ready to use  
**Last Updated:** May 2026

