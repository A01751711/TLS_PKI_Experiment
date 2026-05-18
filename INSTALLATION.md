# Installation and Verification Guide

## Pre-Flight Checks

Before running the experiment, verify your environment:

```bash
python verify_environment.py
```

This will check:
- ✓ Python 3.7+
- ✓ OpenSSL availability
- ✓ Required Python packages (pandas, matplotlib)
- ✓ Project directories
- ✓ CA certificate bundle

---

## Platform-Specific Setup

### Windows

1. **Install Python 3.7+**
   - Download from https://www.python.org/downloads/
   - ✓ Check "Add Python to PATH" during installation

2. **Install OpenSSL**
   - Option A: **Git for Windows** (easiest)
     - Download from https://git-scm.com/download/win
     - Installs OpenSSL automatically
   
   - Option B: **Direct OpenSSL**
     - Download from https://slproweb.com/products/Win32OpenSSL.html
     - Add to PATH

3. **Verify installation**
   ```powershell
   python --version
   openssl version
   pip --version
   ```

4. **Install Python dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Verify environment**
   ```powershell
   python verify_environment.py
   ```

6. **Run experiment**
   ```powershell
   python run.bat
   ```

---

### Linux (Ubuntu/Debian)

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip openssl

# 2. Verify Python version
python3 --version  # Should be 3.7+

# 3. Install Python packages
pip3 install -r requirements.txt

# 4. Make run.sh executable
chmod +x run.sh

# 5. Verify environment
python3 verify_environment.py

# 6. Run experiment
bash run.sh
```

---

### macOS

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies via Homebrew
brew install python3 openssl

# 3. Verify installation
python3 --version
openssl version
pip3 --version

# 4. Install Python packages
pip3 install -r requirements.txt

# 5. Make run.sh executable
chmod +x run.sh

# 6. Verify environment
python3 verify_environment.py

# 7. Run experiment
bash run.sh
```

---

## Troubleshooting

### "python: command not found"
**Windows:**
```powershell
# Check PATH
$env:PATH -split ";"

# If Python not in PATH, reinstall with "Add to PATH" option
```

**Linux/macOS:**
```bash
which python3
# If not found: sudo apt-get install python3 (Linux)
#               brew install python3 (macOS)
```

---

### "openssl: command not found"
**Windows:**
```powershell
# Install Git for Windows from https://git-scm.com/download/win
# Or install OpenSSL directly from https://slproweb.com/products/Win32OpenSSL.html
```

**Linux:**
```bash
sudo apt-get install openssl
```

**macOS:**
```bash
brew install openssl
```

---

### "ModuleNotFoundError: No module named 'pandas' / 'matplotlib'"
```bash
pip install -r requirements.txt

# If using Python 3:
pip3 install -r requirements.txt

# If still failing:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### "Permission denied: run.sh" (Linux/macOS)
```bash
chmod +x run.sh
bash run.sh
```

---

### Network errors downloading CA bundle
If the automatic CA bundle download fails:

```bash
# Manual download
curl -o cacert.pem https://curl.se/ca/cacert.pem

# Place in project root
# (The scripts will find it automatically)
```

---

## Minimal Installation (Quick Test)

If you just want to verify everything works without waiting 15 minutes:

1. Create a test script `test_environment.py`:
```python
import csv
from pathlib import Path
from scripts.utils import log, ok, verify_openssl, setup_ca_bundle

print("Testing imports... ", end="")
ok("✓")

print("Testing OpenSSL... ", end="")
if verify_openssl():
    ok("✓")
else:
    print("✗ OpenSSL not found")
    exit(1)

print("Testing CA bundle setup... ", end="")
verify_args, verify_mode = setup_ca_bundle()
ok("✓")

print("\nAll systems go!")
```

2. Run it:
```bash
python test_environment.py
```

---

## Automated CI/CD Verification

If running in CI/CD (GitHub Actions, etc.):

```yaml
name: Verify Environment

on: [push]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y openssl
      
      - name: Install Python dependencies
        run: pip install -r requirements.txt
      
      - name: Verify environment
        run: python verify_environment.py
      
      - name: Run quick test
        run: python test_environment.py
```

---

## What Gets Verified

| Item | Purpose | How to Fix |
|------|---------|-----------|
| Python 3.7+ | Language runtime | Install Python from python.org |
| OpenSSL | Certificate inspection | See platform-specific guide above |
| pandas | Data analysis | `pip install pandas` |
| matplotlib | Visualization | `pip install matplotlib` |
| data/ directory | Raw data storage | Already created in project |
| results/ directory | Output storage | Already created in project |
| Permissions (Unix) | Script execution | `chmod +x run.sh` |

---

## Success Indicators

After running `python verify_environment.py`, you should see:

```
========================================================================
 Environment Verification for TLS PKI Experiment
========================================================================

Python:
  [✓] Python 3.7+ (found 3.9)

System Dependencies:
  [✓] OpenSSL in PATH
       → OpenSSL 1.1.1 ...

Python Packages:
  [✓] pandas
  [✓] matplotlib

File System:
  [✓] data/ directory exists
  [✓] results/ directory exists
  [✓] scripts/ directory exists

Certificate Verification:
  [i] CA bundle available (or will be auto-downloaded)

========================================================================
 ✓ All checks passed! Ready to run.

   Execute:
     python run.bat      (Windows)
     bash run.sh         (Linux/macOS)
========================================================================
```

If you see all ✓ marks, you're good to go!

