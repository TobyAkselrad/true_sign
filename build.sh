#!/bin/bash
# Build script para Render

echo "🚀 Iniciando build de TrueSign..."
echo "📂 Current directory: $(pwd)"
echo "📂 Git directory: $(git rev-parse --show-toplevel 2>/dev/null || echo 'No git')"

# Instalar Git LFS y dependencias del sistema
echo "📥 Instalando Git LFS y Chromium..."
apt-get update -qq
apt-get install -y -qq git-lfs chromium-browser chromium-chromedriver xvfb

echo "✅ Dependencias del sistema instaladas"

# Inicializar Git LFS
echo "🔄 Inicializando Git LFS..."
git lfs install

# Verificar que Git LFS está funcionando
echo "🔍 Verificando estado de Git LFS..."
git lfs env

# Descargar archivos LFS
echo "⬇️ Descargando archivos LFS (.pkl)..."
echo "🔄 Ejecutando: git lfs fetch --all"
git lfs fetch --all

echo "🔄 Ejecutando: git lfs pull"
git lfs pull

# También intentar checkout manual
echo "🔄 Ejecutando: git lfs checkout"
git lfs checkout

# Verificar archivos específicos
echo "🔍 Verificando archivos LFS..."
git lfs ls-files

# Forzar checkout de archivos específicos
echo "📥 Forzando descarga de modelos grandes..."
if [ -f "models/trained/maximum_price_model.pkl" ]; then
    echo "✅ maximum_price_model.pkl presente"
else
    echo "⚠️ maximum_price_model.pkl faltante, intentando descargar..."
    git lfs pull --include="models/trained/maximum_price_model.pkl" || echo "❌ No se pudo descargar"
fi

if [ -f "models/trained/value_change_model.pkl" ]; then
    echo "✅ value_change_model.pkl presente"  
else
    echo "⚠️ value_change_model.pkl faltante, intentando descargar..."
    git lfs pull --include="models/trained/value_change_model.pkl" || echo "❌ No se pudo descargar"
fi

# Listar archivos descargados
echo "📋 Archivos en models/trained después de git lfs checkout:"
ls -la models/trained/ || echo "⚠️ models/trained no existe todavía"

# Instalar dependencias de Python PRIMERO
echo "📦 Instalando dependencias de Python..."
pip install -r requirements.txt

# Verificar si los modelos grandes están presentes
echo "🔍 Verificando si los modelos grandes están presentes..."
if [ ! -f "models/trained/value_change_model.pkl" ] || [ ! -s "models/trained/value_change_model.pkl" ]; then
    echo "⚠️ value_change_model.pkl no encontrado, intentando extraer de archivo comprimido..."
    
    # Intentar descargar desde archivo comprimido si existe
    if [ -f "data/models_compressed.tar.gz.partaa" ]; then
        echo "📦 Juntando partes del archivo comprimido..."
        cat data/models_compressed.tar.gz.part* > data/models_compressed.tar.gz
        echo "📦 Extrayendo modelos desde archivo comprimido..."
        tar -xzf data/models_compressed.tar.gz -C models/trained/
        echo "✅ Modelos extraídos"
    fi
    
    # Si aún no están, intentar LFS
    if [ ! -f "models/trained/value_change_model.pkl" ] || [ ! -s "models/trained/value_change_model.pkl" ]; then
        echo "⚠️ Reintentando descarga desde Git LFS..."
        git lfs pull --include="models/trained/value_change_model.pkl" || true
    fi
fi

if [ ! -f "models/trained/maximum_price_model.pkl" ] || [ ! -s "models/trained/maximum_price_model.pkl" ]; then
    echo "⚠️ maximum_price_model.pkl no encontrado, intentando extraer de archivo comprimido..."
    
    if [ -f "data/models_compressed.tar.gz.partaa" ]; then
        echo "📦 Juntando partes del archivo comprimido..."
        cat data/models_compressed.tar.gz.part* > data/models_compressed.tar.gz
        echo "📦 Extrayendo modelos desde archivo comprimido..."
        tar -xzf data/models_compressed.tar.gz -C models/trained/
        echo "✅ Modelos extraídos"
    fi
    
    if [ ! -f "models/trained/maximum_price_model.pkl" ] || [ ! -s "models/trained/maximum_price_model.pkl" ]; then
        echo "⚠️ Reintentando descarga desde Git LFS..."
        git lfs pull --include="models/trained/maximum_price_model.pkl" || true
    fi
fi

# Verificar que los modelos estén presentes
echo "📊 Verificando modelos entrenados..."
if [ -d "models/trained" ]; then
    echo "✅ Directorio models/trained existe"
    ls -lah models/trained/
    echo "📋 Total archivos .pkl: $(find models/trained -name '*.pkl' | wc -l)"
    
    # Verificar archivos críticos
    if [ ! -f "models/trained/value_change_model.pkl" ]; then
        echo "❌ ERROR CRÍTICO: value_change_model.pkl faltante"
        echo "🔄 Intentando verificación adicional de Git LFS..."
        git lfs pull --include="models/trained/value_change_model.pkl"
        git lfs checkout models/trained/value_change_model.pkl
    fi
    
    if [ ! -f "models/trained/maximum_price_model.pkl" ]; then
        echo "❌ ERROR CRÍTICO: maximum_price_model.pkl faltante"
        echo "🔄 Intentando verificación adicional de Git LFS..."
        git lfs pull --include="models/trained/maximum_price_model.pkl"
        git lfs checkout models/trained/maximum_price_model.pkl
    fi
    
    # Verificar tamaño de archivos (no deben ser solo pointers)
    if [ -f "models/trained/value_change_model.pkl" ]; then
        SIZE=$(stat -f%z models/trained/value_change_model.pkl 2>/dev/null || stat -c%s models/trained/value_change_model.pkl 2>/dev/null || echo "0")
        if [ "$SIZE" -lt 1000000 ]; then
            echo "⚠️ WARNING: value_change_model.pkl parece ser un pointer de LFS en lugar del archivo real"
            echo "   Tamaño: $SIZE bytes"
        else
            echo "✅ value_change_model.pkl tiene tamaño correcto: $SIZE bytes"
        fi
    fi
    
    if [ -f "models/trained/maximum_price_model.pkl" ]; then
        SIZE=$(stat -f%z models/trained/maximum_price_model.pkl 2>/dev/null || stat -c%s models/trained/maximum_price_model.pkl 2>/dev/null || echo "0")
        if [ "$SIZE" -lt 10000000 ]; then
            echo "⚠️ WARNING: maximum_price_model.pkl parece ser un pointer de LFS en lugar del archivo real"
            echo "   Tamaño: $SIZE bytes"
        else
            echo "✅ maximum_price_model.pkl tiene tamaño correcto: $SIZE bytes"
        fi
    fi
    
else
    echo "❌ ERROR: Directorio models/trained no existe"
    exit 1
fi

# Verificar que el archivo principal existe
if [ ! -f "app/run.py" ]; then
    echo "❌ Error: app/run.py no encontrado"
    exit 1
fi

echo "✅ Build completado exitosamente"
