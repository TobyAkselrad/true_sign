#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar TrueSign Perfect App
"""

import sys
import os

def main():
    print("🚀 Iniciando TrueSign Perfect App...")
    print("=" * 50)
    
    # Agregar directorio actual al path
    sys.path.append('.')
    
    try:
        # Importar la aplicación
        from truesign_perfect_app import app, initialize_model, initialize_hybrid_model, initialize_hybrid_searcher
        
        print("✅ Aplicación importada correctamente")
        
        # Inicializar modelo base (opcional)
        print("🔄 Inicializando modelo base...")
        try:
            if not initialize_model():
                print("⚠️ Modelo base no disponible, continuando sin él...")
            else:
                print("✅ Modelo base inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando modelo base: {e}")
            print("🔄 Continuando sin modelo base...")
        
        # Inicializar modelo híbrido ROI
        print("🔄 Inicializando modelo híbrido ROI...")
        try:
            result = initialize_hybrid_model()
            if result:
                print("✅ Modelo híbrido ROI inicializado correctamente")
            else:
                print("❌ Error inicializando modelo híbrido ROI")
        except Exception as e:
            print(f"❌ Error en inicialización del modelo híbrido: {e}")
        
        # Inicializar sistema híbrido
        print("🔄 Inicializando sistema híbrido...")
        initialize_hybrid_searcher()
        print("✅ Sistema híbrido inicializado")
        
        print("🌐 Iniciando servidor web...")
        print("📱 Accede a: http://localhost:5001")
        print("🔍 Busca jugadores como: Lionel Messi, Kylian Mbappé, Erling Haaland")
        print("=" * 50)
        
        # Configurar puerto
        port = int(os.environ.get('PORT', 5001))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        # Ejecutar aplicación
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        print("💡 Asegúrate de tener todas las dependencias instaladas:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
