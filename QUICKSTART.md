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

### 3. Run Complete Experiment

**Windows:**
```bash
run.bat
```

**Linux/macOS:**
```bash
# First time: make script executable
chmod +x run.sh

# Then run:
./run.sh
```

**Or manually (all platforms):**
```bash
python scripts/main.py
```

### 4. Wait for Results (~15-20 minutes)

The script will:
- Measure 10 websites × 1000 handshakes each
- Show progress in the terminal
- Create a timestamped folder with all outputs

**Output folder example:**
```
tls_web_tls13_rsa_ecdsa_20260519_200420/
├── results/
│   ├── raw_web_results.csv           ← All 10,000 measurements
│   ├── resumen_web_estadistico.csv   ← Per-site stats
│   ├── comparativo_algoritmo.csv     ← RSA vs ECDSA
│   └── ...
├── plots/
│   ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
│   ├── boxplot_rsa_vs_ecdsa.png
│   └── ... (4 more PNG files)
└── logs/

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
Edit `scripts/main.py` and modify `TARGETS` list or increase `TIMEOUT_SECONDS`.

## Custom Configuration

### Change number of repetitions
Edit `scripts/main.py`:
```python
REPETITIONS = 500  # default is 1000
```

### Add/remove websites
Edit `scripts/main.py`:
```python
TARGETS = [
    {"label": "example", "host": "example.com", "port": 443},
    # Add your own sites here
]
```

### Increase timeout
Edit `scripts/main.py`:
```python
TIMEOUT_SECONDS = 15  # default is 10
```

## Output Interpretation

- **resumen_estadistico.csv**: Per-site statistics (median, p95, stdev, etc.)
- **comparativo_algoritmo.csv**: RSA vs ECDSA comparison
- **plots/**: Visual comparisons of latency, size, and depth

See README.md for detailed column descriptions.

