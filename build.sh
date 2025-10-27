#!/bin/bash
# Build script para Render

echo "🚀 Iniciando build de TrueSign..."

# Verificar si estamos en Render
if [ -n "$RENDER" ]; then
    echo "🌐 Configurando Chrome y ChromeDriver para Render..."
    
    # Instalar Chrome y ChromeDriver
    apt-get update
    apt-get install -y chromium-browser chromium-chromedriver xvfb \
        xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-base xfonts-scalable
    
    # Crear symlinks para ChromeDriver
    ln -sf /usr/bin/chromium-browser /usr/bin/google-chrome-stable
    ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver
    
    # Configurar variables de entorno
    export CHROME_BIN=/usr/bin/chromium-browser
    export CHROMEDRIVER_PATH=/usr/bin/chromedriver
    
    echo "✅ Chrome y ChromeDriver configurados"
fi

# Instalar dependencias
pip install -r requirements.txt

# Verificar que los modelos estén presentes
echo "📊 Verificando modelos entrenados..."
ls -la models/trained/

# Verificar que el archivo principal existe
if [ ! -f "truesign_perfect_app.py" ]; then
    echo "❌ Error: truesign_perfect_app.py no encontrado"
    exit 1
fi

echo "✅ Build completado exitosamente"
