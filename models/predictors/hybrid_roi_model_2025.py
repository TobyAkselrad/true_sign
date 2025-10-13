#!/usr/bin/env python3
"""
HybridROIModel 2025 - Combina los modelos modernos 2025
"""

import sys
import os

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from models.predictors.value_change_predictor_2025 import ValueChangePredictor2025
from models.predictors.maximum_price_predictor_2025 import MaximumPricePredictor2025

class HybridROIModel2025:
    """Modelo híbrido que combina ValueChange y MaximumPrice (versión 2025)"""
    
    def __init__(self):
        print("\n🚀 Inicializando HybridROIModel 2025...")
        self.value_change_predictor = ValueChangePredictor2025()
        self.maximum_price_predictor = MaximumPricePredictor2025()
        print("✅ HybridROIModel 2025 listo\n")
    
    def _get_club_multiplier(self, club_name):
        """Obtener multiplicador según el club de destino"""
        if not club_name:
            return 1.0
        
        club_lower = club_name.lower()
        
        # Clubes élite (1.4x)
        elite_clubs = [
            'barcelona', 'real madrid', 'manchester city', 'psg', 
            'paris saint-germain', 'bayern munich', 'bayern'
        ]
        
        # Clubes top (1.2x)
        top_clubs = [
            'manchester united', 'chelsea', 'arsenal', 'liverpool',
            'juventus', 'inter', 'milan', 'atletico', 'tottenham'
        ]
        
        # Clubes buenos (1.1x)
        good_clubs = [
            'napoli', 'roma', 'sevilla', 'leicester', 'newcastle',
            'dortmund', 'leipzig', 'atalanta'
        ]
        
        for elite in elite_clubs:
            if elite in club_lower:
                return 1.4
        
        for top in top_clubs:
            if top in club_lower:
                return 1.2
        
        for good in good_clubs:
            if good in club_lower:
                return 1.1
        
        return 1.0
    
    def calculate_hybrid_analysis(self, player_data, club_data=None):
        """
        Calcula análisis híbrido combinando ambos modelos
        
        Returns:
            dict con maximum_price, predicted_future_value, roi_percentage, etc.
        """
        try:
            print("\n" + "╔" + "="*68 + "╗")
            print("║" + " "*15 + "🎯 HYBRID ROI MODEL 2025" + " "*30 + "║")
            print("╚" + "="*68 + "╝")
            
            print(f"\n📥 INPUT - Hybrid Model:")
            print(f"   👤 Jugador: {player_data.get('player_name', player_data.get('name', 'N/A'))}")
            print(f"   🏟️  Club: {club_data.get('name', 'N/A') if club_data else 'N/A'}")
            market_value_display = player_data.get('market_value', 0) or 0
            print(f"   💰 Valor mercado: €{market_value_display:,.0f}")
            
            # Predicción de cambio de valor
            print(f"\n┌─ LLAMANDO A VALUE CHANGE PREDICTOR ─┐")
            value_result = self.value_change_predictor.calculate_maximum_price(player_data, club_data)
            print(f"└─ VALUE CHANGE COMPLETADO ─┘")
            
            # Predicción de precio máximo
            print(f"\n┌─ LLAMANDO A MAXIMUM PRICE PREDICTOR ─┐")
            price_result = self.maximum_price_predictor.predict_maximum_price(player_data, club_data)
            print(f"└─ MAXIMUM PRICE COMPLETADO ─┘")
            
            # Obtener club multiplier
            club_name = club_data.get('name', '') if club_data else ''
            club_multiplier = self._get_club_multiplier(club_name)
            
            print(f"\n🏆 Aplicando Club Multiplier...")
            print(f"   - Club: {club_name}")
            print(f"   - Multiplier: {club_multiplier}x")
            
            # Combinar resultados
            print(f"\n🔀 Combinando resultados de ambos modelos...")
            
            # IMPORTANTE: El club multiplier afecta TANTO al precio como al valor futuro
            # Si un jugador va al PSG, tanto el precio de compra como el valor de reventa serán más altos
            maximum_price_base = price_result['maximum_price']
            predicted_future_value_base = value_result['maximum_price']
            
            # Aplicar multiplier a AMBOS lados de la ecuación
            maximum_price = maximum_price_base * club_multiplier
            predicted_future_value = predicted_future_value_base * club_multiplier
            
            # Calcular ROI REAL basado en el precio que pagas vs valor futuro
            # ROI = (ganancia / inversión) × 100
            if maximum_price > 0:
                roi_percentage = ((predicted_future_value - maximum_price) / maximum_price) * 100
            else:
                roi_percentage = 0
            
            print(f"   📊 Precio base (MaxPrice): €{maximum_price_base:,.0f}")
            print(f"   📊 Valor futuro base: €{predicted_future_value_base:,.0f}")
            print(f"   ✖️  Club multiplier: {club_multiplier}x (aplica a ambos)")
            print(f"   = Precio final: €{maximum_price:,.0f}")
            print(f"   = Valor futuro final: €{predicted_future_value:,.0f}")
            print(f"   💡 ROI calculado: ({predicted_future_value:,.0f} - {maximum_price:,.0f}) / {maximum_price:,.0f} = {roi_percentage:.2f}%")
            
            # Confianza combinada
            combined_confidence = (value_result['confidence'] * 0.4 + price_result['confidence'] * 0.6)
            print(f"\n📊 Confianza combinada:")
            print(f"   - ValueChange (40%): {value_result['confidence']}%")
            print(f"   - MaxPrice (60%): {price_result['confidence']}%")
            print(f"   = Total: {combined_confidence:.0f}%")
            
            result = {
                'maximum_price': maximum_price,
                'predicted_future_value': predicted_future_value,
                'predicted_change_percentage': value_result['predicted_change_percentage'],
                'roi_percentage': roi_percentage,
                'five_values': price_result['five_values'],
                'success_rate': price_result['success_rate'],
                'club_multiplier': club_multiplier,
                'confidence': combined_confidence,
                'model_used': 'Hybrid ROI Model 2025'
            }
            
            print(f"\n" + "╔" + "="*68 + "╗")
            print(f"║  📤 OUTPUT FINAL - HYBRID ROI MODEL 2025" + " "*27 + "║")
            print("╚" + "="*68 + "╝")
            print(f"   💰 Precio Máximo: €{result['maximum_price']:,.0f}")
            print(f"   📈 Valor Futuro: €{result['predicted_future_value']:,.0f}")
            print(f"   📊 ROI: {result['roi_percentage']:+.2f}%")
            print(f"   🎯 Success Rate: {result['success_rate']*100:.0f}%")
            print(f"   ✅ Confianza: {result['confidence']:.0f}%")
            print(f"   🏆 Club Multiplier: {result['club_multiplier']}x")
            print(f"   🤖 Modelo: {result['model_used']}")
            print("="*70 + "\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Error en análisis híbrido: {e}")
            # Fallback simple
            market_value = player_data.get('market_value', 1000000) or 1000000
            
            return {
                'maximum_price': market_value * 1.5,
                'predicted_future_value': market_value * 1.3,
                'predicted_change_percentage': 30,
                'roi_percentage': 30,
                'five_values': {
                    'market_value': market_value,
                    'marketing_impact': market_value * 0.25,
                    'sporting_value': market_value * 0.35,
                    'resale_potential': market_value * 0.50,
                    'similar_transfers': market_value * 0.20
                },
                'success_rate': 0.75,
                'club_multiplier': 1.0,
                'confidence': 50,
                'model_used': 'Hybrid ROI Model 2025 (fallback)'
            }

if __name__ == "__main__":
    # Test
    hybrid_model = HybridROIModel2025()
    
    player_test = {
        'age': 24,
        'height': 180,
        'market_value': 10000000,
        'position': 'Attack',
        'nationality': 'Argentina',
        'foot': 'right'
    }
    
    club_test = {
        'name': 'FC Barcelona'
    }
    
    result = hybrid_model.calculate_hybrid_analysis(player_test, club_test)
    
    print(f"\n📊 RESULTADO HÍBRIDO:")
    print(f"   Precio máximo: €{result['maximum_price']:,.0f}")
    print(f"   Valor futuro: €{result['predicted_future_value']:,.0f}")
    print(f"   ROI: {result['roi_percentage']:.2f}%")
    print(f"   Success rate: {result['success_rate']*100:.1f}%")
    print(f"   Club multiplier: {result['club_multiplier']}x")
    print(f"   Confianza: {result['confidence']:.1f}%")

