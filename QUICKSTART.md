# Guía rápida de inicio

## Configuración (5 minutos) + ejecución del experimento (~20 minutos)

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Verificar Entorno (opcional pero recomendado)
```bash
python verify_environment.py
```

Esto verifica versión de Python, OpenSSL, paquetes y directorios. Ver [INSTALLATION.md](INSTALLATION.md) para instalación por plataforma.

### 3. Ejecutar Experimento Completo

**Windows:**
```bash
run.bat
```

**Linux/macOS:**
```bash
# Primera vez: hacer script ejecutable
chmod +x run.sh

# Luego ejecutar:
./run.sh
```

**O manualmente (todas las plataformas):**
```bash
python scripts/main.py
```

### 4. Esperar Resultados (~15-20 minutos)

El script hará:
- Medir 10 sitios web × 1000 handshakes cada uno
- Mostrar progreso en la terminal
- Crear una carpeta con marca de tiempo con todas las salidas

**Ejemplo de carpeta de salida:**
```
tls_web_tls13_rsa_ecdsa_20260519_200420/
├── results/
│   ├── raw_web_results.csv           ← Todos los 10,000 mediciones
│   ├── resumen_web_estadistico.csv   ← Estadísticas por sitio
│   ├── comparativo_algoritmo.csv     ← Comparación RSA vs ECDSA
│   └── ...
├── plots/
│   ├── comparativo_latencia_sitio_rsa_vs_ecdsa.png
│   ├── boxplot_rsa_vs_ecdsa.png
│   └── ... (4 más archivos PNG)
└── logs/
```

## Solución de problemas

### OpenSSL no encontrado
- **Windows:** Instalar Git for Windows (incluye OpenSSL)
- **Linux:** `sudo apt-get install openssl`
- **macOS:** `brew install openssl`

### matplotlib no disponible
```bash
pip install matplotlib
```

### Problemas de red
Editar `scripts/main.py` y modificar la lista `TARGETS` o aumentar `TIMEOUT_SECONDS`.

## Configuración Personalizada

### Cambiar número de repeticiones
Editar `scripts/main.py`:
```python
REPETITIONS = 500  # por defecto es 1000
```

### Agregar/remover sitios web
Editar `scripts/main.py`:
```python
TARGETS = [
    {"label": "example", "host": "example.com", "port": 443},
    # Agrega tus propios sitios aquí
]
```

### Aumentar timeout
Editar `scripts/main.py`:
```python
TIMEOUT_SECONDS = 15  # por defecto es 10
```

## Interpretación de Salida

- **resumen_web_estadistico.csv**: Estadísticas por sitio (mediana, p95, desviación estándar, etc.)
- **comparativo_algoritmo.csv**: Comparación RSA vs ECDSA
- **plots/**: Comparativas visuales de latencia, tamaño y profundidad

Ver README.md para descripciones detalladas de columnas.

