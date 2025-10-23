#!/usr/bin/env python3
"""
TrueSign Perfect App - Punto de entrada para Render
"""

import sys
import os

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importar la aplicación principal
from app.main import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
