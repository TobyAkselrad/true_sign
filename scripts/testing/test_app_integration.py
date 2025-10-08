"""
Test de integración completa con datos bien formados
"""

import sys
import os

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from models.predictors.hybrid_roi_model_2025 import HybridROIModel2025

print("="*70)
print("   TEST DE INTEGRACIÓN - MODELO 2025")
print("="*70)

# Crear modelo
model = HybridROIModel2025()

# Datos de prueba con formato correcto
player_data = {
    'age': 24,
    'height': 180,
    'market_value': 15000000,
    'position': 'Attack',
    'nationality': 'Argentina',
    'foot': 'right'
}

club_data = {
    'name': 'FC Barcelona'
}

print("\n👤 JUGADOR DE PRUEBA:")
print(f"   - Edad: {player_data['age']} años")
print(f"   - Altura: {player_data['height']} cm")
print(f"   - Valor: €{player_data['market_value']:,}")
print(f"   - Posición: {player_data['position']}")
print(f"   - Nacionalidad: {player_data['nationality']}")

print(f"\n🏟️  CLUB DESTINO: {club_data['name']}")

# Calcular análisis
result = model.calculate_hybrid_analysis(player_data, club_data)

print("\n📊 RESULTADO DEL ANÁLISIS:")
print("-"*70)
print(f"💰 Precio Máximo Sugerido: €{result['maximum_price']:,.2f}")
print(f"📈 Valor Futuro Predicho: €{result['predicted_future_value']:,.2f}")
print(f"📊 ROI Esperado: {result['roi_percentage']:.2f}%")
print(f"🎯 Tasa de Éxito: {result['success_rate']*100:.1f}%")
print(f"🏆 Club Multiplier: {result['club_multiplier']}x")
print(f"✅ Confianza: {result['confidence']:.1f}%")
print(f"🤖 Modelo Usado: {result['model_used']}")

print("\n💎 CINCO VALORES:")
print("-"*70)
for key, value in result['five_values'].items():
    print(f"   - {key.replace('_', ' ').title()}: €{value:,.2f}")

print("\n" + "="*70)
print("   ✅ TEST COMPLETADO")
print("="*70 + "\n")

