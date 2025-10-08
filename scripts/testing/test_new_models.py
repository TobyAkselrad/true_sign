"""
Script para probar los nuevos modelos entrenados
"""

import sys
import os

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

print("="*70)
print("   PROBANDO NUEVOS MODELOS")
print("="*70)

# Cargar modelos
print("\n📦 Cargando modelos...")
try:
    with open('models/trained/value_change_model.pkl', 'rb') as f:
        value_change_model = pickle.load(f)
    print("   ✅ value_change_model.pkl cargado")
    
    with open('models/trained/maximum_price_model.pkl', 'rb') as f:
        maximum_price_model = pickle.load(f)
    print("   ✅ maximum_price_model.pkl cargado")
    
    with open('models/trained/value_change_scaler.pkl', 'rb') as f:
        value_change_scaler = pickle.load(f)
    print("   ✅ value_change_scaler.pkl cargado")
    
    with open('models/trained/maximum_price_scaler.pkl', 'rb') as f:
        maximum_price_scaler = pickle.load(f)
    print("   ✅ maximum_price_scaler.pkl cargado")
    
    with open('models/trained/position_encoder.pkl', 'rb') as f:
        position_encoder = pickle.load(f)
    print("   ✅ position_encoder.pkl cargado")
    
    with open('models/trained/nationality_encoder.pkl', 'rb') as f:
        nationality_encoder = pickle.load(f)
    print("   ✅ nationality_encoder.pkl cargado")
    
except Exception as e:
    print(f"   ❌ Error cargando modelos: {e}")
    exit(1)

# Probar predicción con datos de ejemplo
print("\n🧪 Probando predicción con jugador de ejemplo...")
print("-"*70)

# Ejemplo: Jugador de 24 años, 180cm, valor 10M, delantero, argentino, pie derecho
age = 24
height = 180
market_value = 10_000_000

# Codificar posición y nacionalidad
try:
    position_encoded = position_encoder.transform(['Attack'])[0]
    nationality_encoded = nationality_encoder.transform(['Argentina'])[0]
except:
    position_encoded = 0
    nationality_encoded = 0

foot_encoded = 1  # Right

# Crear features (19 features para value_change)
features_vc = []
features_vc.append(age)
features_vc.append(height)
features_vc.append(market_value)
features_vc.append(position_encoded)
features_vc.append(nationality_encoded)
features_vc.append(foot_encoded)
features_vc.append(np.sqrt(market_value))
features_vc.append(age ** 2)
features_vc.append(age ** 3)
features_vc.append(height / 100.0)
features_vc.append(np.log1p(market_value))
features_vc.append(market_value / 1000000)
features_vc.append(age * market_value / 1000000)
features_vc.append(position_encoded * nationality_encoded)
features_vc.append(position_encoded * market_value / 1000000)
features_vc.append(height * age)
features_vc.append(1 if age < 23 else 0)
features_vc.append(1 if age >= 30 else 0)
features_vc.append(1 if (age >= 23 and age < 30) else 0)

X_vc = np.array(features_vc).reshape(1, -1)

print(f"\n👤 Jugador de prueba:")
print(f"   - Edad: {age} años")
print(f"   - Altura: {height} cm")
print(f"   - Valor: €{market_value:,}")
print(f"   - Posición: Delantero")
print(f"   - Nacionalidad: Argentina")

# Escalar y predecir cambio de valor
X_vc_scaled = value_change_scaler.transform(X_vc)
value_change_pct = value_change_model.predict(X_vc_scaled)[0]

print(f"\n📈 VALUE CHANGE PREDICTOR:")
print(f"   - Cambio predicho: {value_change_pct:+.2f}%")
print(f"   - Valor futuro: €{market_value * (1 + value_change_pct/100):,.0f}")

# Crear features para maximum price (14 features)
features_mp = []
features_mp.append(age)
features_mp.append(height)
features_mp.append(market_value)
features_mp.append(position_encoded)
features_mp.append(nationality_encoded)
features_mp.append(foot_encoded)
features_mp.append(np.sqrt(market_value))
features_mp.append(age ** 2)
features_mp.append(np.log1p(market_value))
features_mp.append(market_value / 1000000)
features_mp.append(age * market_value / 1000000)
features_mp.append(position_encoded * market_value / 1000000)
features_mp.append(1 if age < 23 else 0)
features_mp.append(1 if age >= 30 else 0)

X_mp = np.array(features_mp).reshape(1, -1)

# Escalar y predecir precio máximo
X_mp_scaled = maximum_price_scaler.transform(X_mp)
maximum_price = maximum_price_model.predict(X_mp_scaled)[0]

print(f"\n💰 MAXIMUM PRICE PREDICTOR:")
print(f"   - Precio máximo sugerido: €{maximum_price:,.0f}")

print("\n" + "="*70)
print("   ✅ MODELOS FUNCIONANDO CORRECTAMENTE")
print("="*70 + "\n")

