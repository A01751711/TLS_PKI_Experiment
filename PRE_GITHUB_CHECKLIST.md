# Pre-GitHub Deployment Checklist

Antes de subir tu proyecto a GitHub, verifica esta checklist. ✅

## 📋 Estructura de Archivos

### Archivos Principales
- [ ] `README.md` — Documentación técnica completa
- [ ] `QUICKSTART.md` — Guía de 5 minutos
- [ ] `INSTALLATION.md` — Setup por plataforma
- [ ] `00_START_HERE.md` — Punto de entrada
- [ ] `requirements.txt` — Dependencias Python
- [ ] `.gitignore` — Exclusiones Git

### Scripts
- [ ] `scripts/main.py` — Script principal (recolección + análisis completo)
- [ ] `run.bat` — Ejecución Windows
- [ ] `run.sh` — Ejecución Linux/macOS
- [ ] `verify_environment.py` — Verificación de pre-requisitos

### Documentación Adicional
- [ ] `PROJECT_STRUCTURE.md` — Arquitectura
- [ ] `REPRODUCIBILITY_CHECKLIST.md` — Validación interna
- [ ] `REPRODUCIBILITY_GITHUB.md` — Guía para GitHub

### Directorios
- [ ] `data/` — Carpeta vacía (legacy, no se usa)
- [ ] `results/` — Carpeta vacía (legacy, no se usa)
- [ ] Nota: Resultados se generan en `tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/` por cada ejecución

---

## 🧪 Pruebas Pre-Deployment

### En Tu Máquina Local

- [ ] `python verify_environment.py` — Pasa sin errores
- [ ] `python scripts/main.py` — Completa exitosamente
- [ ] Se crea carpeta `tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/`
- [ ] Contiene `results/resumen_web_estadistico.csv`
- [ ] Contiene `plots/` con 6 archivos PNG
- [ ] Contiene `results/raw_web_results.csv` con >1000 líneas
- [ ] Contiene `results/chains_detectadas.csv`

### En Ambiente Limpio (Simulación)

```bash
# Crear carpeta temporal para simular usuario nuevo
mkdir /tmp/test_tls_pki
cd /tmp/test_tls_pki

# Clonar (o copiar tus archivos)
cp -r ~/TLS_PKI_Experiment/* .

# Simular usuario nuevo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar
pip install -r requirements.txt

# Verificar
python verify_environment.py

# Ejecutar (script centralizado)
python scripts/main.py
```

**Resultado esperado:** ✅ Funciona igual que en tu máquina

---

## 📝 Documentación

- [ ] README.md tiene todas las secciones:
  - [ ] Objetivo del experimento
  - [ ] Pregunta técnica
  - [ ] Requisitos (Python, OpenSSL)
  - [ ] Comandos para ejecutar
  - [ ] Descripción de salidas
  - [ ] Referencias técnicas

- [ ] INSTALLATION.md cubre:
  - [ ] Windows (Git for Windows, versión directa)
  - [ ] Linux (Ubuntu/Debian)
  - [ ] macOS (Homebrew)
  - [ ] Troubleshooting de dependencias

- [ ] QUICKSTART.md es realmente "5 minutos"
  - [ ] Solo pasos esenciales
  - [ ] Links a docs completas

- [ ] Todos los archivos .md tienen:
  - [ ] Títulos claros
  - [ ] Código de ejemplo
  - [ ] Explicaciones concisas

---

## 🔐 Seguridad y Privacidad

- [ ] No hay credenciales en código (API keys, contraseñas)
- [ ] No hay rutas absoltas hardcoded (C:\Users\...)
- [ ] No hay directorios personales
- [ ] CA bundle se descarga de URL pública y verificada
- [ ] Scripts no escriben fuera de project root

---

## 🎯 Metadatos GitHub

Antes de hacer push, en tu repo local:

```bash
# Verificar remoto
git remote -v

# Crear .gitignore (ya hecho)
cat .gitignore

# Commit inicial
git add .
git commit -m "Initial commit: TLS PKI reproducible research project"
```

### En GitHub Web

- [ ] Descripción corta en "About":
  ```
  Empirical study of X.509 certificate verification cost in TLS 1.3
  (RSA-2048 vs ECDSA P-256)
  ```

- [ ] Topics agregados:
  ```
  tls, pki, cryptography, x509, ecdsa, rsa, research, reproducible
  ```

- [ ] README es visible en GitHub (markdown renderizado)

- [ ] Licencia agregada:
  - [ ] Crear `LICENSE` (p.ej., MIT, CC-BY-4.0)
  - [ ] Mencionada en README.md

---

## 📊 Datos y Resultados

### Antes de Subir

- [ ] `data/` está EN .gitignore (datos generados)
- [ ] `results/` está EN .gitignore (outputs regenerables)
- [ ] `data/logs/` no sube a GitHub
- [ ] `data/certs_extraidos/` no sube a GitHub
- [ ] Solo scripts y docs suben

**Razón:** Los usuarios generarán sus propios datos al ejecutar

### Después de Subir

- [ ] Usuario puede clonar
- [ ] `data/` y `results/` existen pero vacíos (carpetas)
- [ ] Al ejecutar scripts, crea sus propios CSVs

---

## 🔍 Revisar Archivos Específicos

### 01_collect_data.py
- [ ] No tiene hardcoded paths
- [ ] TARGETS es fácil de modificar
- [ ] Comentarios explican secciones clave
- [ ] Usa Path() para rutas relativas

### 02_analyze_results.py
- [ ] Lee de `data/raw_web_results.csv`
- [ ] Escribe en `results/`
- [ ] No depende de ejecución anterior (solo de CSV)

### utils.py
- [ ] Funciones bien documentadas (docstrings)
- [ ] setup_ca_bundle() maneja fallback automático
- [ ] No hay imports externos no listados en requirements.txt

### run.bat, run.sh
- [ ] run.bat funciona en Windows
- [ ] run.sh es ejecutable (chmod +x)
- [ ] Ambos muestran progreso claro

---

## 🧠 Lógica de Decisiones

Documenta WHY, no solo WHAT. En cada script principal:

- [ ] Comentario inicial explica propósito
- [ ] Secciones con ## numeradas
- [ ] Decisiones técnicas comentadas
- [ ] Referencias a RFC/estándares

Ejemplo:
```python
# Usar TLS 1.3 específicamente por:
# - RFC 8446 es versión actual
# - Simplifica análisis (no mezclar versiones)
# - Refleja internet actual (>80% TLS 1.3 en 2026)
TLS_VERSION_FLAG = "-tls1_3"
```

---

## 🚀 Antes del Primer Push

```bash
# Último check local
cd ~/TLS_PKI_Experiment

# Verificar estructura
ls -la
ls -la scripts/
ls -la data/
ls -la results/

# Verificar .gitignore
cat .gitignore | grep data
cat .gitignore | grep results

# Verificar ambiente
python verify_environment.py

# Verificar que solo docs + scripts suban
git status

# Expected:
# On branch main
# nothing to commit, working tree clean
#
# O si es primer commit:
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#         .gitignore
#         00_START_HERE.md
#         INSTALLATION.md
#         ... (docs y scripts)
#         scripts/01_collect_data.py
#         ... (scripts)
#
# NO debe haber:
#         data/raw_web_results.csv
#         results/plots/*.png
```

---

## ✅ Final Verification

Execute this before pushing:

```bash
# Quick reproducibility test
python -c "
from pathlib import Path
import sys

# Check required files
required = [
    'README.md', 'QUICKSTART.md', 'INSTALLATION.md',
    'requirements.txt', '.gitignore',
    'scripts/01_collect_data.py', 'scripts/02_analyze_results.py',
    'scripts/utils.py', 'run.bat', 'run.sh',
    'verify_environment.py'
]

missing = [f for f in required if not Path(f).exists()]

if missing:
    print(f'❌ Missing files: {missing}')
    sys.exit(1)
else:
    print('✅ All required files present')

# Check .gitignore
gitignore = Path('.gitignore').read_text()
if 'data/' not in gitignore or 'results/' not in gitignore:
    print('❌ .gitignore does not exclude data/ and results/')
    sys.exit(1)
else:
    print('✅ .gitignore properly configured')

print('✅ Project ready for GitHub!')
"
```

---

## 📋 Post-GitHub Verification

After pushing to GitHub:

- [ ] Go to your GitHub repo URL
- [ ] Click "Code" button
- [ ] Copy HTTPS URL
- [ ] In new temp directory:
  ```bash
  cd /tmp/test_clone
  git clone <your-repo-url>
  cd TLS_PKI_Experiment
  python verify_environment.py
  ```
- [ ] Should pass all checks
- [ ] README.md renders beautifully
- [ ] All links work (.md files, code references)

---

## 🎉 You're Ready!

If all checkboxes are ✅, your project is:

- ✅ **Reproducible** — Anyone can clone and run
- ✅ **Professional** — Well-structured and documented
- ✅ **Safe** — No sensitive data leaked
- ✅ **Maintainable** — Easy for others to extend

### Push It!

```bash
git add .
git commit -m "Initial commit: TLS PKI reproducible research project"
git push -u origin main
```

Share the GitHub link with confidence. 🚀

---

## If Something Goes Wrong

1. Check [REPRODUCIBILITY_GITHUB.md](REPRODUCIBILITY_GITHUB.md)
2. Verify with [INSTALLATION.md](INSTALLATION.md)
3. Run `python verify_environment.py` locally
4. Review [README.md](README.md) for complete setup

---

**Last Updated:** May 17, 2026  
**Status:** Ready for production use ✅

