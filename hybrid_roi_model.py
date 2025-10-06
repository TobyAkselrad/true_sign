#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODELO HÍBRIDO ROI - Combina ValueChangePredictor + UltimateTransferModel
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, Optional

class HybridROIModel:
    """Modelo híbrido que combina lo mejor de ValueChangePredictor y UltimateTransferModel"""
    
    def __init__(self):
        self.value_change_predictor = None
        self.ultimate_model = None
        self.is_initialized = False
        
        print("🚀 Iniciando Modelo Híbrido ROI...")
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializar ambos modelos"""
        try:
            # Importar ValueChangePredictor
            from value_change_predictor import ValueChangePredictor
            self.value_change_predictor = ValueChangePredictor()
            print("✅ ValueChangePredictor inicializado")
            
            # Importar UltimateTransferModelOptimized
            from ultimate_transfer_model_optimized import get_ultimate_model
            self.ultimate_model = get_ultimate_model()
            print("✅ UltimateTransferModelOptimized inicializado")
            
            self.is_initialized = True
            print("✅ Modelo Híbrido ROI inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando modelos híbridos: {e}")
            self.is_initialized = False
    
    def calculate_hybrid_analysis(self, player_data: Dict, club_destino: str, roi_target: int = 30) -> Dict:
        """Calcular análisis híbrido combinando ambos modelos"""
        if not self.is_initialized:
            print("⚠️ Modelo no inicializado, usando fallback")
            return self._fallback_analysis(player_data, club_destino, roi_target)
        
        print(f"🔄 Calculando análisis híbrido para: {player_data.get('player_name', 'N/A')}")
        
        try:
            # 1. Obtener análisis de ValueChangePredictor (para resale value)
            print("📊 Obteniendo análisis de ValueChangePredictor...")
            value_analysis = self.value_change_predictor.calculate_maximum_price(
                player_data, club_destino, roi_target
            )
            
            # 2. Obtener análisis de UltimateTransferModel (para precio máximo)
            print("🎯 Obteniendo análisis de UltimateTransferModel...")
            ultimate_analysis = self.ultimate_model.predict_ultimate_maximum_price(
                player_data, club_destino
            )
            
            # 3. Combinar resultados
            print("🔗 Combinando resultados...")
            hybrid_result = self._combine_analyses(
                value_analysis, ultimate_analysis, player_data, club_destino
            )
            
            print("✅ Análisis híbrido completado")
            return hybrid_result
            
        except Exception as e:
            print(f"❌ Error en análisis híbrido: {e}")
            return self._fallback_analysis(player_data, club_destino, roi_target)
    
    def _combine_analyses(self, value_analysis: Dict, ultimate_analysis: Dict, 
                         player_data: Dict, club_destino: str) -> Dict:
        """Combinar análisis de ambos modelos"""
        
        # Extraer datos de ValueChangePredictor
        predicted_change_percentage = value_analysis.get('predicted_change_percentage', 0)
        current_market_value = value_analysis.get('current_market_value', player_data.get('market_value', 0))
        predicted_future_value = value_analysis.get('predicted_future_value', current_market_value)
        value_change_confidence = value_analysis.get('confidence', 50)
        
        # Extraer datos de UltimateTransferModel
        ultimate_maximum_price = ultimate_analysis.get('maximum_price', current_market_value * 1.5)
        ultimate_base_price = ultimate_analysis.get('base_price', current_market_value * 1.2)
        ultimate_confidence = ultimate_analysis.get('confidence', 50)
        value_change_prediction = ultimate_analysis.get('value_change_prediction', 0)
        
        # Calcular ROI híbrido
        roi_percentage = (predicted_future_value / ultimate_maximum_price - 1) * 100
        roi_percentage = max(0, min(200, roi_percentage))  # Limitar entre 0% y 200%
        
        # Calcular confianza combinada
        combined_confidence = (value_change_confidence + ultimate_confidence) / 2
        
        # Calcular los 5 valores fundamentales (estimados basados en el análisis)
        five_values = self._calculate_five_values_hybrid(
            current_market_value, predicted_future_value, ultimate_maximum_price,
            player_data, predicted_change_percentage
        )
        
        # Análisis de jugadores similares (estimado)
        similar_analysis = self._estimate_similar_analysis(
            player_data, predicted_change_percentage, combined_confidence
        )
        
        return {
            # Datos principales
            'player_name': player_data.get('player_name', 'N/A'),
            'market_value': current_market_value,
            'final_price': ultimate_maximum_price,
            'fair_price': ultimate_maximum_price,
            'adjusted_price': ultimate_maximum_price,
            
            # ROI y valor futuro (de ValueChangePredictor)
            'roi_estimate': {
                'percentage': roi_percentage
            },
            'predicted_change': {
                'percentage': predicted_change_percentage
            },
            'resale_value': predicted_future_value,  # Valor futuro esperado
            
            # Confianza combinada
            'confidence': combined_confidence,
            'value_change_confidence': value_change_confidence,
            'ultimate_confidence': ultimate_confidence,
            
            # Los 5 valores fundamentales
            'five_values': five_values,
            'cinco_valores': five_values,  # Compatibilidad con la aplicación web
            
            # Análisis de jugadores similares
            'similar_analysis': similar_analysis,
            
            # Detalles técnicos
            'model_used': 'Hybrid ROI Model (ValueChange + Ultimate)',
            'analysis_type': 'Hybrid Analysis',
            'value_change_prediction': predicted_change_percentage,
            'ultimate_maximum_price': ultimate_maximum_price,
            'ultimate_base_price': ultimate_base_price,
            
            # Métricas adicionales
            'value_change_multiplier': 1.0 + (predicted_change_percentage / 100),
            'price_to_market_ratio': ultimate_maximum_price / current_market_value if current_market_value > 0 else 1.0,
            'expected_return': predicted_future_value - ultimate_maximum_price
        }
    
    def _calculate_five_values_hybrid(self, market_value: float, future_value: float, 
                                    max_price: float, player_data: Dict, change_percentage: float) -> Dict:
        """Calcular los 5 valores fundamentales basados en análisis híbrido"""
        
        age = player_data.get('age', 25)
        position = player_data.get('position', '').lower()
        nationality = player_data.get('nationality', '').lower()
        
        # Marketing Value (20-30% del precio máximo)
        marketing_value = max_price * 0.25
        if 'forward' in position or 'winger' in position:
            marketing_value *= 1.3
        if 'brazil' in nationality or 'argentina' in nationality:
            marketing_value *= 1.2
        
        # Sport Value (30-40% del precio máximo)
        sport_value = max_price * 0.35
        if age <= 25:
            sport_value *= 1.2
        elif age > 30:
            sport_value *= 0.8
        
        # Resale Value (usar predicción de ValueChangePredictor)
        resale_value = future_value * 0.8  # 80% del valor futuro esperado
        if age <= 22:
            resale_value *= 1.3
        elif age > 28:
            resale_value *= 0.7
        
        # Similar Transfers Value (15-20% del precio máximo)
        similar_transfers_value = max_price * 0.175
        if change_percentage > 20:  # Si se predice buen rendimiento
            similar_transfers_value *= 1.2
        elif change_percentage < -10:  # Si se predice mal rendimiento
            similar_transfers_value *= 0.8
        
        # Different Markets Value (10-15% del precio máximo)
        different_markets_value = max_price * 0.125
        if 'brazil' in nationality or 'argentina' in nationality:
            different_markets_value *= 1.3
        elif 'spain' in nationality or 'france' in nationality:
            different_markets_value *= 1.1
        
        return {
            'marketing_value': marketing_value,
            'sport_value': sport_value,
            'resale_value': resale_value,
            'similar_transfers_value': similar_transfers_value,
            'different_markets_value': different_markets_value
        }
    
    def _estimate_similar_analysis(self, player_data: Dict, change_percentage: float, confidence: float) -> Dict:
        """Estimar análisis de jugadores similares"""
        
        age = player_data.get('age', 25)
        position = player_data.get('position', '').lower()
        
        # Estimar tasa de éxito basada en predicción de cambio
        if change_percentage > 30:
            success_rate = 85.0
            avg_roi = 45.0
        elif change_percentage > 10:
            success_rate = 70.0
            avg_roi = 25.0
        elif change_percentage > 0:
            success_rate = 60.0
            avg_roi = 15.0
        else:
            success_rate = 45.0
            avg_roi = 5.0
        
        # Ajustar por edad
        if age <= 22:
            success_rate += 10
            avg_roi += 10
        elif age > 30:
            success_rate -= 15
            avg_roi -= 10
        
        # Ajustar por posición
        if 'forward' in position:
            success_rate += 5
            avg_roi += 5
        
        # Limitar valores
        success_rate = max(30, min(95, success_rate))
        avg_roi = max(0, min(100, avg_roi))
        
        return {
            'similar_count': 50,  # Estimación
            'success_rate': success_rate,
            'avg_performance': success_rate / 100,
            'avg_roi': avg_roi,
            'adaptation_months': 6 if age <= 25 else 8,
            'confidence': confidence
        }
    
    def _fallback_analysis(self, player_data: Dict, club_destino: str, roi_target: int) -> Dict:
        """Análisis de fallback si los modelos no están disponibles"""
        market_value = player_data.get('market_value', 10000000)
        age = player_data.get('age', 25)
        
        # Precio simple
        final_price = market_value * 1.5
        
        # ROI simple
        roi_percentage = roi_target
        
        # Valor futuro simple
        future_value = market_value * (1 + roi_target / 100)
        
        return {
            'player_name': player_data.get('player_name', 'N/A'),
            'market_value': market_value,
            'final_price': final_price,
            'fair_price': final_price,
            'adjusted_price': final_price,
            'roi_estimate': {'percentage': roi_percentage},
            'predicted_change': {'percentage': roi_percentage},
            'resale_value': future_value,
            'confidence': 50,
            'value_change_confidence': 50,
            'ultimate_confidence': 50,
            'five_values': {
                'marketing_value': market_value * 0.25,
                'sport_value': market_value * 0.35,
                'resale_value': future_value * 0.8,
                'similar_transfers_value': market_value * 0.175,
                'different_markets_value': market_value * 0.125
            },
            'similar_analysis': {
                'similar_count': 0,
                'success_rate': 50,
                'avg_performance': 0.5,
                'avg_roi': roi_target,
                'adaptation_months': 6,
                'confidence': 50
            },
            'model_used': 'Fallback Analysis',
            'analysis_type': 'Simple Fallback'
        }

# Función para obtener instancia singleton
_hybrid_model_instance = None

def get_hybrid_model():
    """Obtener instancia singleton del modelo híbrido"""
    global _hybrid_model_instance
    if _hybrid_model_instance is None:
        _hybrid_model_instance = HybridROIModel()
    return _hybrid_model_instance

if __name__ == "__main__":
    # Probar el modelo híbrido
    hybrid_model = HybridROIModel()
    
    test_player = {
        'player_name': 'Lionel Messi',
        'age': 36,
        'height': 170,
        'market_value': 30000000,
        'position': 'Forward',
        'nationality': 'Argentina',
        'current_club': 'Inter Miami'
    }
    
    result = hybrid_model.calculate_hybrid_analysis(test_player, 'Real Madrid', 30)
    print("Resultado del modelo híbrido:")
    print(f"Precio máximo: €{result['final_price']:,.0f}")
    print(f"ROI estimado: {result['roi_estimate']['percentage']:.1f}%")
    print(f"Valor futuro: €{result['resale_value']:,.0f}")
    print(f"Confianza: {result['confidence']:.1f}%")
