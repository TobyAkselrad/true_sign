#!/usr/bin/env python3
"""
Test del nuevo sistema de ROI ajustado por objetivo
"""

def calcular_roi_ajustado_test(valor_futuro, precio_ml, roi_ml, roi_objetivo):
    """
    Simula la lógica del sistema de ROI ajustado
    """
    print("\n" + "="*70)
    print(f"   TEST: ROI AJUSTADO")
    print("="*70)
    
    print(f"\n📥 INPUT:")
    print(f"   Valor futuro predicho: €{valor_futuro/1_000_000:.1f}M")
    print(f"   Precio ML: €{precio_ml/1_000_000:.1f}M")
    print(f"   ROI ML: {roi_ml:.2f}%")
    print(f"   ROI objetivo usuario: {roi_objetivo:.1f}%")
    
    # Calcular precio para lograr ROI objetivo
    precio_para_roi_objetivo = valor_futuro / (1 + roi_objetivo / 100.0)
    
    print(f"\n🧮 CÁLCULO:")
    print(f"   precio_ajustado = {valor_futuro/1_000_000:.1f}M / (1 + {roi_objetivo/100:.2f})")
    print(f"   precio_ajustado = €{precio_para_roi_objetivo/1_000_000:.1f}M")
    
    # Determinar si cumple objetivo
    cumple_objetivo = roi_ml >= roi_objetivo
    
    print(f"\n🎯 DECISIÓN:")
    if cumple_objetivo:
        print(f"   ✅ ROI ML ({roi_ml:.2f}%) >= ROI objetivo ({roi_objetivo:.1f}%)")
        print(f"   → MANTENER valores del modelo ML")
        precio_mostrar = precio_ml
        roi_mostrar = roi_ml
        fue_ajustado = False
    else:
        print(f"   ⚠️ ROI ML ({roi_ml:.2f}%) < ROI objetivo ({roi_objetivo:.1f}%)")
        print(f"   → AJUSTAR para lograr objetivo")
        precio_mostrar = precio_para_roi_objetivo
        roi_mostrar = roi_objetivo
        fue_ajustado = True
    
    print(f"\n📤 OUTPUT FINAL:")
    print(f"   💰 Precio máximo (mostrado): €{precio_mostrar/1_000_000:.1f}M")
    print(f"   📊 ROI (mostrado): {roi_mostrar:.2f}%")
    print(f"   🔄 Fue ajustado: {'✅ SÍ' if fue_ajustado else '❌ NO'}")
    
    # Verificar el ROI real
    roi_verificado = ((valor_futuro - precio_mostrar) / precio_mostrar) * 100
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   ROI real si paga €{precio_mostrar/1_000_000:.1f}M: {roi_verificado:.2f}%")
    print(f"   {'✅ CORRECTO' if abs(roi_verificado - roi_mostrar) < 0.1 else '❌ ERROR'}")
    
    print("="*70)
    
    return {
        'precio_mostrado': precio_mostrar,
        'roi_mostrado': roi_mostrar,
        'fue_ajustado': fue_ajustado,
        'roi_verificado': roi_verificado
    }

# ============================================================
# TEST CASES
# ============================================================

print("\n\n🧪 EJECUTANDO TESTS DEL SISTEMA DE ROI AJUSTADO\n")

# TEST 1: ROI ML < ROI Objetivo → Debe ajustar
print("\n📝 TEST 1: Jugador NO alcanza objetivo (debe ajustar)")
test1 = calcular_roi_ajustado_test(
    valor_futuro=191_400_000,   # €191.4M
    precio_ml=373_300_000,      # €373.3M
    roi_ml=-48.7,               # ROI negativo
    roi_objetivo=30.0           # Usuario pide 30%
)
assert test1['fue_ajustado'] == True, "❌ Test 1 falló: debería estar ajustado"
assert abs(test1['roi_mostrado'] - 30.0) < 0.1, "❌ Test 1 falló: ROI debería ser 30%"
print("✅ TEST 1 PASADO")

# TEST 2: ROI ML >= ROI Objetivo → NO debe ajustar
print("\n📝 TEST 2: Jugador SUPERA objetivo (no debe ajustar)")
test2 = calcular_roi_ajustado_test(
    valor_futuro=115_600_000,   # €115.6M
    precio_ml=85_000_000,       # €85M
    roi_ml=36.0,                # ROI positivo alto
    roi_objetivo=25.0           # Usuario pide 25%
)
assert test2['fue_ajustado'] == False, "❌ Test 2 falló: NO debería estar ajustado"
assert abs(test2['roi_mostrado'] - 36.0) < 0.1, "❌ Test 2 falló: ROI debería ser 36%"
assert abs(test2['precio_mostrado'] - 85_000_000) < 1, "❌ Test 2 falló: precio debería ser €85M"
print("✅ TEST 2 PASADO")

# TEST 3: ROI ML = ROI Objetivo → NO debe ajustar (igual)
print("\n📝 TEST 3: Jugador IGUALA objetivo (no debe ajustar)")
test3 = calcular_roi_ajustado_test(
    valor_futuro=130_000_000,   # €130M
    precio_ml=100_000_000,      # €100M
    roi_ml=30.0,                # ROI exacto
    roi_objetivo=30.0           # Usuario pide 30%
)
assert test3['fue_ajustado'] == False, "❌ Test 3 falló: NO debería estar ajustado"
assert abs(test3['roi_mostrado'] - 30.0) < 0.1, "❌ Test 3 falló: ROI debería ser 30%"
print("✅ TEST 3 PASADO")

# TEST 4: ROI ML muy bajo → Ajustar significativamente
print("\n📝 TEST 4: ROI muy bajo (ajuste significativo)")
test4 = calcular_roi_ajustado_test(
    valor_futuro=50_000_000,    # €50M
    precio_ml=100_000_000,      # €100M
    roi_ml=-50.0,               # ROI muy negativo
    roi_objetivo=40.0           # Usuario pide 40%
)
assert test4['fue_ajustado'] == True, "❌ Test 4 falló: debería estar ajustado"
assert test4['precio_mostrado'] < 50_000_000, "❌ Test 4 falló: precio debería bajar mucho"
print("✅ TEST 4 PASADO")

# TEST 5: Caso extremo - ROI objetivo muy alto
print("\n📝 TEST 5: ROI objetivo muy alto (50%)")
test5 = calcular_roi_ajustado_test(
    valor_futuro=90_000_000,    # €90M
    precio_ml=80_000_000,       # €80M
    roi_ml=12.5,                # ROI bajo
    roi_objetivo=50.0           # Usuario pide 50%
)
assert test5['fue_ajustado'] == True, "❌ Test 5 falló: debería estar ajustado"
assert test5['precio_mostrado'] == 60_000_000, "❌ Test 5 falló: precio debería ser €60M"
assert abs(test5['roi_verificado'] - 50.0) < 0.1, "❌ Test 5 falló: ROI verificado debería ser 50%"
print("✅ TEST 5 PASADO")

# RESUMEN
print("\n\n" + "="*70)
print("   🎉 TODOS LOS TESTS PASARON")
print("="*70)
print("\n✅ La lógica de ROI ajustado funciona correctamente")
print("\n📋 Resumen de casos probados:")
print("   1. ROI ML < Objetivo → Ajusta precio y muestra objetivo ✅")
print("   2. ROI ML > Objetivo → Mantiene valores del modelo ✅")
print("   3. ROI ML = Objetivo → Mantiene valores del modelo ✅")
print("   4. ROI muy bajo → Ajuste significativo ✅")
print("   5. ROI objetivo muy alto → Cálculo correcto ✅")
print("\n" + "="*70 + "\n")

