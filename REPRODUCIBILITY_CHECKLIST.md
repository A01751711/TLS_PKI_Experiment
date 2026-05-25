# Lista de verificación de reproducibilidad

Esta checklist verifica que tu experimento cumple con todos los requisitos de reproducibilidad.

## ✓ Requisitos de Estructura Mínima

### Documentación
- [x] **README.md** — Descripción clara del objetivo, requisitos, comandos y salidas
  - [x] Pregunta técnica central
  - [x] Requisitos del entorno
  - [x] Comandos completos de principio a fin
  - [x] Descripción detallada de salidas
  - [x] Referencias técnicas

- [x] **QUICKSTART.md** — Guía de 5 minutos para usuarios nuevos

- [x] **PROJECT_STRUCTURE.md** — Diagrama visual y decisiones de diseño

### Dependencias
- [x] **requirements.txt** — Todas las dependencias Python enlistadas
  - pandas>=1.0.0
  - matplotlib>=3.1.0
  - colorama>=0.4.3

### Organización de scripts
- [x] **scripts/** carpeta con el script principal
  - [x] **main.py** — Script único que ejecuta todo el flujo
    - [x] Verificación de dependencias
    - [x] Configuración del bundle CA
    - [x] Inspección de cadenas
    - [x] Mediciones de handshake TLS
    - [x] Cálculo de estadísticas
    - [x] Generación de gráficas
    - [x] Exportación a CSV y PNG

### Gestión de datos
- [x] **scripts/main.py** genera una carpeta con marca de tiempo:
  - **results/** — Archivos CSV y análisis
    - raw_web_results.csv (todos los 10,000+ handshakes)
    - chains_detectadas.csv (resumen de cadenas)
    - fallos.csv (errores, si los hay)
    - resumen_web_estadistico.csv (estadísticas por sitio)
    - comparativo_algoritmo.csv (comparación RSA vs ECDSA)
  
  - **plots/** — 6 gráficas PNG comparativas
  
  - **logs/** — Detalles OpenSSL para depuración
    - inspect_*.log (inspección de cadenas)
    - client_*.log (mediciones de latencia)
  
  - **certs_extraidos/** — Certificados PEM extraídos por sitio

### Ejecución
- [x] **run.bat** — Script de ejecución en un clic para Windows
- [x] **run.sh** — Script de ejecución en un clic para Linux/macOS

### Control de versiones
- [x] **.gitignore** — Excluye archivos temporales, logs, datos generados

---

## ✓ Verificación Técnica

### Independencia del script
```
✓ main.py integra todo el flujo en un solo archivo
✓ Cada ejecución crea una carpeta nueva con timestamp (sin sobrescribir)
✓ verify_environment.py valida el entorno antes de la primera corrida
```

### Reproducibilidad
```
✓ No requiere información externa más allá de acceso a Internet
✓ CA bundle se auto-detecta o descarga automáticamente
✓ Todas las decisiones están registradas en logs/
✓ Errores se registran para auditoría en results/fallos.csv
✓ Datos crudos están separados de salidas procesadas
```

### Portabilidad
```
✓ Compatible con Windows, Linux, macOS
✓ Python 3.7+ (sin features muy recientes)
✓ OpenSSL como única dependencia del sistema
✓ No usa rutas absolutas fijas en el código
✓ Scripts usan Path().resolve() para rutas relativas
```

### Documentación técnica
```
✓ README.md explica completo el experimento
✓ QUICKSTART.md permite arrancar en 5 minutos
✓ Código tiene comentarios en secciones clave
✓ CSVs tienen encabezados descriptivos
```

---

## ✓ Uso Típico para Reproducción

### En un entorno nuevo (otra máquina, otro usuario):

```bash
# 1. Descargar una copia en ZIP desde el repositorio y extraerla
cd TLS_PKI_Experiment

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate          # Linux/macOS
# o
venv\Scripts\activate             # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar que OpenSSL está disponible
openssl version

# 5. Ejecutar experimento completo
.\run.bat                         # Windows (PowerShell o CMD)
# o
bash run.sh                       # Linux/macOS

# 6. Revisar resultados (carpeta con timestamp más reciente)
ls tls_web_tls13_rsa_ecdsa_*/     # Linux/macOS
dir tls_web_tls13_rsa_ecdsa_*     # Windows
```

### Tiempo esperado:
- **Total: 15–30 minutos** (dependiendo de velocidad de red y sitios)
  - Verificación y configuración: ~30 segundos
  - Mediciones: 10–25 minutos (1000 handshakes × 10 sitios)
  - Cálculo y gráficas: ~2 minutos

---

## ✓ Validación Post-Ejecución

Después de ejecutar el experimento, verifica en la carpeta con timestamp generada:

```bash
# Ejemplo: ls tls_web_tls13_rsa_ecdsa_20260519_200420/

# Datos recolectados y analizados (todo bajo results/)
✓ results/raw_web_results.csv              (~1-5 MB, >10,000 líneas)
✓ results/chains_detectadas.csv            (~10 KB, 10-11 líneas)
✓ results/fallos.csv                       (~1-50 KB, 0 si sin errores)
✓ results/resumen_web_estadistico.csv      (~15 KB)
✓ results/comparativo_algoritmo.csv        (~1 KB)

# Visualizaciones
✓ plots/*.png                              (6 archivos PNG @ 150 DPI)

# Logs para auditoría y depuración
✓ logs/inspect_*.log                       (inspección de cadenas OpenSSL)
✓ logs/client_*.log                        (mediciones de latencia por sitio)

# Certificados extraídos
✓ certs_extraidos/*/                       (carpetas por sitio, PEM/DER)
```

---

## ✓ Customización sin Romper Reproducibilidad

### Cambiar sitios medidos
Edita en `scripts/main.py`:
```python
TARGETS = [
    {"label": "google", "host": "google.com", "port": 443},
    # Agrega/quita sitios aquí
]
```

### Cambiar número de repeticiones
Edita en `scripts/main.py`:
```python
REPETITIONS = 500  # por defecto es 1000
```

### Cambiar timeout
Edita en `scripts/main.py`:
```python
TIMEOUT_SECONDS = 15  # por defecto es 10
```

### Desactivar verificación de certificados
Edita en `scripts/main.py` (en setup_ca_bundle):
```python
# Comenta la búsqueda automática de CA bundle
# y usa modo inseguro
```

**Nota:** Cualquier cambio debe documentarse en comentarios del código.

---

## ✓ Solución de problemas de reproducción

### "openssl no encontrado"
```
Windows: Instala Git for Windows (incluye OpenSSL)
Linux:   sudo apt-get install openssl
macOS:   brew install openssl
```

### "matplotlib no disponible"
```
pip install matplotlib
```

### "Timeout en mediciones"
- Aumenta `TIMEOUT_SECONDS` en `scripts/main.py`
- O verifica conectividad a los sitios objetivo
- O quita sitios problemáticos de `TARGETS`

### "No encontré CA bundle"
El script descarga automáticamente de curl.se. Si falla:
```
curl -o cacert.pem https://curl.se/ca/cacert.pem
# Coloca cacert.pem en la raíz del proyecto
```

---

## ✓ Checklist Final de Reproducibilidad

Antes de compartir el repositorio, verifica:

- [ ] `README.md` está completo y es claro
- [ ] `requirements.txt` lista todas las dependencias
- [ ] Scripts en `scripts/` están bien documentados
- [ ] `verify_environment.py` pasa (crear `data/` y `results/` vacías si lo solicita)
- [ ] `run.bat` y `run.sh` son ejecutables y funcionan
- [ ] `.gitignore` excluye datos generados
- [ ] Pruebas una ejecución completa en ambiente limpio
- [ ] Documentación de cambios de configuración
- [ ] Licencia o uso educativo está claro

---

**Estado Actual:** ✅ COMPLETAMENTE REPRODUCIBLE

Este proyecto cumple con todos los estándares de reproducibilidad científica/académica.

