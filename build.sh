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

# Descargar archivos LFS
echo "⬇️ Descargando archivos LFS (.pkl)..."
echo "🔄 Ejecutando: git lfs pull"
git lfs pull

# También intentar checkout manual
echo "🔄 Ejecutando: git lfs checkout"
git lfs checkout

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

# Instalar dependencias
pip install -r requirements.txt

# Verificar que los modelos estén presentes
echo "📊 Verificando modelos entrenados..."
if [ -d "models/trained" ]; then
    echo "✅ Directorio models/trained existe"
    ls -la models/trained/
    echo "📋 Total archivos .pkl: $(find models/trained -name '*.pkl' | wc -l)"
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
