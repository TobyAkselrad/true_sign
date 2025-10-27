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
    
    # Agregar directorio raíz del proyecto al path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    print(f"📂 Project root: {project_root}")
    
    # DEBUG: Verificar archivos .pkl
    models_dir = os.path.join(project_root, "models/trained")
    print(f"🔍 DEBUG: Verificando modelos en {models_dir}")
    if os.path.exists(models_dir):
        files = os.listdir(models_dir)
        print(f"📋 Archivos en models/trained: {files}")
        pkl_files = [f for f in files if f.endswith('.pkl')]
        print(f"📊 Total archivos .pkl: {len(pkl_files)}")
        for f in pkl_files:
            path = os.path.join(models_dir, f)
            size = os.path.getsize(path)
            print(f"   - {f}: {size} bytes")
    else:
        print(f"❌ Directorio models/trained NO existe")
    
    try:
        # Importar la aplicación
        from app.main import app, initialize_hybrid_model, initialize_hybrid_searcher
        
        print("✅ Aplicación importada correctamente")
        
        # Inicializar modelo base (NECESARIO para CSV de jugadores)
        print("🔄 Inicializando modelo base...")
        from app.main import initialize_model
        if not initialize_model():
            print("❌ No se pudo inicializar el modelo. Saliendo...")
            sys.exit(1)
        print("✅ Modelo base inicializado")
        
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
