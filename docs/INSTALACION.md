# Instalación de TrueSign

## ⚠️ IMPORTANTE: Compatibilidad de Modelos ML

Los modelos de machine learning (.pkl) fueron entrenados con **versiones específicas** de las librerías. Es **CRÍTICO** instalar las versiones exactas especificadas en `requirements.txt` o la aplicación fallará.

## Requisitos Previos

- **Python 3.8 - 3.10** (Recomendado: 3.9)
- **pip** actualizado
- **macOS**: Homebrew y libomp (ver abajo)

## Instalación

### 1. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. Actualizar pip

```bash
pip install --upgrade pip
```

### 3. macOS: Instalar libomp (Requerido para LightGBM)

```bash
brew install libomp
```

### 4. Instalar Dependencias (VERSIONES EXACTAS)

**IMPORTANTE:** Usa `--force-reinstall` para asegurar versiones exactas:

```bash
pip install -r requirements.txt --force-reinstall
```

## Verificación de Instalación

### Verificar Versiones Críticas

Ejecuta este script para verificar que las versiones sean correctas:

```python
import sys
import numpy as np
import pandas as pd
import sklearn
import lightgbm as lgb
import xgboost as xgb

print(f"Python: {sys.version}")
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print(f"LightGBM: {lgb.__version__}")
print(f"XGBoost: {xgb.__version__}")

# Verificar que sean las versiones exactas
assert np.__version__ == "1.24.3", f"❌ NumPy incorrecto: {np.__version__} != 1.24.3"
assert pd.__version__ == "2.1.4", f"❌ Pandas incorrecto: {pd.__version__} != 2.1.4"
assert sklearn.__version__ == "1.3.2", f"❌ Scikit-learn incorrecto: {sklearn.__version__} != 1.3.2"
assert lgb.__version__ == "4.1.0", f"❌ LightGBM incorrecto: {lgb.__version__} != 4.1.0"
assert xgb.__version__ == "2.0.3", f"❌ XGBoost incorrecto: {xgb.__version__} != 2.0.3"

print("\n✅ Todas las versiones son correctas!")
```

Guarda como `verify_versions.py` y ejecuta:

```bash
python verify_versions.py
```

### Probar Carga de Modelos

```bash
# Probar ValueChangePredictor
python value_change_predictor_real.py

# Probar UltimateTransferModel
python ultimate_transfer_model_real.py

# Probar HybridROIModel
python hybrid_roi_model_real.py
```

Si todos pasan sin errores, los modelos se cargan correctamente.

## Ejecutar la Aplicación

```bash
python run_app.py
```

La aplicación estará disponible en: `http://localhost:5001`

## Problemas Comunes

### Error: "MT19937" o "BitGenerator"

**Causa:** Versión incorrecta de NumPy

**Solución:**

```bash
pip uninstall numpy
pip install numpy==1.24.3
```

### Error: "Unknown label type" o "Invalid parameter"

**Causa:** Versión incorrecta de scikit-learn

**Solución:**

```bash
pip uninstall scikit-learn
pip install scikit-learn==1.3.2
```

### Error al cargar modelos .pkl

**Causa:** Versiones incompatibles de librerías ML

**Solución completa:**

```bash
# Desinstalar todas las librerías ML
pip uninstall numpy pandas scipy scikit-learn lightgbm xgboost -y

# Reinstalar con versiones exactas
pip install -r requirements.txt --no-cache-dir --force-reinstall
```

### macOS: Error con LightGBM "libomp not found"

**Solución:**

```bash
brew install libomp

# Si ya está instalado:
brew reinstall libomp

# Crear symlinks si es necesario:
ln -s /opt/homebrew/opt/libomp/lib/libomp.dylib /usr/local/lib/libomp.dylib
```

### Windows: Error con LightGBM

**Solución:**

1. Instalar Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Reinstalar LightGBM:

```bash
pip install --upgrade --force-reinstall lightgbm==4.1.0
```

## Tabla de Versiones Requeridas

| Librería       | Versión | Crítica  | Motivo                                   |
| -------------- | ------- | -------- | ---------------------------------------- |
| numpy          | 1.24.3  | ✅ SÍ    | Serialización de modelos .pkl            |
| pandas         | 2.1.4   | ✅ SÍ    | Formato de datos en modelos              |
| scikit-learn   | 1.3.2   | ✅ SÍ    | Modelos ML (ensemble, RF, GB)            |
| scipy          | 1.11.4  | ✅ SÍ    | Dependencia de scikit-learn              |
| lightgbm       | 4.1.0   | ✅ SÍ    | Modelo LightGBM                          |
| xgboost        | 2.0.3   | ⚠️ Media | Modelo XGBoost (más tolerante)           |
| Flask          | 2.3.3   | ❌ NO    | Framework web (compatible con versiones) |
| requests       | 2.31.0  | ❌ NO    | HTTP requests (compatible con versiones) |
| beautifulsoup4 | 4.12.2  | ❌ NO    | Parsing HTML (compatible con versiones)  |

## Re-entrenar Modelos (Alternativa)

Si no puedes usar las versiones específicas, puedes re-entrenar los modelos con tus versiones actuales:

**NOTA:** Esto cambiará las predicciones y puede afectar la precisión.

1. Contacta al equipo de data science para el dataset de entrenamiento
2. Ejecuta los scripts de entrenamiento con tus versiones
3. Reemplaza los archivos .pkl en `saved_models_old/`

## Despliegue en Producción

### Opción 1: Render/Heroku

Asegúrate que `requirements.txt` tenga las versiones exactas (sin `~`, `>=`, etc.)

### Opción 2: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema (para LightGBM)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_app.py"]
```

## Soporte

Si tienes problemas de compatibilidad:

1. Verifica versiones con `pip list`
2. Ejecuta `verify_versions.py`
3. Revisa logs de error completos
4. Usa `--force-reinstall` si es necesario

## Notas de Desarrollo

- **NO actualices** las versiones de ML sin re-entrenar modelos
- Usa `pip freeze > requirements_actual.txt` para debug
- Mantén un entorno virtual limpio para evitar conflictos
- Python 3.11+ puede tener problemas - usa 3.9 o 3.10
