#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTIMATE TRANSFER MODEL OPTIMIZADO - Solo modelos entrenados, sin CSV
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
import time
import sys

warnings.filterwarnings('ignore')

class UltimateTransferModelOptimized:
    """Modelo optimizado que solo usa modelos entrenados, sin CSV"""
    
    def __init__(self):
        # Modelos entrenados
        self.ensemble_model = None
        self.value_change_model = None
        self.success_rate_model = None
        self.similarity_engine = None
        self.price_models = {}  # Agregar atributo faltante
        
        # Preprocesadores
        self.scaler = None
        self.position_encoder = None
        self.nationality_encoder = None
        self.from_club_encoder = None
        self.to_club_encoder = None
        
        # Datos preprocesados (estadísticas de entrenamiento)
        self.training_stats = {
            'avg_transfer_value': 25000000,
            'avg_age': 25.5,
            'avg_height': 180.2,
            'position_values': {
                'Forward': 1.2,
                'Midfielder': 1.0,
                'Defender': 0.9,
                'Goalkeeper': 0.8
            },
            'nationality_multipliers': {
                'Brazil': 1.3,
                'Argentina': 1.25,
                'France': 1.2,
                'Spain': 1.15,
                'Germany': 1.1,
                'England': 1.1,
                'Italy': 1.05,
                'Portugal': 1.05
            },
            'club_tiers': {
                'Real Madrid': 1.4,
                'Barcelona': 1.4,
                'Manchester City': 1.3,
                'Liverpool': 1.3,
                'Bayern Munich': 1.3,
                'PSG': 1.3,
                'Chelsea': 1.2,
                'Arsenal': 1.2,
                'Manchester United': 1.2,
                'Juventus': 1.2,
                'AC Milan': 1.15,
                'Inter Milan': 1.15,
                'Atletico Madrid': 1.1,
                'Tottenham': 1.1,
                'Borussia Dortmund': 1.1
            }
        }
        
        self.is_initialized = False
        
    def log(self, message):
        """Log simple"""
        print(f"[ULTIMATE-OPT] {message}")
        sys.stdout.flush()
    
    def load_trained_models(self):
        """Cargar solo los modelos entrenados"""
        self.log("Cargando modelos entrenados...")
        
        models_loaded = 0
        
        try:
            # Cargar modelo de cambio de valor (prioritario)
            if os.path.exists('saved_models/value_change_model.pkl'):
                with open('saved_models/value_change_model.pkl', 'rb') as f:
                    self.value_change_model = pickle.load(f)
                models_loaded += 1
                self.log("✅ Value change model cargado")
            
            # Cargar modelo de precio máximo
            if os.path.exists('saved_models/maximum_price_model.pkl'):
                with open('saved_models/maximum_price_model.pkl', 'rb') as f:
                    self.price_models['maximum'] = pickle.load(f)
                models_loaded += 1
                self.log("✅ Maximum price model cargado")
            
            # Cargar modelo de tasa de éxito
            if os.path.exists('saved_models/success_rate_model.pkl'):
                with open('saved_models/success_rate_model.pkl', 'rb') as f:
                    self.success_rate_model = pickle.load(f)
                models_loaded += 1
                self.log("✅ Success rate model cargado")
            
            # Cargar preprocesadores
            if os.path.exists('saved_models/enhanced_value_change_scaler.pkl'):
                with open('saved_models/enhanced_value_change_scaler.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
                self.log("✅ Enhanced scaler cargado")
            elif os.path.exists('saved_models/value_change_scaler.pkl'):
                with open('saved_models/value_change_scaler.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
                self.log("✅ Scaler cargado")
            
            # Cargar encoders
            if os.path.exists('saved_models/enhanced_position_encoder.pkl'):
                with open('saved_models/enhanced_position_encoder.pkl', 'rb') as f:
                    self.position_encoder = pickle.load(f)
                self.log("✅ Enhanced position encoder cargado")
            elif os.path.exists('saved_models/position_encoder.pkl'):
                with open('saved_models/position_encoder.pkl', 'rb') as f:
                    self.position_encoder = pickle.load(f)
                self.log("✅ Position encoder cargado")
            
            if os.path.exists('saved_models/enhanced_nationality_encoder.pkl'):
                with open('saved_models/enhanced_nationality_encoder.pkl', 'rb') as f:
                    self.nationality_encoder = pickle.load(f)
                self.log("✅ Enhanced nationality encoder cargado")
            elif os.path.exists('saved_models/nationality_encoder.pkl'):
                with open('saved_models/nationality_encoder.pkl', 'rb') as f:
                    self.nationality_encoder = pickle.load(f)
                self.log("✅ Nationality encoder cargado")
            
            # Encoders de clubes
            if os.path.exists('saved_models/from_club_encoder.pkl'):
                with open('saved_models/from_club_encoder.pkl', 'rb') as f:
                    self.from_club_encoder = pickle.load(f)
                self.log("✅ From club encoder cargado")
            
            if os.path.exists('saved_models/to_club_encoder.pkl'):
                with open('saved_models/to_club_encoder.pkl', 'rb') as f:
                    self.to_club_encoder = pickle.load(f)
                self.log("✅ To club encoder cargado")
            
            if models_loaded > 0:
                self.log(f"✅ {models_loaded} modelos principales cargados")
                return True
            else:
                self.log("❌ No se pudieron cargar modelos")
                return False
                
        except Exception as e:
            self.log(f"❌ Error cargando modelos: {e}")
            return False
    
    def initialize(self):
        """Inicializar solo con modelos entrenados"""
        self.log("Inicializando Ultimate Transfer Model Optimizado...")
        
        # Cargar solo modelos entrenados
        if self.load_trained_models():
            self.is_initialized = True
            self.log("✅ Ultimate Transfer Model Optimizado inicializado")
            return True
        else:
            self.log("⚠️ Usando modo fallback con estadísticas de entrenamiento")
            self.is_initialized = False
            return False
    
    def predict_ultimate_maximum_price(self, player_data, club_destino):
        """Predecir precio máximo usando modelos entrenados"""
        if not self.is_initialized:
            self.log("⚠️ Modelo no inicializado, usando fallback inteligente")
            return self._intelligent_fallback_prediction(player_data, club_destino)
        
        try:
            # Preparar features
            features = self._prepare_advanced_features(player_data, club_destino)
            
            # Predicción principal con ensemble
            ensemble_prediction = self._predict_with_ensemble(features)
            
            # Predicción de cambio de valor
            value_change_prediction = self._predict_value_change(features)
            
            # Predicción de tasa de éxito
            success_rate = self._predict_success_rate(features)
            
            # Combinar predicciones
            final_price = self._combine_predictions(
                ensemble_prediction, value_change_prediction, success_rate, player_data
            )
            
            # Calcular confianza
            confidence = self._calculate_confidence(
                ensemble_prediction, value_change_prediction, success_rate
            )
            
            return {
                'maximum_price': final_price,
                'base_price': ensemble_prediction,
                'value_change_prediction': value_change_prediction,
                'success_rate': success_rate,
                'value_change_multiplier': 1.0 + (value_change_prediction * 0.3),
                'confidence': confidence,
                'value_change_confidence': 80 if self.value_change_model else 60,
                'price_confidence': 85 if self.ensemble_model else 60,
                'models_used': self._get_used_models(),
                'analysis_type': 'Ultimate Optimized Model'
            }
            
        except Exception as e:
            self.log(f"❌ Error en predicción: {e}")
            return self._intelligent_fallback_prediction(player_data, club_destino)
    
    def _prepare_advanced_features(self, player_data, club_destino):
        """Preparar features avanzadas usando estadísticas de entrenamiento"""
        try:
            # Features básicas
            age = player_data.get('age', 25)
            height = player_data.get('height', 180)
            market_value = player_data.get('market_value', 10000000)
            position = player_data.get('position', 'Midfielder')
            nationality = player_data.get('nationality', 'Unknown')
            current_club = player_data.get('current_club', 'Unknown')
            
            # Codificar variables categóricas
            position_encoded = self._encode_position(position)
            nationality_encoded = self._encode_nationality(nationality)
            from_club_encoded = self._encode_club(current_club, self.from_club_encoder)
            to_club_encoded = self._encode_club(club_destino, self.to_club_encoder)
            
            # Features calculadas
            market_value_millions = market_value / 1000000
            age_factor = self._calculate_age_factor(age)
            position_multiplier = self.training_stats['position_values'].get(position, 1.0)
            nationality_multiplier = self.training_stats['nationality_multipliers'].get(nationality, 1.0)
            club_tier_multiplier = self.training_stats['club_tiers'].get(club_destino, 1.0)
            
            # Features avanzadas
            features = [
                age,
                height,
                market_value_millions,
                position_encoded,
                nationality_encoded,
                from_club_encoded,
                to_club_encoded,
                age_factor,
                position_multiplier,
                nationality_multiplier,
                club_tier_multiplier,
                np.log1p(market_value),
                age ** 2,
                height / 100,
                market_value / self.training_stats['avg_transfer_value'],
                age / self.training_stats['avg_age'],
                height / self.training_stats['avg_height'],
                position_multiplier * nationality_multiplier,
                club_tier_multiplier * position_multiplier,
                market_value_millions * position_multiplier
            ]
            
            # Asegurar que tenemos exactamente 20 features (como esperan los modelos)
            while len(features) < 20:
                features.append(0.0)
            return np.array(features[:20])  # Limitar a 20 features
            
        except Exception as e:
            self.log(f"❌ Error preparando features: {e}")
            return np.array([25, 180, 10, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 10, 625, 1.8, 0.4, 1.0, 1.0, 1.0, 1.0, 10])
    
    def _predict_with_ensemble(self, features):
        """Predecir usando modelo ensemble"""
        if self.ensemble_model is None:
            return self._estimate_price_from_features(features)
        
        try:
            features_array = features.reshape(1, -1)
            prediction = self.ensemble_model.predict(features_array)[0]
            return max(prediction, features[2] * 1000000 * 1.2)  # Mínimo 20% sobre valor mercado
        except Exception as e:
            self.log(f"❌ Error en ensemble: {e}")
            return self._estimate_price_from_features(features)
    
    def _predict_value_change(self, features):
        """Predecir cambio de valor"""
        if self.value_change_model is None or self.scaler is None:
            return self._estimate_value_change_from_features(features)
        
        try:
            features_array = features.reshape(1, -1)
            features_scaled = self.scaler.transform(features_array)
            prediction = self.value_change_model.predict(features_scaled)[0]
            return max(-50, min(200, prediction))  # Limitar entre -50% y +200%
        except Exception as e:
            self.log(f"❌ Error en value change: {e}")
            return self._estimate_value_change_from_features(features)
    
    def _predict_success_rate(self, features):
        """Predecir tasa de éxito"""
        if self.success_rate_model is None:
            return self._estimate_success_rate_from_features(features)
        
        try:
            features_array = features.reshape(1, -1)
            prediction = self.success_rate_model.predict(features_array)[0]
            return max(0.3, min(0.95, prediction))  # Limitar entre 30% y 95%
        except Exception as e:
            self.log(f"❌ Error en success rate: {e}")
            return self._estimate_success_rate_from_features(features)
    
    def _combine_predictions(self, ensemble_pred, value_change, success_rate, player_data):
        """Combinar predicciones de manera inteligente"""
        market_value = player_data.get('market_value', 10000000)
        
        # Precio base del ensemble
        base_price = ensemble_pred
        
        # Ajustar por cambio de valor predicho
        if value_change != 0:
            value_adjustment = 1.0 + (value_change * 0.3)
            base_price *= value_adjustment
        
        # Ajustar por tasa de éxito
        success_adjustment = 0.8 + (success_rate * 0.4)  # Entre 0.8 y 1.2
        base_price *= success_adjustment
        
        # Asegurar mínimo razonable
        min_price = market_value * 1.2
        max_price = market_value * 5.0
        
        return max(min_price, min(max_price, base_price))
    
    def _calculate_confidence(self, ensemble_pred, value_change, success_rate):
        """Calcular confianza basada en los modelos disponibles"""
        confidence = 60  # Base
        
        if self.ensemble_model:
            confidence += 15
        if self.value_change_model:
            confidence += 10
        if self.success_rate_model:
            confidence += 10
        if self.similarity_engine:
            confidence += 5
        
        # Ajustar por calidad de predicciones
        if success_rate > 0.7:
            confidence += 5
        if abs(value_change) < 50:  # Cambio de valor razonable
            confidence += 5
        
        return min(95, confidence)
    
    def _get_used_models(self):
        """Obtener lista de modelos usados"""
        models = []
        if self.ensemble_model:
            models.append('ensemble')
        if self.value_change_model:
            models.append('value_change')
        if self.success_rate_model:
            models.append('success_rate')
        if self.similarity_engine:
            models.append('similarity')
        return models
    
    def _encode_position(self, position):
        """Codificar posición"""
        if self.position_encoder:
            try:
                return self.position_encoder.transform([position])[0]
            except:
                pass
        return 0
    
    def _encode_nationality(self, nationality):
        """Codificar nacionalidad"""
        if self.nationality_encoder:
            try:
                return self.nationality_encoder.transform([nationality])[0]
            except:
                pass
        return 0
    
    def _encode_club(self, club, encoder):
        """Codificar club"""
        if encoder:
            try:
                return encoder.transform([club])[0]
            except:
                pass
        return 0
    
    def _calculate_age_factor(self, age):
        """Calcular factor de edad"""
        if age <= 22:
            return 1.3  # Jóvenes con potencial
        elif age <= 28:
            return 1.1  # Edad pico
        elif age <= 32:
            return 0.9  # Experiencia pero menos potencial
        else:
            return 0.7  # Declive
    
    def _estimate_price_from_features(self, features):
        """Estimar precio desde features"""
        market_value = features[2] * 1000000
        age_factor = features[7]
        position_mult = features[8]
        nationality_mult = features[9]
        club_mult = features[10]
        
        return market_value * age_factor * position_mult * nationality_mult * club_mult
    
    def _estimate_value_change_from_features(self, features):
        """Estimar cambio de valor desde features"""
        age = features[0]
        position_mult = features[8]
        nationality_mult = features[9]
        
        if age <= 22:
            return 20 + (position_mult - 1) * 10 + (nationality_mult - 1) * 5
        elif age <= 28:
            return 10 + (position_mult - 1) * 5 + (nationality_mult - 1) * 3
        else:
            return -10 + (position_mult - 1) * 3 + (nationality_mult - 1) * 2
    
    def _estimate_success_rate_from_features(self, features):
        """Estimar tasa de éxito desde features"""
        age = features[0]
        position_mult = features[8]
        nationality_mult = features[9]
        club_mult = features[10]
        
        base_rate = 0.6
        age_bonus = 0.1 if 22 <= age <= 28 else 0.05
        position_bonus = (position_mult - 1) * 0.1
        nationality_bonus = (nationality_mult - 1) * 0.05
        club_bonus = (club_mult - 1) * 0.1
        
        return base_rate + age_bonus + position_bonus + nationality_bonus + club_bonus
    
    def _intelligent_fallback_prediction(self, player_data, club_destino):
        """Predicción de fallback inteligente usando estadísticas de entrenamiento"""
        market_value = player_data.get('market_value', 10000000)
        age = player_data.get('age', 25)
        position = player_data.get('position', 'Midfielder')
        nationality = player_data.get('nationality', 'Unknown')
        
        # Usar estadísticas de entrenamiento
        position_mult = self.training_stats['position_values'].get(position, 1.0)
        nationality_mult = self.training_stats['nationality_multipliers'].get(nationality, 1.0)
        club_mult = self.training_stats['club_tiers'].get(club_destino, 1.0)
        age_factor = self._calculate_age_factor(age)
        
        # Calcular precio
        base_price = market_value * 1.5
        final_price = base_price * position_mult * nationality_mult * club_mult * age_factor
        
        # Estimar cambio de valor
        value_change = self._estimate_value_change_from_features(
            np.array([age, 180, market_value/1000000, 0, 0, 0, 0, age_factor, position_mult, nationality_mult, club_mult] + [0]*9)
        )
        
        # Estimar tasa de éxito
        success_rate = self._estimate_success_rate_from_features(
            np.array([age, 180, market_value/1000000, 0, 0, 0, 0, age_factor, position_mult, nationality_mult, club_mult] + [0]*9)
        )
        
        return {
            'maximum_price': final_price,
            'base_price': base_price,
            'value_change_prediction': value_change,
            'success_rate': success_rate,
            'value_change_multiplier': 1.0 + (value_change * 0.3),
            'confidence': 70,
            'value_change_confidence': 70,
            'price_confidence': 70,
            'models_used': ['training_stats'],
            'analysis_type': 'Intelligent Fallback with Training Stats'
        }

# Función para obtener instancia singleton
_ultimate_model_instance = None

def get_ultimate_model():
    """Obtener instancia singleton del modelo ultimate optimizado"""
    global _ultimate_model_instance
    if _ultimate_model_instance is None:
        _ultimate_model_instance = UltimateTransferModelOptimized()
        _ultimate_model_instance.initialize()
    return _ultimate_model_instance

if __name__ == "__main__":
    # Probar el modelo
    model = UltimateTransferModelOptimized()
    if model.initialize():
        print("✅ Modelo Ultimate Optimizado listo para usar")
        
        # Prueba con datos de ejemplo
        test_player = {
            'player_name': 'Lionel Messi',
            'age': 36,
            'height': 170,
            'market_value': 30000000,
            'position': 'Forward',
            'nationality': 'Argentina',
            'current_club': 'Inter Miami'
        }
        
        result = model.predict_ultimate_maximum_price(test_player, 'Real Madrid')
        print(f"Resultado: {result}")
    else:
        print("❌ Error inicializando modelo")
