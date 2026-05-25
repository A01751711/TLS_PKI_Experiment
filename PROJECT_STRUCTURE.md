# Resumen de la estructura del proyecto

```
TLS_PKI_Experiment/
│
├── 📄 README.md                    ★ Documentación principal
├── 📄 QUICKSTART.md                ★ Inicio en 5 minutos
├── 📄 INSTALLATION.md              ★ Instalación por plataforma
├── 📄 verify_environment.py        ★ Verificación previa
├── 📄 requirements.txt             ★ Dependencias Python
├── 📄 .gitignore                   ★ Exclusiones de Git
│
├── 🔨 run.bat                      ★ Ejecución en un clic (Windows)
├── 🔨 run.sh                       ★ Ejecución en un clic (Linux/macOS)
│
├── 📁 scripts/
│   └── 📜 main.py                  ★ Flujo completo del experimento
│       ├── Verificar dependencias (OpenSSL, Python)
│       ├── Configurar bundle CA
│       ├── Inspeccionar cadenas en servidores reales
│       ├── 1000 mediciones TLS por sitio
│       ├── Calcular estadísticas (media, mediana, p95, desv.)
│       ├── Comparar RSA-2048 vs ECDSA P-256
│       ├── Generar 6 gráficas con matplotlib
│       └── Exportar a carpeta con timestamp
│
└── 🔍 Generado en cada ejecución:
    └── tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/
        │
        ├── 📁 results/             ★ CSV y análisis
        │   ├── raw_web_results.csv
        │   ├── chains_detectadas.csv
        │   ├── fallos.csv
        │   ├── resumen_web_estadistico.csv
        │   └── comparativo_algoritmo.csv
        │
        ├── 📁 plots/               ★ 6 PNG comparativos
        │   ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
        │   ├── boxplot_rsa_vs_ecdsa.png
        │   ├── promedio_medianas_por_algoritmo.png
        │   ├── tamano_der_promedio_rsa_vs_ecdsa.png
        │   ├── scatter_latencia_vs_der_por_algoritmo.png
        │   └── scatter_latencia_vs_profundidad_por_algoritmo.png
        │
        ├── 📁 logs/
        │   ├── inspect_*.log
        │   └── client_*.log
        │
        └── 📁 certs_extraidos/
```

## Decisiones de diseño

### ✓ Script unificado

- **main.py:** medición, análisis y visualización en un solo archivo
- Sin dependencias entre varios scripts
- Ejecución: `python scripts/main.py`, `run.bat` o `run.sh`

### ✓ Carpetas de salida con timestamp

- Cada ejecución crea `tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/`
- Permite comparar varias corridas sin sobrescribir datos
- Ejemplo: `tls_web_tls13_rsa_ecdsa_20260519_200420/`

### ✓ Organización de datos (dentro de la carpeta con marca de tiempo)

- **results/** — CSV y tablas procesadas
- **plots/** — Gráficas PNG (hermana de `results/`, no dentro de ella)
- **logs/** — Traza OpenSSL para depuración
- **certs_extraidos/** — Certificados PEM por sitio

### ✓ Reproducibilidad

- Dependencias en `requirements.txt`
- Detección y descarga automática del bundle CA
- Registro de errores en `results/fallos.csv`
- **run.bat** / **run.sh** para ejecución en un comando

### ✓ Multiplataforma

- Windows, Linux y macOS
- Python 3.7+
- Scripts de lanzamiento por SO

---

## Flujo de ejecución

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario: .\run.bat  (o bash run.sh en Linux/macOS)          │
│ (o directamente: python scripts/main.py)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │ scripts/main.py                │
        ├────────────────────────────────┤
        │ 1. Verificar OpenSSL + Python  │
        │ 2. Configurar bundle CA        │
        │ 3. Inspeccionar 10 sitios HTTPS│
        │ 4. 1000 handshakes × 10 sitios │
        │ 5. Calcular estadísticas       │
        │ 6. Generar gráficas            │
        │ 7. Exportar resultados         │
        └────────────┬───────────────────┘
                     │
                     ▼
        tls_web_tls13_rsa_ecdsa_YYYYMMDD_HHMMSS/
        ├── results/
        ├── plots/
        ├── logs/
        └── certs_extraidos/
                     │
                     ▼
                ┌─────────────┐
                │ ✓ Completo  │
                └─────────────┘
```

---

## Tamaños aproximados por ejecución

| Archivo / carpeta | Tamaño | Notas |
|-------------------|--------|-------|
| results/raw_web_results.csv | ~2–5 MB | >10 000 filas |
| results/chains_detectadas.csv | ~10 KB | ~10 sitios |
| results/fallos.csv | ~1–50 KB | Vacío si no hay errores |
| results/resumen_web_estadistico.csv | ~15 KB | |
| results/comparativo_algoritmo.csv | ~1 KB | |
| plots/*.png | ~200–400 KB c/u | 6 gráficas @ 150 DPI |
| logs/ | ~1–5 MB | |
| certs_extraidos/ | ~500 KB | |

**Uso de disco por corrida:** ~10–15 MB

---

## Pasos para el usuario

1. ✓ Revisar [README.md](README.md)
2. ✓ `pip install -r requirements.txt`
3. ✓ `python verify_environment.py`
4. ✓ Ejecutar: `.\run.bat` (Windows) o `bash run.sh` (Linux/macOS)
5. ✓ Revisar la carpeta `tls_web_tls13_rsa_ecdsa_*` más reciente
6. ✓ Personalizar `TARGETS` y `REPETITIONS` en `scripts/main.py`

**Última actualización:** Mayo 2026
