# PKI Clásica en TLS — Costo de Verificación de Certificados

## Objetivo del Experimento

Este proyecto constituye un estudio empírico del **costo operativo real de verificar certificados digitales en TLS 1.3** bajo distintos esquemas clásicos de autenticación y diferentes profundidades de cadena.

### Pregunta Central

¿Cuál es el impacto en latencia, tamaño de mensaje y escalabilidad de la autenticación al variar entre **esquemas RSA-2048 vs ECDSA P-256** con diferentes profundidades de cadena de certificados X.509?

### Enfoque Metodológico

El experimento trata la verificación de certificados como una **caja negra** y mide:
- **Latencia TCP + TLS handshake** (ms) en múltiples repeticiones
- **Profundidad de cadena** detectada (servidor + intermediarios)
- **Tamaño de certificados** en formato PEM y DER
- **Algoritmos de firma** identificados en el servidor

Los datos se recolectan contra **sitios HTTPS reales** permitiendo capturar escenarios de producción.

---

## Requisitos del Entorno

### Dependencias del Sistema

- **Python 3.7+** (probado con Python 3.9, 3.10, 3.11)
- **OpenSSL 1.1.1+** disponible en PATH
- **Conexión a Internet** para acceder a sitios HTTPS

### Verificación Rápida

```bash
python --version
openssl version
```

**First time setup?** → See [INSTALLATION.md](INSTALLATION.md) for platform-specific instructions.

### Instalación de Dependencias en Python

```bash
pip install -r requirements.txt
```

En Windows, si `pip` no está disponible:

```bash
python -m pip install -r requirements.txt
```

### Verificar Configuración

Antes de ejecutar el experimento, verifica que todo esté configurado:

```bash
python verify_environment.py
```

This will check:
- ✓ Python version
- ✓ OpenSSL availability
- ✓ Python packages (pandas, matplotlib)
- ✓ Project directories
- ✓ CA certificate bundle

---

## Estructura del Proyecto

```
TLS_PKI_Experiment/
│
├── README.md                      # Este archivo
├── requirements.txt               # Dependencias Python
│
├── scripts/
│   ├── __init__.py
│   ├── utils.py                   # Funciones compartidas (logging, CA bundle, helpers)
│   ├── 01_collect_data.py         # Script de ejecución: mediciones TLS
│   └── 02_analyze_results.py      # Script de análisis: estadísticas y gráficas
│
├── data/                          # Datos crudos generados por el experimento
│   ├── raw_web_results.csv        # Todos los handshakes (label, host, latency, depth, ...)
│   ├── chains_detectadas.csv      # Resumen de cadenas por sitio
│   └── fallos.csv                 # Errores durante mediciones
│
└── results/                       # Salidas regenerables (solo tablas y figuras)
    ├── resumen_estadistico.csv    # Estadísticas agregadas por sitio
    ├── comparativo_algoritmo.csv  # Comparación RSA vs ECDSA
    └── plots/                     # Visualizaciones PNG
        ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
        ├── boxplot_rsa_vs_ecdsa.png
        ├── promedio_medianas_por_algoritmo.png
        ├── tamano_der_promedio_rsa_vs_ecdsa.png
        ├── scatter_latencia_vs_der_por_algoritmo.png
        └── scatter_latencia_vs_profundidad_por_algoritmo.png
```

---

## Flujo de Ejecución End-to-End

### 1. Recolección de Datos (Mediciones TLS)

```bash
python scripts/01_collect_data.py
```

**Lo que hace:**
- Verifica disponibilidad de OpenSSL y Python
- Busca o descarga CA bundle para validación de certificados
- Inspecciona cada sitio HTTPS para detectar algoritmo y profundidad de cadena
- Ejecuta 1000 handshakes TLS 1.3 por sitio (configurable)
- Registra latencia, tamaños, profundidad y algoritmo en CSV

**Salidas generadas:**
- `data/raw_web_results.csv` — Todos los handshakes crudos
- `data/chains_detectadas.csv` — Resumen de cadenas por sitio
- `data/fallos.csv` — Errores durante ejecución
- Directorio de logs con detalles de OpenSSL

**Tiempo estimado:** 10–30 minutos dependiendo del número de sitios

### 2. Análisis y Visualización

```bash
python scripts/02_analyze_results.py
```

**Lo que hace:**
- Lee datos crudos desde `data/raw_web_results.csv`
- Calcula estadísticas por sitio: media, mediana, p95, desviación estándar
- Agrupa por algoritmo (RSA-2048 vs ECDSA P-256) para comparativas
- Genera 6 gráficas comparativas con matplotlib
- Exporta tablas a CSV

**Salidas generadas:**
- `results/resumen_estadistico.csv` — Tabla de estadísticas por sitio
- `results/comparativo_algoritmo.csv` — Comparación agregada por algoritmo
- `results/plots/` — Visualizaciones PNG

**Tiempo estimado:** <5 segundos

### Ejecución Completa en Una Línea

```bash
python scripts/01_collect_data.py && python scripts/02_analyze_results.py
```

---

## Descripción de Salidas

### Archivos de Datos (carpeta `data/`)

#### `raw_web_results.csv`
Registro completo de cada handshake TLS.

Columnas:
| Campo | Descripción |
|-------|-------------|
| `label` | Identificador del sitio (ej: "google") |
| `host` | Nombre de dominio (ej: "google.com") |
| `port` | Puerto (típicamente 443) |
| `repetition` | Número de repetición (1..1000) |
| `latency_ms` | Tiempo total TCP + TLS (milisegundos) |
| `detected_depth` | Profundidad de cadena (servidor + intermediarios - 1) |
| `cert_count` | Número de certificados en cadena |
| `server_cert_algorithm` | Algoritmo detectado (rsa2048, ecdsa_p256, other) |
| `chain_size_pem_bytes` | Tamaño completo de cadena en PEM |
| `chain_size_der_bytes` | Tamaño completo de cadena en DER |
| `tls_version` | Versión TLS (TLS1.3) |
| `verify_mode` | Modo de verificación (CAfile o insecure) |
| `returncode` | 0 si éxito, ERROR si fallo |

**Ejemplo:**
```csv
label,host,port,repetition,latency_ms,detected_depth,cert_count,server_cert_algorithm,chain_size_pem_bytes,chain_size_der_bytes,tls_version,verify_mode,returncode
google,google.com,443,1,85.234,1,2,ecdsa_p256,3245,1892,TLS1.3,CAfile,0
google,google.com,443,2,88.102,1,2,ecdsa_p256,3245,1892,TLS1.3,CAfile,0
```

#### `chains_detectadas.csv`
Resumen único de cada cadena detectada por sitio.

Columnas:
| Campo | Descripción |
|-------|-------------|
| `label` | Identificador del sitio |
| `host` | Nombre de dominio |
| `port` | Puerto |
| `detected_depth` | Profundidad de cadena |
| `cert_count` | Número de certificados |
| `server_cert_algorithm` | Algoritmo del certificado del servidor |
| `chain_size_pem_bytes` | Tamaño total en PEM |
| `chain_size_der_bytes` | Tamaño total en DER |
| `subjects` | Asuntos (DN) de los certificados separados por `\|` |

#### `fallos.csv`
Registro de errores durante mediciones.

Columnas: `stage`, `label`, `host`, `port`, `repetition`, `error`

---

### Archivos de Resultados (carpeta `results/`)

#### `resumen_estadistico.csv`
Estadísticas por sitio.

Columnas principales:
- `host`, `server_cert_algorithm`, `detected_depth`
- `n` (número de handshakes exitosos)
- `mean_ms`, `median_ms`, `stdev_ms`, `p95_ms`, `min_ms`, `max_ms`
- `pem_bytes`, `der_bytes`

#### `comparativo_algoritmo.csv`
Agregación por algoritmo para comparativa directa RSA vs ECDSA.

Columnas:
- `server_cert_algorithm`
- `sites` (número de sitios con ese algoritmo)
- `total_handshakes`
- `avg_median_ms`, `median_of_medians_ms`
- `avg_p95_ms`
- `avg_der_bytes`, `avg_depth`

#### Visualizaciones (`results/plots/`)

1. **comparativo_latencia_sitio_rsa_vs_ecdsa.png**  
   Gráfica de barras: latencia mediana por sitio, coloreada por algoritmo.

2. **boxplot_rsa_vs_ecdsa.png**  
   Boxplot: distribución de latencias para cada algoritmo (RSA vs ECDSA).

3. **promedio_medianas_por_algoritmo.png**  
   Barras: promedio de medianas por algoritmo.

4. **tamano_der_promedio_rsa_vs_ecdsa.png**  
   Barras: tamaño de cadena DER promedio por algoritmo.

5. **scatter_latencia_vs_der_por_algoritmo.png**  
   Scatter: latencia vs tamaño DER, con anotaciones de sitios.

6. **scatter_latencia_vs_profundidad_por_algoritmo.png**  
   Scatter: latencia vs profundidad, con anotaciones de sitios.

---

## Configuración

### Modificar Sitios Objetivo

Edita `scripts/01_collect_data.py` y ajusta la lista `TARGETS`:

```python
TARGETS = [
    {"label": "example", "host": "example.com", "port": 443},
    {"label": "google", "host": "google.com", "port": 443},
    # Agrega más aquí
]
```

### Modificar Número de Repeticiones

En `scripts/01_collect_data.py`:

```python
REPETITIONS = 1000  # Cambiar a tu valor
```

### Forzar Modo Inseguro (sin CA bundle)

En `scripts/01_collect_data.py`, comenta la verificación:

```python
# VERIFY_ARGS = ["-CAfile", str(CA_BUNDLE)]
VERIFY_ARGS = ["-verify", "0"]
```

---

## Reproducibilidad

Este proyecto garantiza **reproducibilidad completa** porque:

1. ✓ Todas las dependencias están listadas en `requirements.txt`
2. ✓ Scripts configurables sin hardcoding
3. ✓ Logs y fallos se registran para auditoría
4. ✓ Datos crudos y procesados están separados
5. ✓ README describe completamente entradas, salidas y pasos
6. ✓ No requiere información externa más allá de Internet para HTTPS

Para reproducir en otro entorno:

```bash
git clone <repo>
cd TLS_PKI_Experiment
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/01_collect_data.py
python scripts/02_analyze_results.py
```

---

## Notas Importantes

### Algoritmos Detectados

En internet real, el servidor **decide qué certificado entregar**. Es común encontrar:
- **rsa2048**: RSA con 2048 bits
- **ecdsa_p256**: ECDSA con curva P-256
- **other**: Otros algoritmos (RSA-4096, etc.)

Para **control total** sobre RSA vs ECDSA, usa un experimento local generando certificados con:
```bash
openssl genrsa -out key.pem 2048
openssl req -new -x509 -key key.pem -out cert.pem
```

### Validación de Certificados

El script:
- Busca CA bundle en locaciones estándar (Git, curl, sistema)
- Intenta descargar `cacert.pem` desde `curl.se` si no lo encuentra
- Fallback a modo inseguro (`-verify 0`) si no hay CA bundle

### Dependencia: OpenSSL

OpenSSL es esencial para:
- Inspeccionar cadenas de certificados (`s_client -showcerts`)
- Parsear X.509 (`x509 -text`, `-subject`)
- Convertir formatos (PEM ↔ DER)

En Windows, instálalo vía:
- Git for Windows (incluye OpenSSL)
- WSL (Windows Subsystem for Linux)
- instalador directo de OpenSSL.org

---

## Troubleshooting

### Error: "openssl no encontrado en PATH"

**Solución:** Instala OpenSSL o agrega su ruta a PATH.

En Windows con Git:
```powershell
$env:PATH += ";C:\Program Files\Git\usr\bin"
```

### Error: "No encontré CA bundle"

**Solución:** El script intentará descargar automáticamente. Si falla, descarga manualmente:
```bash
curl -o cacert.pem https://curl.se/ca/cacert.pem
```

y colócalo en el directorio raíz del proyecto.

### Timeout en mediciones

**Posible causa:** Red lenta o sitio inaccesible.

**Solución:** Aumenta `TIMEOUT_SECONDS` en `scripts/01_collect_data.py` o elimina sitios problemáticos de `TARGETS`.

### matplotlib no disponible

**Error:** "matplotlib no disponible"

**Solución:**
```bash
pip install matplotlib
```

Si usa requirements.txt está incluido pero puedes instalar manual.

---

## Referencias

- [RFC 5280](https://tools.ietf.org/html/rfc5280) — X.509 Public Key Infrastructure
- [RFC 8446](https://tools.ietf.org/html/rfc8446) — TLS 1.3
- [NIST SP 800-52R2](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-52r2.pdf) — Guidelines for TLS
- [OpenSSL Documentation](https://www.openssl.org/docs/)

---

## Licencia

Este proyecto es de uso educativo. Adapta según tus necesidades.

---

**Última actualización:** Mayo 2026

#   T L S _ P K I _ E x p e r i m e n t  
 #   T L S _ P K I _ E x p e r i m e n t  
 