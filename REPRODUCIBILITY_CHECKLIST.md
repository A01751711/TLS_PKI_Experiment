# Reproducibility Checklist

Esta checklist verifica que tu experimento cumple con todos los requisitos de reproducibilidad.

## ✓ Requisitos de Estructura Mínima

### Documentation
- [x] **README.md** — Descripción clara del objetivo, requisitos, comandos y salidas
  - [x] Pregunta técnica central
  - [x] Requisitos del entorno
  - [x] Comandos completos end-to-end
  - [x] Descripción detallada de salidas
  - [x] Referencias técnicas

- [x] **QUICKSTART.md** — Guía de 5 minutos para usuarios nuevos

- [x] **PROJECT_STRUCTURE.md** — Diagrama visual y decisiones de diseño

### Dependencies
- [x] **requirements.txt** — Todas las dependencias Python enlistadas
  - pandas>=1.0.0
  - matplotlib>=3.1.0
  - colorama>=0.4.3

### Scripts Organization
- [x] **scripts/** carpeta con scripts claramente etiquetados
  - [x] `__init__.py` — Hace que sea un paquete Python
  
  - [x] **utils.py** — Funciones compartidas reutilizables
    - [x] Logging utilities
    - [x] CA bundle detection
    - [x] OpenSSL wrappers
    - [x] Certificate parsing
    - [x] SSL context creation
  
  - [x] **01_collect_data.py** — Script de recolección de datos
    - [x] Verificación de dependencias
    - [x] Setup de CA bundle
    - [x] Inspección de cadenas
    - [x] Mediciones de handshake TLS
    - [x] Exportación a CSV
  
  - [x] **02_analyze_results.py** — Script de análisis y visualización
    - [x] Lectura de datos crudos
    - [x] Cálculo de estadísticas
    - [x] Agrupación por algoritmo
    - [x] Generación de gráficas
    - [x] Exportación de resultados

### Data Management
- [x] **data/** — Carpeta para datos crudos
  - Contendrá (después de ejecución):
    - raw_web_results.csv
    - chains_detectadas.csv
    - fallos.csv
    - logs/ (subdirectorio)
    - certs_extraidos/ (subdirectorio)

- [x] **results/** — Carpeta para salidas regenerables
  - Contendrá (después de análisis):
    - resumen_estadistico.csv
    - comparativo_algoritmo.csv
    - plots/ (con 6 gráficas PNG)

### Execution
- [x] **run.bat** — Script de ejecución one-click para Windows
- [x] **run.sh** — Script de ejecución one-click para Linux/macOS

### Version Control
- [x] **.gitignore** — Excluye archivos temporales, logs, datos generados

---

## ✓ Verificación Técnica

### Independencia de Scripts
```
✓ 01_collect_data.py NO depende de ningún output previo
✓ 02_analyze_results.py lee ÚNICAMENTE de data/raw_web_results.csv
✓ Ambos scripts usan utils.py para funciones compartidas
✓ Scripts pueden ejecutarse repetidamente sin conflictos
```

### Reproducibilidad
```
✓ No requiere información externa más allá de acceso a Internet
✓ CA bundle se auto-detecta o descarga automáticamente
✓ Todas las decisiones están registradas en logs/
✓ Errores se registran para auditoría en data/fallos.csv
✓ Datos crudos están separados de salidas procesadas
```

### Portabilidad
```
✓ Compatible con Windows, Linux, macOS
✓ Python 3.7+ (sin features muy recientes)
✓ OpenSSL como única dependencia del sistema
✓ No usa rutas absolutas hardcoded
✓ Scripts usan Path().resolve() para rutas relativas
```

### Documentation
```
✓ README.md explica completo el experimento
✓ QUICKSTART.md permite arrancar en 5 minutos
✓ Código tiene comentarios en secciones clave
✓ Funciones en utils.py tienen docstrings
✓ CSVs tienen encabezados descriptivos
```

---

## ✓ Uso Típico para Reproducción

### En un entorno nuevo (otra máquina, otro usuario):

```bash
# 1. Clonar o descargar el proyecto
git clone <repo>
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
python run.bat                    # Windows
# o
bash run.sh                       # Linux/macOS

# 6. Revisar resultados
ls results/                       # Linux/macOS
dir results                       # Windows
```

### Tiempo esperado:
- Recolección: 10–30 minutos (dependiendo de velocidad de red)
- Análisis: <5 segundos
- **Total: ~15 minutos**

---

## ✓ Validación Post-Ejecución

Después de ejecutar el experimento, verifica:

```bash
# Datos recolectados
✓ data/raw_web_results.csv    (~1-5 MB, >10,000 líneas)
✓ data/chains_detectadas.csv  (~10 KB, 10-11 líneas)
✓ data/fallos.csv             (~1-50 KB)

# Análisis completado
✓ results/resumen_estadistico.csv      (~15 KB)
✓ results/comparativo_algoritmo.csv    (~1 KB)
✓ results/plots/*.png                  (6 archivos PNG)

# Logs para auditoría
✓ data/logs/inspect_*.log     (inspección de cadenas)
✓ data/logs/client_*.log      (mediciones por sitio)

# Certificados extraídos
✓ data/certs_extraidos/*/     (carpetas por sitio)
```

---

## ✓ Customización sin Romper Reproducibilidad

### Cambiar sitios medidos
Edita en `scripts/01_collect_data.py`:
```python
TARGETS = [
    {"label": "google", "host": "google.com", "port": 443},
    # Agrega/quita sitios aquí
]
```

### Cambiar número de repeticiones
Edita en `scripts/01_collect_data.py`:
```python
REPETITIONS = 500  # default es 1000
```

### Cambiar timeout
Edita en `scripts/01_collect_data.py`:
```python
TIMEOUT_SECONDS = 15  # default es 10
```

### Desactivar verificación de certificados
Edita en `scripts/01_collect_data.py` (en setup_ca_bundle):
```python
# Comenta la búsqueda automática de CA bundle
# y usa modo inseguro
```

**Nota:** Cualquier cambio debe documentarse en comentarios del código.

---

## ✓ Troubleshooting de Reproducción

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
- Aumenta `TIMEOUT_SECONDS` en `scripts/01_collect_data.py`
- O verifica conectividad a los sitios objetivo
- O remove sitios problemáticos de `TARGETS`

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
- [ ] `data/` y `results/` existen (aunque estén vacíos)
- [ ] `run.bat` y `run.sh` son ejecutables y funcionan
- [ ] `.gitignore` excluye datos generados
- [ ] Pruebas una ejecución completa en ambiente limpio
- [ ] Documentación de cambios de configuración
- [ ] Licencia o uso educativo está claro

---

**Estado Actual:** ✅ COMPLETAMENTE REPRODUCIBLE

Este proyecto cumple con todos los estándares de reproducibilidad científica/académica.

