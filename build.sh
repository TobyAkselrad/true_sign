#!/bin/bash
# Build script para Render

echo "🚀 Iniciando build de TrueSign..."

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
