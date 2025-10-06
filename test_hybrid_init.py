#!/usr/bin/env python3

print("🧪 Probando inicialización del modelo híbrido...")

# Importar la función de inicialización
try:
    import truesign_perfect_app
    print("✅ Importación exitosa")
    
    # Verificar estado inicial
    print(f"🔍 Estado inicial de hybrid_model: {type(truesign_perfect_app.hybrid_model) if truesign_perfect_app.hybrid_model else 'None'}")
    
    # Inicializar modelo híbrido
    print("🔄 Inicializando modelo híbrido...")
    result = truesign_perfect_app.initialize_hybrid_model()
    print(f"✅ Resultado de inicialización: {result}")
    
    # Verificar estado después de inicialización
    print(f"🔍 Estado después de inicialización: {type(truesign_perfect_app.hybrid_model) if truesign_perfect_app.hybrid_model else 'None'}")
    
    if truesign_perfect_app.hybrid_model:
        print("🎯 Probando análisis híbrido...")
        test_data = {
            'player_name': 'Franco Mastantuono',
            'market_value': 50000000,
            'age': 18,
            'height': 177,
            'position': 'Forward',
            'nationality': 'Argentina'
        }
        
        result = truesign_perfect_app.hybrid_model.calculate_hybrid_analysis(test_data, 'Barcelona', 30)
        print(f"✅ Análisis híbrido exitoso")
        print(f"   Precio máximo: €{result.get('final_price', 0):,.0f}")
        
        cinco_valores = result.get('cinco_valores', {})
        if cinco_valores:
            print("💰 CINCO VALORES:")
            for key, value in cinco_valores.items():
                print(f"   {key}: €{value:,.0f}")
        else:
            print("❌ No hay cinco_valores")
    else:
        print("❌ Modelo híbrido no disponible")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
