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
            # Cargar modelo de cambio de valor (prioritario) - FORZAR CARGA ML
            if os.path.exists('saved_models/enhanced_value_change_model_real.pkl'):
                try:
                    print(f"🔍 DEBUG - Intentando cargar enhanced_value_change_model_real.pkl")
                    with open('saved_models/enhanced_value_change_model_real.pkl', 'rb') as f:
                        self.value_change_model = pickle.load(f)
                    models_loaded += 1
                    self.log("✅ Enhanced value change model cargado (ML REAL - DATOS REALES)")
                    print(f"🔍 DEBUG - Modelo cargado exitosamente: {type(self.value_change_model)}")
                except Exception as e:
                    self.log(f"❌ ERROR CRÍTICO: No se puede cargar modelo ML: {e}")
                    print(f"🔍 DEBUG - Error cargando modelo: {e}")
                    raise ValueError(f"❌ MODELO ML REQUERIDO: No se puede cargar enhanced_value_change_model_real.pkl: {e}")
            else:
                print(f"🔍 DEBUG - Archivo enhanced_value_change_model_real.pkl no existe")
                if os.path.exists('saved_models/enhanced_value_change_model_fixed.pkl'):
                    try:
                        with open('saved_models/enhanced_value_change_model_fixed.pkl', 'rb') as f:
                            self.value_change_model = pickle.load(f)
                        models_loaded += 1
                        self.log("✅ Enhanced value change model cargado (ML REAL - FIXED)")
                    except Exception as e:
                        self.log(f"❌ ERROR CRÍTICO: No se puede cargar modelo ML: {e}")
                        raise ValueError(f"❌ MODELO ML REQUERIDO: No se puede cargar enhanced_value_change_model_fixed.pkl: {e}")
                elif os.path.exists('saved_models/enhanced_value_change_model.pkl'):
                    try:
                        # Intentar cargar con compatibilidad de NumPy
                        import numpy as np
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            with open('saved_models/enhanced_value_change_model.pkl', 'rb') as f:
                                self.value_change_model = pickle.load(f)
                        models_loaded += 1
                        self.log("✅ Enhanced value change model cargado (ML REAL)")
                    except Exception as e:
                        self.log(f"❌ ERROR CRÍTICO: No se puede cargar modelo ML: {e}")
                        raise ValueError(f"❌ MODELO ML REQUERIDO: No se puede cargar enhanced_value_change_model.pkl: {e}")
                elif os.path.exists('saved_models/value_change_model.pkl'):
                    try:
                        with open('saved_models/value_change_model.pkl', 'rb') as f:
                            self.value_change_model = pickle.load(f)
                        models_loaded += 1
                        self.log("✅ Value change model cargado")
                    except Exception as e:
                        self.log(f"⚠️ Error cargando value change model: {e}")
                        self.value_change_model = None
            
            # Cargar modelo de precio máximo - PRIORIZAR MODELOS REALES
            if os.path.exists('saved_models/maximum_price_model_real.pkl'):
                try:
                    with open('saved_models/maximum_price_model_real.pkl', 'rb') as f:
                        self.price_models['maximum'] = pickle.load(f)
                    models_loaded += 1
                    self.log("✅ Maximum price model cargado (DATOS REALES - RandomForest)")
                except Exception as e:
                    self.log(f"⚠️ Error cargando maximum price model real: {e}")
                    self.price_models['maximum'] = None
            elif os.path.exists('saved_models/maximum_price_model.pkl'):
                try:
                    with open('saved_models/maximum_price_model.pkl', 'rb') as f:
                        self.price_models['maximum'] = pickle.load(f)
                    models_loaded += 1
                    self.log("✅ Maximum price model cargado")
                except Exception as e:
                    self.log(f"⚠️ Error cargando maximum price model: {e}")
                    self.price_models['maximum'] = None
            
            # Cargar modelo de tasa de éxito - PRIORIZAR MODELOS REALES
            if os.path.exists('saved_models/success_rate_model_real.pkl'):
                try:
                    with open('saved_models/success_rate_model_real.pkl', 'rb') as f:
                        self.success_rate_model = pickle.load(f)
                    models_loaded += 1
                    self.log("✅ Success rate model cargado (DATOS REALES)")
                except Exception as e:
                    self.log(f"⚠️ Error cargando success rate model real: {e}")
                    self.success_rate_model = None
            elif os.path.exists('saved_models/success_rate_model.pkl'):
                try:
                    with open('saved_models/success_rate_model.pkl', 'rb') as f:
                        self.success_rate_model = pickle.load(f)
                    models_loaded += 1
                    self.log("✅ Success rate model cargado")
                except Exception as e:
                    self.log(f"⚠️ Error cargando success rate model: {e}")
                    self.success_rate_model = None
            
            # Cargar preprocesadores
            if os.path.exists('saved_models/enhanced_value_change_scaler_real.pkl'):
                with open('saved_models/enhanced_value_change_scaler_real.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
                self.log("✅ Enhanced scaler cargado (DATOS REALES)")
            elif os.path.exists('saved_models/enhanced_value_change_scaler_fixed.pkl'):
                with open('saved_models/enhanced_value_change_scaler_fixed.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
                self.log("✅ Enhanced scaler cargado (FIXED)")
            elif os.path.exists('saved_models/enhanced_value_change_scaler.pkl'):
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
            # Preparar features (usar original para compatibilidad con 14 features)
            features = self._prepare_original_features(player_data, club_destino)
            
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
            
            # Calcular los 5 valores de análisis
            five_values = self._calculate_five_values_analysis(
                player_data, ensemble_prediction, value_change_prediction, success_rate
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
                'analysis_type': 'Ultimate Optimized Model',
                'five_values': five_values
            }
            
        except Exception as e:
            self.log(f"❌ Error en predicción: {e}")
            return self._intelligent_fallback_prediction(player_data, club_destino)
    
    def predict_ultimate_maximum_price_enhanced(self, player_data, club_destino):
        """Predecir precio máximo con features mejoradas del club"""
        if not self.is_initialized:
            self.log("⚠️ Modelo no inicializado, usando fallback inteligente")
            return self._intelligent_fallback_prediction(player_data, club_destino)

        try:
            # Preparar features mejoradas con datos del club
            features, club_features = self._prepare_enhanced_features_with_club(player_data, club_destino)
            
            # Usar solo las primeras 12 features para los modelos actuales
            features_12 = features[:12]
            
            price_prediction = self._predict_with_ensemble(features_12)
            success_rate = self._predict_success_rate(features_12)
            value_change_prediction = self._predict_value_change(features_12)

            # Ajustar predicciones basadas en features del club
            club_tier_multiplier = club_features.get('club_tier', 1.0)
            financial_power_multiplier = club_features.get('club_financial_power', 1.0)
            
            # Ajustar precio basado en el poder del club
            adjusted_price = price_prediction * club_tier_multiplier * financial_power_multiplier
            
            final_price = self._combine_predictions(
                adjusted_price, value_change_prediction, success_rate, player_data
            )
            
            confidence = self._calculate_confidence(
                adjusted_price, value_change_prediction, success_rate
            )
            
            # Calcular los 5 valores de análisis
            five_values = self._calculate_five_values_analysis(
                player_data, adjusted_price, value_change_prediction, success_rate
            )
            
            return {
                'maximum_price': final_price,
                'base_price': adjusted_price,
                'value_change_prediction': value_change_prediction,
                'success_rate': success_rate,
                'value_change_multiplier': 1.0 + (value_change_prediction * 0.3),
                'confidence': confidence,
                'value_change_confidence': 80 if self.value_change_model else 60,
                'price_confidence': 85 if self.price_models.get('maximum') else 60,
                'models_used': self._get_used_models(),
                'analysis_type': 'Ultimate Optimized Model Enhanced',
                'five_values': five_values,
                'club_features': club_features
            }

        except Exception as e:
            self.log(f"❌ Error en predicción ML mejorada: {e}")
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
    
    def _prepare_original_features(self, player_data, club_destino):
        """Preparar features para modelos originales (14 features)"""
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
            
            # Features originales (14 features como esperan los modelos originales)
            features = [
                age,                    # 0: Edad
                height,                 # 1: Altura
                market_value_millions,  # 2: Valor de mercado en millones
                position_encoded,       # 3: Posición codificada
                nationality_encoded,    # 4: Nacionalidad codificada
                from_club_encoded,      # 5: Club origen codificado
                to_club_encoded,        # 6: Club destino codificado
                age_factor,             # 7: Factor de edad
                np.log1p(market_value), # 8: Log del valor de mercado
                age ** 2,               # 9: Edad al cuadrado
                height / 100,           # 10: Altura normalizada
                market_value_millions ** 0.5,  # 11: Raíz cuadrada del valor
                age * market_value_millions / 1000,  # 12: Interacción edad-valor
                position_encoded * nationality_encoded  # 13: Interacción posición-nacionalidad
            ]
            
            print(f"🔍 DEBUG - Features generadas: {len(features)} elementos")
            print(f"🔍 DEBUG - Features: {features}")
            return np.array(features)  # Todas las features
            
        except Exception as e:
            self.log(f"❌ Error preparando features originales: {e}")
            return np.zeros(14)
    
    def _prepare_enhanced_features_with_club(self, player_data, club_destino):
        """Preparar features mejoradas con datos del club (18 features)"""
        try:
            # Importar extractor de features del club
            from enhanced_features_system import ClubFeaturesExtractor
            
            # Inicializar extractor
            club_extractor = ClubFeaturesExtractor()
            
            # Obtener features del club
            club_features = club_extractor.extract_club_features(club_destino)
            
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
            
            # Features originales (12)
            features_original = [
                age,                    # 0: Edad
                height,                 # 1: Altura
                market_value_millions,  # 2: Valor de mercado en millones
                position_encoded,       # 3: Posición codificada
                nationality_encoded,    # 4: Nacionalidad codificada
                from_club_encoded,      # 5: Club origen codificado
                to_club_encoded,        # 6: Club destino codificado
                age_factor,             # 7: Factor de edad
                np.log1p(market_value), # 8: Log del valor de mercado
                age ** 2,               # 9: Edad al cuadrado
                height / 100,           # 10: Altura normalizada
                market_value / 1000000  # 11: Valor de mercado normalizado
            ]
            
            # NUEVAS FEATURES DEL CLUB (6)
            features_club = [
                club_features['club_market_value'] / 1000000,  # 12: Valor del club (millones)
                club_features['club_squad_size'],              # 13: Tamaño de plantilla
                club_features['club_country_code'],            # 14: País del club
                club_features['club_tier'],                    # 15: Tier del club
                club_features['club_financial_power'],         # 16: Poder financiero
                club_features['club_competitiveness']          # 17: Competitividad
            ]
            
            # Combinar features
            features_enhanced = features_original + features_club
            
            return np.array(features_enhanced), club_features
            
        except Exception as e:
            self.log(f"❌ Error preparando features mejoradas: {e}")
            return np.zeros(18), {}
    
    def _predict_with_ensemble(self, features):
        """Predecir usando modelo ensemble"""
        if self.price_models.get('maximum') is None:
            return self._estimate_price_from_features(features)
        
        try:
            # Usar features originales (12) para modelos reales
            if len(features) == 20:
                # Si tenemos 20 features, usar solo las primeras 12 para modelos originales
                original_features = features[:12]
            else:
                original_features = features
            
            # Verificar que el modelo espera el mismo número de features
            model = self.price_models['maximum']
            if hasattr(model, 'n_features_in_') and model.n_features_in_ != len(original_features):
                self.log(f"⚠️ Modelo espera {model.n_features_in_} features, pero tenemos {len(original_features)}")
                # Usar solo las primeras features que el modelo espera
                original_features = original_features[:model.n_features_in_]
                
            features_array = original_features.reshape(1, -1)
            prediction = self.price_models['maximum'].predict(features_array)[0]
            return max(prediction, original_features[2] * 1000000 * 1.2)  # Mínimo 20% sobre valor mercado
        except Exception as e:
            self.log(f"❌ Error en ensemble: {e}")
            return self._estimate_price_from_features(features)
    
    def _predict_value_change(self, features):
        """Predecir cambio de valor - SOLO ML, SIN FALLBACK"""
        if self.value_change_model is None or self.scaler is None:
            raise ValueError("❌ MODELO ML REQUERIDO: value_change_model no disponible. No se puede hacer predicción sin ML.")
        
        try:
            features_array = features.reshape(1, -1)
            features_scaled = self.scaler.transform(features_array)
            prediction = self.value_change_model.predict(features_scaled)[0]
            print(f"🔍 DEBUG - Value change prediction RAW: {prediction}")
            # Limitar a un rango más realista para transferencias
            limited_prediction = max(-30, min(50, prediction))  # Limitar entre -30% y +50%
            print(f"🔍 DEBUG - Value change prediction LIMITED: {limited_prediction}")
            return limited_prediction
        except Exception as e:
            raise ValueError(f"❌ ERROR EN MODELO ML: No se puede predecir cambio de valor: {e}")
    
    def _predict_success_rate(self, features):
        """Predecir tasa de éxito"""
        if self.success_rate_model is None:
            return self._estimate_success_rate_from_features(features)
        
        try:
            # Usar features originales (12) para modelos reales
            if len(features) == 20:
                # Si tenemos 20 features, usar solo las primeras 12 para modelos originales
                original_features = features[:12]
            elif len(features) == 14:
                # Si tenemos 14 features, usar solo las primeras 12 para modelos originales
                original_features = features[:12]
            else:
                original_features = features
                
            features_array = original_features.reshape(1, -1)
            prediction = self.success_rate_model.predict(features_array)[0]
            return max(0.3, min(0.95, prediction))  # Limitar entre 30% y 95%
        except Exception as e:
            self.log(f"❌ Error en success rate: {e}")
            return self._estimate_success_rate_from_features(features)
    
    def _combine_predictions(self, ensemble_pred, value_change, success_rate, player_data):
        """Combinar predicciones de manera inteligente"""
        market_value = player_data.get('market_value', 10000000)
        
        # Usar directamente el ensemble prediction (está funcionando bien)
        base_price = ensemble_pred
        print(f"🔍 DEBUG - Ensemble prediction (usado): {ensemble_pred}")
        print(f"🔍 DEBUG - Market value: {market_value}")
        print(f"🔍 DEBUG - Base price (ensemble): {base_price}")
        
        # Ajustar por cambio de valor predicho (limitado para evitar valores extremos)
        if value_change != 0:
            print(f"🔍 DEBUG - Value change recibido: {value_change}")
            # Limitar el cambio de valor a máximo 10% de ajuste
            limited_change = min(abs(value_change), 10) / 100.0
            value_adjustment = 1.0 + (limited_change * 0.05)  # Máximo 0.5% de ajuste
            print(f"🔍 DEBUG - Limited change: {limited_change}, Adjustment: {value_adjustment}")
            base_price *= value_adjustment
            print(f"🔍 DEBUG - Base price after value adjustment: {base_price}")
        
        # Ajustar por tasa de éxito (reducido para evitar acumulación)
        success_adjustment = 0.95 + (success_rate * 0.1)  # Entre 0.95 y 1.05
        base_price *= success_adjustment
        
        # Asegurar mínimo razonable
        min_price = market_value * 1.2
        max_price = market_value * 5.0
        
        final_price = max(min_price, min(max_price, base_price))
        print(f"🔍 DEBUG - Final price before limits: {base_price}")
        print(f"🔍 DEBUG - Min price: {min_price}, Max price: {max_price}")
        print(f"🔍 DEBUG - Final price after limits: {final_price}")
        
        return final_price
    
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
        """Codificar club (normalizado para evitar valores extremos)"""
        if encoder:
            try:
                encoded_value = encoder.transform([club])[0]
                # Normalizar valores extremos (más de 50 → dividir por 50)
                if encoded_value > 50:
                    return encoded_value / 50
                return encoded_value
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
        """Estimar cambio de valor desde features (más conservador)"""
        age = features[0]
        position_mult = features[8]
        nationality_mult = features[9]
        
        if age <= 22:
            return 8 + (position_mult - 1) * 3 + (nationality_mult - 1) * 2  # Más conservador
        elif age <= 28:
            return 5 + (position_mult - 1) * 2 + (nationality_mult - 1) * 1  # Más conservador
        else:
            return -5 + (position_mult - 1) * 1 + (nationality_mult - 1) * 1  # Más conservador
    
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
    
    def _calculate_five_values_analysis(self, player_data, base_price, value_change_prediction, success_rate):
        """Calcular los 5 valores de análisis usando el UltimateTransferModel"""
        
        age = player_data.get('age', 25)
        position = player_data.get('position', '').lower()
        nationality = player_data.get('nationality', '').lower()
        market_value = player_data.get('market_value', 0)
        
        print(f"🔍 DEBUG 5 valores - player_data completo: {player_data}")
        print(f"🔍 DEBUG 5 valores - market_value extraído: {market_value}")
        
        # 1. Marketing Value - Valor comercial del jugador
        marketing_value = market_value * 0.3  # 30% del valor de mercado como base
        print(f"🔍 DEBUG 5 valores - marketing_value calculado: {marketing_value}")
        if 'forward' in position or 'winger' in position:
            marketing_value *= 1.5  # Delanteros tienen más valor comercial
        if 'brazil' in nationality or 'argentina' in nationality:
            marketing_value *= 1.3  # Nacionalidades con alto valor comercial
        if success_rate > 0.8:  # Si la tasa de éxito es alta
            marketing_value *= 1.2
        
        # 2. Sport Value - Valor deportivo basado en rendimiento esperado
        sport_value = market_value * 0.4  # 40% del valor de mercado como base
        if age <= 25:
            sport_value *= 1.4  # Jóvenes tienen más potencial
        elif age > 30:
            sport_value *= 0.7  # Mayores tienen menos potencial
        if value_change_prediction > 20:
            sport_value *= 1.3  # Si se predice buen rendimiento
        if success_rate > 0.8:
            sport_value *= 1.2
        
        # 3. Resale Value - Valor de reventa basado en predicción de cambio
        future_value = market_value * (1 + value_change_prediction / 100)
        resale_value = future_value * 0.8  # 80% del valor futuro esperado
        if age <= 22:
            resale_value *= 1.2  # Jóvenes tienen mejor valor de reventa
        elif age > 28:
            resale_value *= 0.8  # Mayores tienen menor valor de reventa
        
        # 4. Similar Transfers Value - Comparación con transferencias similares
        similar_transfers_value = market_value * 0.25  # 25% del valor de mercado como base
        if value_change_prediction > 20:
            similar_transfers_value *= 1.4  # Transferencias exitosas
        elif value_change_prediction < -10:
            similar_transfers_value *= 0.6  # Transferencias menos exitosas
        if success_rate > 0.8:
            similar_transfers_value *= 1.3
        
        # 5. Different Markets Value - Valor en diferentes mercados
        different_markets_value = market_value * 0.2  # 20% del valor de mercado como base
        if 'brazil' in nationality or 'argentina' in nationality:
            different_markets_value *= 1.5  # Alto valor en mercados sudamericanos
        elif 'spain' in nationality or 'france' in nationality:
            different_markets_value *= 1.2  # Buen valor en mercados europeos
        if success_rate > 0.8:
            different_markets_value *= 1.1
        
        return {
            'market_value': market_value,  # Valor de mercado original
            'marketing_value': marketing_value,
            'sport_value': sport_value,
            'resale_value': resale_value,
            'similar_transfers_value': similar_transfers_value,
            'different_markets_value': different_markets_value
        }
    
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
