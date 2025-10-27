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
        # Usar path absoluto basado en la ubicación del archivo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.models_path = os.path.join(project_root, "models", "trained")
        print(f"📂 Models path: {self.models_path}")
        print(f"📂 Models path exists: {os.path.exists(self.models_path)}")
        if os.path.exists(self.models_path):
            print(f"📋 Archivos en models/trained: {os.listdir(self.models_path)}")
        self.model = None
        self.scaler = None
        self.position_encoder = None
        self.nationality_encoder = None
        self._load_models()
    
    def _load_models(self):
        """Cargar modelos modernos"""
        print("🔄 Cargando modelos 2025 de ValueChangePredictor...")
        
        try:
            # Verificar que el directorio existe
            if not os.path.exists(self.models_path):
                raise FileNotFoundError(f"Directorio de modelos no encontrado: {self.models_path}")
            
            # Modelo principal
            model_file = os.path.join(self.models_path, "value_change_model.pkl")
            if not os.path.exists(model_file):
                raise FileNotFoundError(f"Modelo no encontrado: {model_file}")
            
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Modelo 2025 cargado")
            
            # Scaler
            scaler_file = os.path.join(self.models_path, "value_change_scaler.pkl")
            if not os.path.exists(scaler_file):
                raise FileNotFoundError(f"Scaler no encontrado: {scaler_file}")
            
            with open(scaler_file, 'rb') as f:
                self.scaler = pickle.load(f)
            print("✅ Scaler cargado")
            
            # Encoders
            position_file = os.path.join(self.models_path, "position_encoder.pkl")
            if not os.path.exists(position_file):
                raise FileNotFoundError(f"Position encoder no encontrado: {position_file}")
            
            with open(position_file, 'rb') as f:
                self.position_encoder = pickle.load(f)
            print("✅ Position encoder cargado")
            
            nationality_file = os.path.join(self.models_path, "nationality_encoder.pkl")
            if not os.path.exists(nationality_file):
                raise FileNotFoundError(f"Nationality encoder no encontrado: {nationality_file}")
            
            with open(nationality_file, 'rb') as f:
                self.nationality_encoder = pickle.load(f)
            print("✅ Nationality encoder cargado")
            
        except Exception as e:
            print(f"❌ ERROR cargando modelos 2025: {e}")
            print(f"📂 Current directory: {os.getcwd()}")
            print(f"📂 Models path: {self.models_path}")
            print(f"📂 Models path absolute: {os.path.abspath(self.models_path)}")
            print(f"📂 Parent directory: {os.path.dirname(os.path.dirname(os.path.abspath(self.models_path)))}")
            raise
    
    def _calculate_confidence(self, player_data, predicted_value):
        """
        Calcular confianza dinámica basada en calidad de datos y factores de riesgo
        Retorna un valor entre 50-95%
        """
        base_confidence = 85  # Confianza base del modelo (R² típico de RandomForest)
        
        # Factores que REDUCEN la confianza
        penalties = 0
        
        # 1. Edad extrema (-10%)
        age = player_data.get('age', 25)
        # Convertir edad a entero si es posible, sino usar valor por defecto
        try:
            age = int(float(age)) if age != "--" and age is not None else 25
        except (ValueError, TypeError):
            age = 25
        
        if age < 18 or age > 33:
            penalties += 10
            print(f"   ⚠️ Edad extrema ({age} años): -10% confianza")
        
        # 2. Valor de mercado extremo (-5%)
        market_value = player_data.get('market_value', 0)
        if market_value < 500_000 or market_value > 150_000_000:
            penalties += 5
            print(f"   ⚠️ Valor extremo (€{market_value/1_000_000:.1f}M): -5% confianza")
        
        # 3. Datos faltantes (-5% por campo crítico)
        critical_fields = ['position', 'nationality', 'height']
        for field in critical_fields:
            value = player_data.get(field)
            if not value or value == 'Unknown' or value == 0:
                penalties += 5
                print(f"   ⚠️ Campo faltante ({field}): -5% confianza")
        
        # 4. Predicción muy alta o muy baja (-10%)
        if predicted_value > market_value * 2.5 or predicted_value < market_value * 0.5:
            penalties += 10
            change_pct = ((predicted_value - market_value) / market_value) * 100
            print(f"   ⚠️ Cambio extremo ({change_pct:+.1f}%): -10% confianza")
        
        # Calcular confianza final
        final_confidence = max(50, min(95, base_confidence - penalties))
        
        return final_confidence
    
    def _prepare_features(self, player_data):
        """Preparar 19 features del jugador"""
        age = player_data.get('age', 25)
        # Convertir edad a entero si es posible, sino usar valor por defecto
        try:
            age = int(float(age)) if age != "--" and age is not None else 25
        except (ValueError, TypeError):
            age = 25
            
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
            
            # Manejar None en altura
            height = player_data.get('height', 'N/A')
            print(f"   - Altura: {height if height else 'N/A'} cm")
            
            # Manejar None en valor de mercado
            market_value = player_data.get('market_value', 0)
            if market_value is None or market_value == 0:
                print(f"   - Valor mercado: €0 (no disponible)")
            else:
                print(f"   - Valor mercado: €{market_value:,.0f}")
            
            print(f"   - Posición: {player_data.get('position', 'N/A') or 'N/A'}")
            print(f"   - Nacionalidad: {player_data.get('nationality', 'N/A') or 'N/A'}")
            print(f"   - Pie: {player_data.get('foot', 'N/A') or 'N/A'}")
            
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
            
            # Calcular confianza dinámica
            print(f"\n🎯 Calculando confianza...")
            confidence = self._calculate_confidence(player_data, predicted_future_value)
            print(f"   ✅ Confianza calculada: {confidence}%")
            
            result = {
                'maximum_price': predicted_future_value,
                'predicted_change_percentage': value_change_pct,
                'roi_percentage': value_change_pct,
                'confidence': confidence,
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

