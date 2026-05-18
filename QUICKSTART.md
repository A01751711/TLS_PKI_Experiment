# Quick Start Guide

## 5-Minute Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Environment (optional but recommended)
```bash
python verify_environment.py
```

This checks Python version, OpenSSL, packages, and directories. See [INSTALLATION.md](INSTALLATION.md) for setup help.

### 3. Run Complete Experiment (Collection + Analysis)

**On Windows:**
```bash
python run.bat
```

**On Linux/macOS:**
```bash
# First time: make script executable
chmod +x run.sh

# Then run:
bash run.sh
```

**Or manually:**
```bash
python scripts/01_collect_data.py
python scripts/02_analyze_results.py
```

### 4. View Results
```
results/
├── resumen_estadistico.csv
├── comparativo_algoritmo.csv
└── plots/
    ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
    ├── boxplot_rsa_vs_ecdsa.png
    └── ... (6 plots total)
```

## Troubleshooting

### OpenSSL not found
- **Windows:** Install Git for Windows (includes OpenSSL)
- **Linux:** `sudo apt-get install openssl`
- **macOS:** `brew install openssl`

### matplotlib not available
```bash
pip install matplotlib
```

### Network issues
Edit `scripts/01_collect_data.py` and modify `TARGETS` list or increase `TIMEOUT_SECONDS`.

## Custom Configuration

### Change number of repetitions
Edit `scripts/01_collect_data.py`:
```python
REPETITIONS = 500  # default is 1000
```

### Add/remove websites
Edit `scripts/01_collect_data.py`:
```python
TARGETS = [
    {"label": "example", "host": "example.com", "port": 443},
    # Add your own sites here
]
```

## Output Interpretation

- **resumen_estadistico.csv**: Per-site statistics (median, p95, stdev, etc.)
- **comparativo_algoritmo.csv**: RSA vs ECDSA comparison
- **plots/**: Visual comparisons of latency, size, and depth

See README.md for detailed column descriptions.

