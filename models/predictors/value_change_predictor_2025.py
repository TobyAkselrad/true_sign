#!/usr/bin/env python3
"""
ValueChangePredictor 2025 - Usa modelos entrenados con sklearn 1.5+, numpy 2.0+
"""

import sys
import os
import pickle
import numpy as np
from pathlib import Path

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

class ValueChangePredictor2025:
    """ValueChangePredictor con modelos modernos (2025)"""
    
    def __init__(self):
        self.models_path = "models/trained"
        self.model = None
        self.scaler = None
        self.position_encoder = None
        self.nationality_encoder = None
        self._load_models()
    
    def _load_models(self):
        """Cargar modelos modernos"""
        print("🔄 Cargando modelos 2025 de ValueChangePredictor...")
        
        try:
            # Modelo principal
            with open(os.path.join(self.models_path, "value_change_model.pkl"), 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Modelo 2025 cargado")
            
            # Scaler
            with open(os.path.join(self.models_path, "value_change_scaler.pkl"), 'rb') as f:
                self.scaler = pickle.load(f)
            print("✅ Scaler cargado")
            
            # Encoders
            with open(os.path.join(self.models_path, "position_encoder.pkl"), 'rb') as f:
                self.position_encoder = pickle.load(f)
            print("✅ Position encoder cargado")
            
            with open(os.path.join(self.models_path, "nationality_encoder.pkl"), 'rb') as f:
                self.nationality_encoder = pickle.load(f)
            print("✅ Nationality encoder cargado")
            
        except Exception as e:
            print(f"❌ ERROR cargando modelos 2025: {e}")
            raise
    
    def _prepare_features(self, player_data):
        """Preparar 19 features del jugador"""
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
        
        # Crear 19 features
        features = [
            age,
            height,
            market_value,
            position_encoded,
            nationality_encoded,
            foot_encoded,
            np.sqrt(market_value),
            age ** 2,
            age ** 3,
            height / 100.0,
            np.log1p(market_value),
            market_value / 1000000,
            age * market_value / 1000000,
            position_encoded * nationality_encoded,
            position_encoded * market_value / 1000000,
            height * age,
            1 if age < 23 else 0,
            1 if age >= 30 else 0,
            1 if (age >= 23 and age < 30) else 0
        ]
        
        return np.array(features).reshape(1, -1)
    
    def calculate_maximum_price(self, player_data, club_data=None):
        """
        Calcula el cambio de valor predicho para un jugador
        
        Returns:
            dict con maximum_price, predicted_change_percentage, roi_percentage, confidence
        """
        try:
            print("\n" + "="*70)
            print("   🔄 VALUE CHANGE PREDICTOR 2025 - INICIO")
            print("="*70)
            print(f"📥 INPUT recibido:")
            print(f"   - Nombre: {player_data.get('player_name', player_data.get('name', 'N/A'))}")
            print(f"   - Edad: {player_data.get('age', 'N/A')}")
            print(f"   - Altura: {player_data.get('height', 'N/A')} cm")
            print(f"   - Valor mercado: €{player_data.get('market_value', 0):,.0f}")
            print(f"   - Posición: {player_data.get('position', 'N/A')}")
            print(f"   - Nacionalidad: {player_data.get('nationality', 'N/A')}")
            print(f"   - Pie: {player_data.get('foot', 'N/A')}")
            
            # Preparar features
            print(f"\n🔧 Preparando 19 features...")
            X = self._prepare_features(player_data)
            print(f"   ✅ Features preparadas: {X.shape}")
            
            # Escalar
            print(f"\n📊 Escalando features...")
            X_scaled = self.scaler.transform(X)
            print(f"   ✅ Features escaladas")
            
            # Predecir
            print(f"\n🤖 Ejecutando predicción del modelo ML...")
            value_change_pct = self.model.predict(X_scaled)[0]
            print(f"   📈 Cambio de valor RAW predicho: {value_change_pct:+.2f}%")
            
            # Calcular valor futuro
            market_value = player_data.get('market_value', 1000000)
            predicted_future_value = market_value * (1 + value_change_pct / 100)
            print(f"   💰 Valor futuro calculado: €{predicted_future_value:,.0f}")
            
            # LÍMITES ELIMINADOS - El modelo ML decide libremente
            # Solo aplicamos límites muy amplios para evitar valores absurdos
            original_change = value_change_pct
            value_change_pct = max(-90, min(500, value_change_pct))  # Ampliado: -90% a +500%
            predicted_future_value = max(market_value * 0.1, min(market_value * 6, predicted_future_value))  # 0.1x a 6x
            
            if original_change != value_change_pct:
                print(f"   ⚠️  Cambio ajustado a límites de seguridad: {original_change:.2f}% → {value_change_pct:.2f}%")
            
            result = {
                'maximum_price': predicted_future_value,
                'predicted_change_percentage': value_change_pct,
                'roi_percentage': value_change_pct,
                'confidence': 85,
                'model_used': 'ValueChangePredictor 2025'
            }
            
            print(f"\n📤 OUTPUT - Value Change Predictor:")
            print(f"   - Valor futuro: €{result['maximum_price']:,.0f}")
            print(f"   - Cambio predicho: {result['predicted_change_percentage']:+.2f}%")
            print(f"   - ROI: {result['roi_percentage']:+.2f}%")
            print(f"   - Confianza: {result['confidence']}%")
            print("="*70 + "\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Error en predicción: {e}")
            # Fallback simple
            market_value = player_data.get('market_value', 1000000)
            return {
                'maximum_price': market_value * 1.3,
                'predicted_change_percentage': 30,
                'roi_percentage': 30,
                'confidence': 50,
                'model_used': 'ValueChangePredictor 2025 (fallback)'
            }

if __name__ == "__main__":
    # Test
    predictor = ValueChangePredictor2025()
    
    player_test = {
        'age': 24,
        'height': 180,
        'market_value': 10000000,
        'position': 'Attack',
        'nationality': 'Argentina',
        'foot': 'right'
    }
    
    result = predictor.calculate_maximum_price(player_test)
    print(f"\n📊 Resultado:")
    print(f"   ROI: {result['roi_percentage']:.2f}%")
    print(f"   Valor futuro: €{result['maximum_price']:,.0f}")

