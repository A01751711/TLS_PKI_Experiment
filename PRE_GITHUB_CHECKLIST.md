# Lista de verificación previa a GitHub

Antes de subir tu proyecto a GitHub, verifica esta lista. ✅

## 📋 Estructura de Archivos

### Archivos Principales
- [ ] `README.md` — Documentación técnica completa
- [ ] `QUICKSTART.md` — Guía de 5 minutos
- [ ] `INSTALLATION.md` — Instalación por plataforma
- [ ] `00_START_HERE.md` — Punto de entrada
- [ ] `requirements.txt` — Dependencias Python
- [ ] `.gitignore` — Exclusiones Git

### Scripts
- [ ] `scripts/main.py` — Script principal (recolección + análisis completo)
- [ ] `run.bat` — Ejecución Windows
- [ ] `run.sh` — Ejecución Linux/macOS
- [ ] `verify_environment.py` — Verificación de pre-requisitos

### Documentación adicional
- [ ] `PROJECT_STRUCTURE.md` — Arquitectura
- [ ] `REPRODUCIBILITY_CHECKLIST.md` — Validación interna
- [ ] `REPRODUCIBILITY_GITHUB.md` — Guía para GitHub

### Directorios
- [ ] Opcional: `data/` y `results/` vacías en la raíz (si `verify_environment.py` las exige)
- [ ] Nota: Los resultados reales se generan en `tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/` por cada ejecución

---

## 🧪 Pruebas antes de publicar

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

# Descargar una copia en ZIP y extraerla
unzip TLS_PKI_Experiment-main.zip

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
  - [ ] Solución de problemas de dependencias

- [ ] QUICKSTART.md es realmente "5 minutos"
  - [ ] Solo pasos esenciales
  - [ ] Enlaces a la documentación completa

- [ ] Todos los archivos .md tienen:
  - [ ] Títulos claros
  - [ ] Código de ejemplo
  - [ ] Explicaciones concisas

---

## 🔐 Seguridad y Privacidad

- [ ] No hay credenciales en código (claves de API, contraseñas)
- [ ] No hay rutas absolutas fijas en el código (p. ej. `C:\Users\...`)
- [ ] No hay directorios personales
- [ ] El bundle CA se descarga desde una URL pública y verificada
- [ ] Los scripts no escriben fuera de la raíz del proyecto

---

## 🎯 Metadatos en GitHub

Antes de hacer push, en tu repo local:

```bash
# Verificar remoto
git remote -v

# Crear .gitignore (ya hecho)
cat .gitignore

# Commit inicial
git add .
git commit -m "Commit inicial: proyecto TLS PKI reproducible"
```

### En la web de GitHub

- [ ] Descripción corta en «About»:
  ```
  Estudio empírico del costo de verificación de certificados X.509 en TLS 1.3
  (RSA-2048 vs ECDSA P-256)
  ```

- [ ] Temas (topics) agregados:
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
- [ ] `results/` está EN .gitignore (salidas regenerables)
- [ ] Carpetas `tls_web_tls13_rsa_ecdsa_*/` no suben a GitHub (salidas regenerables)
- [ ] Solo scripts y docs suben

**Razón:** Los usuarios generarán sus propios datos al ejecutar

### Después de Subir

- [ ] Usuario puede descargar ZIP y ejecutar
- [ ] Opcional: crear `data/` y `results/` vacías si la verificación lo pide
- [ ] Al ejecutar scripts, crea sus propios CSVs

---

## 🔍 Revisar Archivos Específicos

### main.py
- [ ] Integra recolección y análisis en un solo script
- [ ] No tiene rutas fijas en el código
- [ ] TARGETS es fácil de modificar
- [ ] Comentarios explican secciones clave
- [ ] Usa Path() para rutas relativas

### run.bat, run.sh
- [ ] run.bat funciona en Windows
- [ ] run.sh es ejecutable (chmod +x)
- [ ] Ambos muestran progreso claro

---

## 🧠 Lógica de Decisiones

Documenta el porqué, no solo el qué. En el script principal:

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
# Última comprobación local
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

# Resultado esperado:
# En la rama main
# nada para confirmar, árbol de trabajo limpio
#
# O en el primer commit, solo archivos del proyecto (documentación y scripts):
#         .gitignore
#         00_START_HERE.md
#         INSTALLATION.md
#         ... (docs y scripts)
#         scripts/main.py
#         ... (scripts)
#
# NO debe haber:
#         tls_web_tls13_rsa_ecdsa_*/
#         cacert.pem
```

---

## ✅ Verificación final

Ejecuta esto antes del push:

```bash
# Verificación rápida de reproducibilidad
python -c "
from pathlib import Path
import sys

# Archivos requeridos
required = [
    'README.md', 'QUICKSTART.md', 'INSTALLATION.md',
    'requirements.txt', '.gitignore',
    'scripts/main.py',
    'run.bat', 'run.sh',
    'verify_environment.py'
]

missing = [f for f in required if not Path(f).exists()]

if missing:
    print(f'❌ Faltan archivos: {missing}')
    sys.exit(1)
else:
    print('✅ Todos los archivos requeridos presentes')

# Comprobar .gitignore
gitignore = Path('.gitignore').read_text()
if 'tls_web_tls13_rsa_ecdsa_' not in gitignore:
    print('❌ .gitignore no excluye carpetas de salida con marca de tiempo')
    sys.exit(1)
else:
    print('✅ .gitignore configurado correctamente')

print('✅ Proyecto listo para GitHub!')
"
```

---

## 📋 Verificación posterior a GitHub

Después de subir a GitHub:

- [ ] Abre la URL de tu repositorio en GitHub
- [ ] Haz clic en el botón "Code"
- [ ] Descarga el ZIP del repositorio
- [ ] En un directorio temporal nuevo:
  ```bash
  mkdir -p /tmp/test_tls_pki
  cd /tmp/test_tls_pki
  unzip TLS_PKI_Experiment-main.zip
  cd TLS_PKI_Experiment
  python verify_environment.py
  ```
- [ ] Debe pasar todos los checks
- [ ] README.md se renderiza correctamente
- [ ] Todos los enlaces funcionan (archivos .md, referencias)

---

## 🎉 ¡Listo para publicar!

Si todos los checkboxes están ✅, tu proyecto es:

- ✅ **Reproducible** — Cualquier usuario puede descargar el ZIP y ejecutar
- ✅ **Profesional** — Bien estructurado y documentado en español
- ✅ **Seguro** — Sin datos sensibles en el repositorio
- ✅ **Mantenible** — Fácil de extender por otros

### Publicar

```bash
git add .
git commit -m "Commit inicial: proyecto TLS PKI reproducible"
git push -u origin main
```

Comparte el enlace de GitHub con confianza. 🚀

---

## Si algo falla

1. Revisa [REPRODUCIBILITY_GITHUB.md](REPRODUCIBILITY_GITHUB.md)
2. Verifica con [INSTALLATION.md](INSTALLATION.md)
3. Ejecuta `python verify_environment.py` en local
4. Consulta [README.md](README.md) para la configuración completa

---

**Última actualización:** Mayo 2026  
**Estado:** Listo para publicar ✅

