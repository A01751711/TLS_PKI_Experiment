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
│       ├── utils.py                 ← Reusable utilities
│       ├── 01_collect_data.py       ← Measurement collection
│       └── 02_analyze_results.py    ← Statistical analysis & plots
│
├── 🔄 Execution/
│   ├── run.bat                      ← One-click Windows
│   └── run.sh                       ← One-click Linux/macOS
│
└── 📂 Data Folders/
    ├── data/                        ← Raw measurements (generated)
    └── results/                     ← Analysis outputs (generated)
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
```
results/
├── resumen_estadistico.csv         (Per-site statistics)
├── comparativo_algoritmo.csv       (RSA vs ECDSA comparison)
└── plots/                          (6 visualization PNG files)
```

**Done!** 🎉

---

## 📖 Documentation Guide

| Document | Read This For |
|----------|---------------|
| **00_START_HERE.md** (this file) | Quick introduction |
| [**QUICKSTART.md**](QUICKSTART.md) | 5-minute getting started |
| [**README.md**](README.md) | Complete technical reference |
| [**INSTALLATION.md**](INSTALLATION.md) | Platform-specific setup (Windows/Linux/macOS) |
| [**PROJECT_STRUCTURE.md**](PROJECT_STRUCTURE.md) | Architecture and design |
| [**REPRODUCIBILITY_GITHUB.md**](REPRODUCIBILITY_GITHUB.md) | GitHub/sharing guide |
| [**REPRODUCIBILITY_CHECKLIST.md**](REPRODUCIBILITY_CHECKLIST.md) | Verification checklist |

---

## 📋 What Each File Does

### Scripts (`scripts/`)

| Script | Purpose | Duration |
|--------|---------|----------|
| **01_collect_data.py** | Measures TLS handshakes from 10 real websites × 1000 times each | ~15 min |
| **02_analyze_results.py** | Calculates statistics and generates 6 comparative plots | ~5 sec |
| **utils.py** | Shared functions (logging, OpenSSL, cert parsing, CA bundle) | Library |

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
Edit `scripts/01_collect_data.py`:
```python
TARGETS = [
    {"label": "google", "host": "google.com", "port": 443},
    # Add your own sites here
]
```

### Change Number of Measurements
Edit `scripts/01_collect_data.py`:
```python
REPETITIONS = 1000  # Change to your value
```

### Increase Timeout (for slow networks)
Edit `scripts/01_collect_data.py`:
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

