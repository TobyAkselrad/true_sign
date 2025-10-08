#!/usr/bin/env python3
"""
MaximumPricePredictor 2025 - Usa modelos entrenados con sklearn 1.5+, numpy 2.0+
"""

import sys
import os
import pickle
import numpy as np
from pathlib import Path

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

class MaximumPricePredictor2025:
    """MaximumPricePredictor con modelos modernos (2025)"""
    
    def __init__(self):
        self.models_path = "models/trained"
        self.model = None
        self.scaler = None
        self.position_encoder = None
        self.nationality_encoder = None
        self._load_models()
    
    def _load_models(self):
        """Cargar modelos modernos"""
        print("🔄 Cargando modelos 2025 de MaximumPricePredictor...")
        
        try:
            # Modelo principal
            with open(os.path.join(self.models_path, "maximum_price_model.pkl"), 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Modelo 2025 cargado")
            
            # Scaler
            with open(os.path.join(self.models_path, "maximum_price_scaler.pkl"), 'rb') as f:
                self.scaler = pickle.load(f)
            print("✅ Scaler cargado")
            
            # Encoders
            with open(os.path.join(self.models_path, "position_encoder_price.pkl"), 'rb') as f:
                self.position_encoder = pickle.load(f)
            print("✅ Position encoder cargado")
            
            with open(os.path.join(self.models_path, "nationality_encoder_price.pkl"), 'rb') as f:
                self.nationality_encoder = pickle.load(f)
            print("✅ Nationality encoder cargado")
            
        except Exception as e:
            print(f"❌ ERROR cargando modelos 2025: {e}")
            raise
    
    def _prepare_features(self, player_data):
        """Preparar 14 features del jugador"""
        age = player_data.get('age', 25)
        height = player_data.get('height', 180)
        market_value = player_data.get('market_value', 1000000)
        position = player_data.get('position', 'Attack')
        nationality = player_data.get('nationality', 'Unknown')
        foot = player_data.get('foot', 'right')
        
        # Codificar
        try:
            position_encoded = self.position_encoder.transform([position])[0]
        except:
            position_encoded = 0
        
        try:
            nationality_encoded = self.nationality_encoder.transform([nationality])[0]
        except:
            nationality_encoded = 0
        
        foot_encoded = {'right': 1, 'left': 0, 'both': 2}.get(foot.lower(), 1)
        
        # Crear 14 features
        features = [
            age,
            height,
            market_value,
            position_encoded,
            nationality_encoded,
            foot_encoded,
            np.sqrt(market_value),
            age ** 2,
            np.log1p(market_value),
            market_value / 1000000,
            age * market_value / 1000000,
            position_encoded * market_value / 1000000,
            1 if age < 23 else 0,
            1 if age >= 30 else 0
        ]
        
        return np.array(features).reshape(1, -1)
    
    def predict_maximum_price(self, player_data, club_data=None):
        """
        Predice el precio máximo a pagar por un jugador
        
        Returns:
            dict con maximum_price, five_values, success_rate, confidence
        """
        try:
            print("\n" + "="*70)
            print("   💰 MAXIMUM PRICE PREDICTOR 2025 - INICIO")
            print("="*70)
            print(f"📥 INPUT recibido:")
            print(f"   - Nombre: {player_data.get('player_name', player_data.get('name', 'N/A'))}")
            print(f"   - Edad: {player_data.get('age', 'N/A')}")
            print(f"   - Valor mercado: €{player_data.get('market_value', 0):,.0f}")
            print(f"   - Posición: {player_data.get('position', 'N/A')}")
            
            # Preparar features
            print(f"\n🔧 Preparando 14 features...")
            X = self._prepare_features(player_data)
            print(f"   ✅ Features preparadas: {X.shape}")
            
            # Escalar
            print(f"\n📊 Escalando features...")
            X_scaled = self.scaler.transform(X)
            print(f"   ✅ Features escaladas")
            
            # Predecir
            print(f"\n🤖 Ejecutando predicción del modelo ML...")
            maximum_price = self.model.predict(X_scaled)[0]
            print(f"   💎 Precio máximo RAW predicho: €{maximum_price:,.0f}")
            
            # Aplicar límites realistas
            market_value = player_data.get('market_value', 1000000)
            min_price = market_value * 1.1
            max_price = market_value * 4.0
            original_price = maximum_price
            maximum_price = max(min_price, min(max_price, maximum_price))
            
            if original_price != maximum_price:
                print(f"   ⚠️  Precio ajustado a límites: €{original_price:,.0f} → €{maximum_price:,.0f}")
            
            # Calcular success rate (simple heurística)
            age = player_data.get('age', 25)
            if age < 23:
                success_rate = 0.75
            elif age < 28:
                success_rate = 0.85
            else:
                success_rate = 0.70
            
            print(f"\n🎯 Calculando tasa de éxito...")
            print(f"   - Edad: {age} años → Success rate: {success_rate*100:.0f}%")
            
            # Cinco valores
            print(f"\n💎 Calculando cinco valores...")
            five_values = {
                'market_value': market_value,
                'marketing_impact': maximum_price * 0.25 * success_rate,
                'sporting_value': maximum_price * 0.35 * success_rate,
                'resale_potential': maximum_price * 0.50 * success_rate,
                'similar_transfers': maximum_price * 0.20 * success_rate
            }
            
            print(f"   - Market Value: €{five_values['market_value']:,.0f}")
            print(f"   - Marketing Impact: €{five_values['marketing_impact']:,.0f}")
            print(f"   - Sporting Value: €{five_values['sporting_value']:,.0f}")
            print(f"   - Resale Potential: €{five_values['resale_potential']:,.0f}")
            print(f"   - Similar Transfers: €{five_values['similar_transfers']:,.0f}")
            
            result = {
                'maximum_price': maximum_price,
                'five_values': five_values,
                'success_rate': success_rate,
                'confidence': 85,
                'model_used': 'MaximumPricePredictor 2025'
            }
            
            print(f"\n📤 OUTPUT - Maximum Price Predictor:")
            print(f"   - Precio máximo: €{result['maximum_price']:,.0f}")
            print(f"   - Success rate: {result['success_rate']*100:.0f}%")
            print(f"   - Confianza: {result['confidence']}%")
            print("="*70 + "\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Error en predicción: {e}")
            # Fallback simple
            market_value = player_data.get('market_value', 1000000)
            maximum_price = market_value * 1.5
            
            five_values = {
                'market_value': market_value,
                'marketing_impact': maximum_price * 0.25,
                'sporting_value': maximum_price * 0.35,
                'resale_potential': maximum_price * 0.50,
                'similar_transfers': maximum_price * 0.20
            }
            
            return {
                'maximum_price': maximum_price,
                'five_values': five_values,
                'success_rate': 0.75,
                'confidence': 50,
                'model_used': 'MaximumPricePredictor 2025 (fallback)'
            }

if __name__ == "__main__":
    # Test
    predictor = MaximumPricePredictor2025()
    
    player_test = {
        'age': 24,
        'height': 180,
        'market_value': 10000000,
        'position': 'Attack',
        'nationality': 'Argentina',
        'foot': 'right'
    }
    
    result = predictor.predict_maximum_price(player_test)
    print(f"\n📊 Resultado:")
    print(f"   Precio máximo: €{result['maximum_price']:,.0f}")
    print(f"   Success rate: {result['success_rate']*100:.1f}%")

