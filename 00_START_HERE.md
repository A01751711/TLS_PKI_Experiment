# 🚀 Empieza aquí — Experimento TLS PKI

## Qué incluye este proyecto

Estructura de investigación **reproducible** para medir el costo de verificación de certificados X.509 en TLS 1.3.

### ✅ Estructura del repositorio

```
TLS_PKI_Experiment/
├── 📚 Documentación/
│   ├── README.md                    ← Referencia técnica completa
│   ├── QUICKSTART.md                ← Inicio en 5 minutos
│   ├── INSTALLATION.md              ← Instalación por plataforma
│   ├── PROJECT_STRUCTURE.md         ← Arquitectura y flujo
│   ├── REPRODUCIBILITY_CHECKLIST.md ← Validación de reproducibilidad
│   ├── REPRODUCIBILITY_GITHUB.md    ← Reproducibilidad al publicar en GitHub
│   └── PRE_GITHUB_CHECKLIST.md      ← Lista previa a subir el repositorio
│
├── 📦 Código/
│   ├── requirements.txt             ← Dependencias Python
│   ├── verify_environment.py        ← Verificación previa al experimento
│   └── scripts/
│       └── main.py                  ← Experimento completo (medición + análisis)
│
├── 🔄 Ejecución/
│   ├── run.bat                      ← Un clic en Windows
│   └── run.sh                       ← Un clic en Linux/macOS
│
└── 📂 Generado al ejecutar (carpeta con timestamp)/
    └── tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/
        ├── results/                 ← CSV y análisis
        ├── plots/                   ← 6 gráficas PNG
        ├── logs/                    ← Logs de OpenSSL
        └── certs_extraidos/         ← Certificados extraídos
```

---

## 🎯 Inicio rápido (5 minutos)

### Paso 1: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Verificar entorno

```bash
python verify_environment.py
```

Comprueba Python, OpenSSL, paquetes y directorios. Ver [INSTALLATION.md](INSTALLATION.md) para ayuda por plataforma.

### Paso 3: Ejecutar el experimento

```bash
# Windows (PowerShell o CMD):
.\run.bat

# Linux/macOS:
chmod +x run.sh
bash run.sh
```

### Paso 4: Revisar resultados

Cada ejecución crea una **carpeta con timestamp** con todas las salidas:

```
tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/
├── results/
│   ├── raw_web_results.csv           ← ~10 000 mediciones de handshake
│   ├── resumen_web_estadistico.csv   ← Estadísticas por sitio
│   ├── comparativo_algoritmo.csv     ← Comparación RSA vs ECDSA
│   ├── chains_detectadas.csv         ← Resumen de cadenas
│   └── fallos.csv                    ← Errores (si los hay)
├── plots/
│   ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
│   ├── boxplot_rsa_vs_ecdsa.png
│   ├── promedio_medianas_por_algoritmo.png
│   ├── tamano_der_promedio_rsa_vs_ecdsa.png
│   ├── scatter_latencia_vs_der_por_algoritmo.png
│   └── scatter_latencia_vs_profundidad_por_algoritmo.png
├── logs/
│   ├── inspect_*.log
│   └── client_*.log
└── certs_extraidos/
    └── [certificados_por_sitio]/
```

**Nota:** Cada ejecución genera una carpeta nueva; puedes comparar varias corridas.

---

## ⚙️ Qué ocurre al ejecutar

**Comando único (equivalente a `run.bat` / `run.sh`):**

```bash
python scripts/main.py
```

**El script realiza:**

1. ✅ Verifica Python y OpenSSL
2. ✅ Localiza o descarga el bundle de certificados CA
3. ✅ Inspecciona 10 sitios HTTPS reales (TLS 1.3)
4. ✅ Mide 1000 handshakes por sitio (~15 min)
5. ✅ Calcula estadísticas y comparaciones
6. ✅ Genera 6 gráficas comparativas
7. ✅ Exporta todo a la carpeta con timestamp

**Salida de ejemplo:** `tls_web_tls13_rsa_ecdsa_20260519_200420/`

---

## 📋 Qué hace cada archivo

### Script principal (`scripts/main.py`)

Un solo archivo con todo el flujo:
- Verificación de dependencias (OpenSSL, Python)
- Configuración del bundle CA
- Inspección de cadenas en sitios HTTPS
- Mediciones de handshake TLS 1.3
- Estadísticas y gráficas
- Exportación a CSV y PNG

### Documentación

| Archivo | Para qué leerlo |
|---------|-----------------|
| **README.md** | Objetivo, metodología, salidas, configuración |
| **QUICKSTART.md** | Pasos mínimos en 5 minutos |
| **INSTALLATION.md** | Instalación Windows / Linux / macOS |
| **PROJECT_STRUCTURE.md** | Diagrama y decisiones de diseño |
| **REPRODUCIBILITY_CHECKLIST.md** | Validación de reproducibilidad |
| **REPRODUCIBILITY_GITHUB.md** | Reproducibilidad al publicar en GitHub |
| **PRE_GITHUB_CHECKLIST.md** | Lista previa a subir el repositorio |

---

## 🔧 Configuración

### Cambiar sitios objetivo

Edita `scripts/main.py`:

```python
TARGETS = [
    {"label": "google", "host": "google.com", "port": 443},
    # Agrega tus propios sitios aquí
]
```

### Cambiar número de mediciones

```python
REPETITIONS = 1000  # Cambia al valor deseado
```

### Aumentar timeout (redes lentas)

```python
TIMEOUT_SECONDS = 15  # Por defecto: 10
```

---

## 📊 Interpretación de salidas

Rutas relativas a la carpeta con timestamp (ej. `tls_web_tls13_rsa_ecdsa_20260519_200420/`).

### Archivos CSV (en `results/`)

**`results/resumen_web_estadistico.csv`**

```
host,algorithm,n,median_ms,p95_ms,der_bytes
google.com,ecdsa_p256,1000,85.234,95.102,1892
github.com,rsa2048,1000,92.445,105.330,2145
...
```

**`results/comparativo_algoritmo.csv`**

```
algorithm,sites,total_handshakes,avg_median_ms,avg_der_bytes
rsa2048,5,5000,91.2,2100
ecdsa_p256,4,4000,87.5,1950
```

### Gráficas PNG (en `plots/`)

1. **comparativo_latencia_sitio_rsa_vs_ecdsa.png** — Latencia mediana por sitio
2. **boxplot_rsa_vs_ecdsa.png** — Distribución de latencias por algoritmo
3. **promedio_medianas_por_algoritmo.png** — Promedio de medianas por algoritmo
4. **tamano_der_promedio_rsa_vs_ecdsa.png** — Tamaño medio de cadena DER
5. **scatter_latencia_vs_der_por_algoritmo.png** — Latencia vs tamaño DER
6. **scatter_latencia_vs_profundidad_por_algoritmo.png** — Latencia vs profundidad de cadena

---

## ❓ Solución de problemas

### «openssl no encontrado»

- **Windows:** [Git for Windows](https://git-scm.com/download/win) (incluye OpenSSL)
- **Linux:** `sudo apt-get install openssl`
- **macOS:** `brew install openssl`

### «matplotlib no disponible»

```bash
pip install matplotlib
```

### Timeout de red

- Edita `TIMEOUT_SECONDS` en `scripts/main.py`
- Comprueba la conexión a internet
- Quita sitios problemáticos de `TARGETS`

### «No se encontró CA bundle»

El script intenta descargarlo automáticamente. Si falla:

```bash
curl -o cacert.pem https://curl.se/ca/cacert.pem
```

Coloca `cacert.pem` en la raíz del proyecto.

---

## 🔐 Por qué esta estructura

### ✅ Reproducible

- Cualquiera puede clonar o descargar el ZIP y repetir el experimento
- Dependencias listadas en `requirements.txt`
- Decisiones y errores registrados en `logs/` y `results/fallos.csv`

### ✅ Profesional

- Un solo script (`main.py`) con el flujo completo
- Documentación en español
- Salidas organizadas por ejecución (timestamp)

### ✅ Mantenible

- Configuración centralizada en `TARGETS`, `REPETITIONS`, `TIMEOUT_SECONDS`
- Sin módulos auxiliares que desincronicen la documentación

### ✅ Orientado a investigación

- Datos crudos (`raw_web_results.csv`) separados de resúmenes
- Metadatos en encabezados CSV
- Gráficas listas para informes

---

## 📆 Próximos pasos

1. ✅ Lee [README.md](README.md) para el detalle técnico
2. ✅ Ejecuta `.\run.bat` (Windows) o `bash run.sh` (Linux/macOS)
3. ✅ Abre la carpeta `tls_web_tls13_rsa_ecdsa_*` más reciente
4. ✅ Personaliza `TARGETS` o `REPETITIONS` si lo necesitas
5. ✅ Usa [REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md) antes de publicar

---

## 📞 Ayuda

- [QUICKSTART.md](QUICKSTART.md) — Problemas frecuentes de arranque
- [README.md](README.md) — Documentación completa
- [INSTALLATION.md](INSTALLATION.md) — Instalación por SO
- Comentarios en `scripts/main.py` y `verify_environment.py`

---

## 📝 Información del proyecto

**Objetivo:** Medir el costo operativo de la verificación de certificados X.509 en TLS 1.3 con RSA-2048 frente a ECDSA P-256 y distintas profundidades de cadena.

**Metodología:** Mediciones empíricas sobre conexiones HTTPS reales (caja negra): latencia, tamaños de mensaje y metadatos de cadena.

**Salida:** Análisis estadístico y visualizaciones comparativas RSA vs ECDSA.

**Datos:** Más de 10 000 mediciones en ~10 sitios web.

---

**Estado:** ✅ Listo para usar  
**Última actualización:** Mayo 2026
