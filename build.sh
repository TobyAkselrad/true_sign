#!/bin/bash
# Build script para Render

echo "🚀 Iniciando build de TrueSign..."

# Instalar Git LFS primero (necesario para descargar archivos grandes)
echo "📥 Instalando Git LFS..."
apt-get update -qq
apt-get install -y -qq git-lfs

# Inicializar Git LFS
git lfs install
git lfs pull || echo "⚠️ No se pudieron descargar todos los archivos LFS"

# Verificar si estamos en Render
if [ -n "$RENDER" ]; then
    echo "🌐 Detectado Render, configurando entorno..."
    
    # Instalar dependencias del sistema necesarias para Selenium
    echo "📦 Instalando Chromium y dependencias..."
    apt-get install -y -qq chromium-browser chromium-chromedriver xvfb
    
    echo "✅ Chromium instalado"
fi

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
