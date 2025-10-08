# Instalación en macOS ARM64 (Apple Silicon M1/M2/M3)

## 🍎 Guía Específica para Mac con Apple Silicon

### ⚠️ Problema Común: LightGBM falla al instalar

Si ves este error:

```
ERROR: Failed building wheel for lightgbm
fatal error: can't open input file: ninja (No such file or directory)
CMake Error at CMakeLists.txt:35 (cmake_minimum_required)
```

**Causa:** LightGBM 4.1.0 no tiene wheels pre-compilados para ARM64 y falla al compilar.

**Solución:** Usamos LightGBM 4.3.0 que tiene wheels para ARM64.

## 📦 Instalación Paso a Paso (macOS ARM64)

### 1. Instalar Homebrew (si no lo tienes)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Instalar libomp (Requerido)

```bash
brew install libomp
```

### 3. Verificar que tienes Python correcto

```bash
# Debe mostrar arm64
python3 -c "import platform; print(platform.machine())"
```

**Salida esperada:** `arm64`

Si muestra `x86_64`, estás usando Python Intel (Rosetta). Instala Python ARM64:

```bash
# Opción 1: Desde Homebrew
brew install python@3.10

# Opción 2: Desde python.org (universal installer)
# Descarga: https://www.python.org/downloads/
```

### 4. Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar
source venv/bin/activate

# Verificar que es ARM64
python -c "import platform; print(platform.machine())"
```

### 5. Actualizar pip

```bash
pip install --upgrade pip setuptools wheel
```

### 6. Instalar Dependencias

```bash
# Opción A: Instalación normal (recomendada)
pip install -r requirements.txt

# Opción B: Si falla, instalar manualmente las problemáticas primero
pip install numpy==1.24.3
pip install pandas==2.1.4
pip install scipy==1.11.4
pip install scikit-learn==1.3.2
pip install lightgbm==4.3.0  # Versión con wheels para ARM64
pip install xgboost==2.0.3
pip install -r requirements.txt
```

### 7. Verificar Instalación

```bash
python verify_versions.py
```

## 🔧 Solución de Problemas Específicos

### Error: "libomp not found"

```bash
# Reinstalar libomp
brew reinstall libomp

# Crear symlink si es necesario
ln -sf /opt/homebrew/opt/libomp/lib/libomp.dylib /usr/local/lib/libomp.dylib
```

### Error: "Architecture mismatch"

Estás usando Python x86_64 (Intel) en Mac ARM64:

```bash
# Desactivar entorno actual
deactivate

# Remover entorno viejo
rm -rf venv

# Instalar Python ARM64 desde Homebrew
brew install python@3.10

# Usar explícitamente Python de Homebrew
/opt/homebrew/bin/python3 -m venv venv
source venv/bin/activate

# Verificar
python -c "import platform; print(platform.machine())"  # Debe ser arm64
```

### Error: "Command line tools not found"

```bash
# Instalar Xcode Command Line Tools
xcode-select --install

# Si ya están instalados, resetear
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install
```

### LightGBM aún falla (última opción)

Si LightGBM 4.3.0 también falla, puedes omitirlo temporalmente:

```bash
# Crear requirements_sin_lightgbm.txt
cat requirements.txt | grep -v lightgbm > requirements_sin_lightgbm.txt

# Instalar sin LightGBM
pip install -r requirements_sin_lightgbm.txt

# Intentar LightGBM 4.4.0 (más reciente)
pip install lightgbm==4.4.0

# O la última versión estable
pip install lightgbm
```

**NOTA:** Si usas una versión diferente de LightGBM, los modelos pueden dar resultados ligeramente diferentes.

## 🧪 Verificación Completa

### Script de Verificación Detallado

```bash
# 1. Verificar arquitectura
echo "Arquitectura:"
python -c "import platform; print(f'  Python: {platform.machine()}')"
uname -m

# 2. Verificar versiones
echo -e "\nVersiones instaladas:"
python -c "
import numpy as np
import pandas as pd
import sklearn
import lightgbm as lgb
import xgboost as xgb

print(f'  NumPy: {np.__version__}')
print(f'  Pandas: {pd.__version__}')
print(f'  Scikit-learn: {sklearn.__version__}')
print(f'  LightGBM: {lgb.__version__}')
print(f'  XGBoost: {xgb.__version__}')
"

# 3. Verificar que libomp está disponible
echo -e "\nLibOMP:"
ls -la /opt/homebrew/opt/libomp/lib/libomp.dylib 2>/dev/null && echo "  ✅ Encontrado" || echo "  ❌ No encontrado"

# 4. Probar LightGBM
echo -e "\nProbando LightGBM:"
python -c "import lightgbm as lgb; print('  ✅ LightGBM funciona')" 2>/dev/null || echo "  ❌ LightGBM falla"

# 5. Ejecutar verificación completa
echo -e "\nVerificación completa:"
python verify_versions.py
```

## 📋 Checklist de Instalación

- [ ] Homebrew instalado
- [ ] libomp instalado (`brew install libomp`)
- [ ] Python ARM64 verificado (`platform.machine() == 'arm64'`)
- [ ] Entorno virtual creado y activado
- [ ] pip actualizado (`pip install --upgrade pip`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Versiones verificadas (`python verify_versions.py`)
- [ ] Modelos .pkl cargan correctamente

## 🚀 Comando Rápido (Todo en Uno)

```bash
# Copia y pega esto para instalación completa
brew install libomp python@3.10 && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip setuptools wheel && \
pip install -r requirements.txt && \
python verify_versions.py && \
echo -e "\n✅ Instalación completa. Ejecuta: python run_app.py"
```

## 📊 Comparación de Versiones LightGBM

| Versión | Wheels ARM64 | Compatible | Notas                        |
| ------- | ------------ | ---------- | ---------------------------- |
| 4.1.0   | ❌ No        | ❌         | Requiere compilación (falla) |
| 4.2.0   | ❌ No        | ❌         | Requiere compilación         |
| 4.3.0   | ✅ Sí        | ✅         | **Recomendada para ARM64**   |
| 4.4.0   | ✅ Sí        | ✅         | Más reciente, compatible     |
| Latest  | ✅ Sí        | ⚠️         | Puede tener API changes      |

## 🔍 Debugging

### Ver log completo de instalación

```bash
pip install -r requirements.txt --verbose 2>&1 | tee install.log
```

### Ver qué wheel se descarga

```bash
pip install lightgbm==4.3.0 --verbose 2>&1 | grep "Downloading\|Using cached"
```

**Debe mostrar:**

```
Using cached lightgbm-4.3.0-py3-none-macosx_12_0_arm64.whl
```

Si muestra `tar.gz` o intenta compilar, hay un problema con la arquitectura.

## 💡 Tips Adicionales

### Usar Python de Homebrew explícitamente

```bash
# Agregar a ~/.zshrc o ~/.bash_profile
export PATH="/opt/homebrew/opt/python@3.10/bin:$PATH"
alias python=/opt/homebrew/opt/python@3.10/bin/python3
alias pip=/opt/homebrew/opt/python@3.10/bin/pip3
```

### Limpiar cache de pip

```bash
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### Forzar reinstalación limpia

```bash
pip uninstall -y numpy pandas scipy scikit-learn lightgbm xgboost
pip install --no-cache-dir -r requirements.txt
```

## 📞 Soporte

Si ninguna solución funciona:

1. **Verifica arquitectura:** `python -c "import platform; print(platform.machine())"`
2. **Genera log:** `pip install -r requirements.txt --verbose > install.log 2>&1`
3. **Comparte:** El contenido de `install.log`

## ✅ Éxito

Si ves esto, ¡estás listo! 🎉

```
✅ TODAS LAS VERSIONES SON CORRECTAS
======================================================================
✅ TODOS LOS MODELOS SE CARGARON CORRECTAMENTE
======================================================================
🎉 SISTEMA LISTO PARA USAR
```

Ejecuta la app:

```bash
python run_app.py
```
