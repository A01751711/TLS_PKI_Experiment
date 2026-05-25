# Guía de instalación y verificación

## Comprobaciones previas

Antes de ejecutar el experimento, verifica tu entorno:

```bash
python verify_environment.py
```

El script comprueba:
- ✓ Python 3.7+
- ✓ OpenSSL disponible en PATH
- ✓ Paquetes Python requeridos (pandas, matplotlib)
- ✓ Directorio `scripts/`
- ✓ Carpetas opcionales `data/` y `results/` (marcadores de posición)
- ✓ Bundle de certificados CA (local o descarga automática en la primera ejecución)

Si `verify_environment.py` indica que faltan `data/` o `results/`, créalas vacías en la raíz del proyecto:

```bash
mkdir data results          # Linux/macOS
mkdir data; mkdir results   # PowerShell en Windows
```

---

## Configuración por plataforma

### Windows

1. **Instalar Python 3.7+**
   - Descarga desde https://www.python.org/downloads/
   - ✓ Marca «Add Python to PATH» durante la instalación

2. **Instalar OpenSSL**
   - Opción A: **Git for Windows** (la más sencilla)
     - Descarga desde https://git-scm.com/download/win
     - Incluye OpenSSL automáticamente
   
   - Opción B: **OpenSSL directo**
     - Descarga desde https://slproweb.com/products/Win32OpenSSL.html
     - Añade la ruta al PATH

3. **Verificar instalación**
   ```powershell
   python --version
   openssl version
   pip --version
   ```

4. **Instalar dependencias Python**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Verificar entorno**
   ```powershell
   python verify_environment.py
   ```

6. **Ejecutar experimento**
   ```powershell
   .\run.bat
   ```

---

### Linux (Ubuntu/Debian)

```bash
# 1. Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install python3 python3-pip openssl

# 2. Verificar versión de Python
python3 --version  # Debe ser 3.7+

# 3. Instalar paquetes Python
pip3 install -r requirements.txt

# 4. Hacer ejecutable run.sh (solo la primera vez)
chmod +x run.sh

# 5. Verificar entorno
python3 verify_environment.py

# 6. Ejecutar experimento
bash run.sh
```

---

### macOS

```bash
# 1. Instalar Homebrew (si aún no lo tienes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar dependencias con Homebrew
brew install python3 openssl

# 3. Verificar instalación
python3 --version
openssl version
pip3 --version

# 4. Instalar paquetes Python
pip3 install -r requirements.txt

# 5. Hacer ejecutable run.sh (solo la primera vez)
chmod +x run.sh

# 6. Verificar entorno
python3 verify_environment.py

# 7. Ejecutar experimento
bash run.sh
```

---

## Solución de problemas

### «python: command not found»

**Windows:**
```powershell
# Revisar PATH
$env:PATH -split ";"

# Si Python no está en PATH, reinstala marcando «Add to PATH»
```

**Linux/macOS:**
```bash
which python3
# Si no aparece: sudo apt-get install python3 (Linux)
#                brew install python3 (macOS)
```

---

### «openssl: command not found»

**Windows:**
```powershell
# Instala Git for Windows desde https://git-scm.com/download/win
# O OpenSSL desde https://slproweb.com/products/Win32OpenSSL.html
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

### «ModuleNotFoundError: No module named 'pandas' / 'matplotlib'»

```bash
pip install -r requirements.txt

# Con Python 3 explícito:
pip3 install -r requirements.txt

# Si sigue fallando:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### «Permission denied: run.sh» (Linux/macOS)

```bash
chmod +x run.sh
bash run.sh
```

---

### Errores de red al descargar el bundle CA

Si la descarga automática del bundle CA falla:

```bash
# Descarga manual
curl -o cacert.pem https://curl.se/ca/cacert.pem

# Colócalo en la raíz del proyecto
# (scripts/main.py lo detectará automáticamente)
```

---

## Verificación rápida (sin ejecutar el experimento completo)

Para comprobar que todo está listo sin esperar 15–20 minutos de mediciones:

```bash
python verify_environment.py
```

Ese script es la única verificación previa necesaria. No hace falta ningún otro script auxiliar.

---

## Verificación automatizada en CI/CD

Si usas GitHub Actions u otro CI:

```yaml
name: Verificar entorno

on: [push]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      
      - name: Instalar dependencias del sistema
        run: |
          sudo apt-get update
          sudo apt-get install -y openssl
      
      - name: Instalar dependencias Python
        run: pip install -r requirements.txt
      
      - name: Crear carpetas de marcador de posición
        run: mkdir -p data results
      
      - name: Verificar entorno
        run: python verify_environment.py
```

---

## Qué se verifica

| Elemento | Propósito | Cómo corregirlo |
|----------|-----------|-----------------|
| Python 3.7+ | Intérprete | Instalar desde python.org |
| OpenSSL | Inspección de certificados | Ver guía por plataforma arriba |
| pandas | Análisis de datos | `pip install pandas` |
| matplotlib | Visualización | `pip install matplotlib` |
| `data/` | Carpeta opcional de marcador de posición | `mkdir data` |
| `results/` | Carpeta opcional de marcador de posición | `mkdir results` |
| Permisos (Unix) | Ejecución de `run.sh` | `chmod +x run.sh` |

---

## Indicadores de éxito

Tras ejecutar `python verify_environment.py`, deberías ver algo como:

```
======================================================================
 Verificación de entorno — Experimento TLS PKI
======================================================================

Python:
  [✓] Python 3.7+ (detectado 3.9)

Dependencias del sistema:
  [✓] OpenSSL en PATH
       → OpenSSL 1.1.1 ...

Paquetes Python:
  [✓] pandas
  [✓] matplotlib

Sistema de archivos:
  [✓] existe el directorio data/
  [✓] existe el directorio results/
  [✓] existe el directorio scripts/

Verificación de certificados:
  [i] Bundle CA no encontrado localmente (se intentará descargar en la primera ejecución)

======================================================================
 ✓ Todas las comprobaciones pasaron. Listo para ejecutar.

   Ejecuta:
     .\run.bat           (Windows)
     bash run.sh         (Linux/macOS)
======================================================================
```

Si todas las marcas son ✓, puedes ejecutar el experimento.

**Última actualización:** Mayo 2026
