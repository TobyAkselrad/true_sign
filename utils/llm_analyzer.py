#!/usr/bin/env python3
"""
LLM Analyzer - Genera análisis de texto usando Groq API (gratis)
"""

import os
import json
import requests
from typing import Dict, Optional

class LLMAnalyzer:
    """Generador de análisis de texto usando Groq API"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Groq API key (gratis en https://console.groq.com)
        self.api_key = api_key or os.getenv('GROQ_API_KEY', '')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Modelo a usar (Llama 3.1 70B es excelente y gratis)
        self.model = "llama-3.1-70b-versatile"
        
    def generate_transfer_analysis(self, player_data: Dict, analysis_data: Dict, club_destino: str, language: str = 'es') -> str:
        """
        Genera un análisis de texto personalizado basado en los datos del jugador y predicciones
        
        Args:
            player_data: Datos del jugador (nombre, edad, posición, club actual, etc.)
            analysis_data: Datos del análisis (ROI, precio máximo, cinco valores, etc.)
            club_destino: Club de destino
            language: Idioma del análisis ('es' o 'en')
            
        Returns:
            str: Análisis de texto generado por el LLM
        """
        
        # Si no hay API key, retornar análisis básico
        if not self.api_key:
            return self._generate_fallback_analysis(player_data, analysis_data, club_destino, language=language)
        
        try:
            # Preparar datos para el prompt
            player_name = player_data.get('name', 'el jugador')
            age = player_data.get('age', 25)
            position = player_data.get('position', 'jugador')
            current_club = player_data.get('club', 'su club actual')
            market_value = player_data.get('market_value', 0) / 1_000_000
            
            # Datos del análisis
            roi_percentage = analysis_data.get('roi_estimate', {}).get('percentage', 0)
            fair_price = analysis_data.get('fair_price', 0) / 1_000_000
            resale_value = analysis_data.get('resale_value', 0) / 1_000_000
            confidence = analysis_data.get('confidence', 85)
            club_multiplier = analysis_data.get('club_multiplier', 1.0)
            
            # Cinco valores
            five_values = analysis_data.get('five_values', {})
            sporting_value = five_values.get('sporting_value', 0) / 1_000_000
            resale_potential = five_values.get('resale_potential', 0) / 1_000_000
            marketing_value = five_values.get('marketing_impact', 0) / 1_000_000
            
            # Construir prompt según el idioma
            if language == 'en':
                prompt = f"""You are an expert football and transfers analyst. Analyze the following potential transfer and generate a professional analysis in English of maximum 3 paragraphs (150 words).

PLAYER DATA:
- Name: {player_name}
- Age: {age} years old
- Position: {position}
- Current club: {current_club}
- Market value: €{market_value:.1f}M

DESTINATION CLUB: {club_destino}

PREDICTIVE ANALYSIS:
- Maximum recommended price: €{fair_price:.1f}M
- Estimated future value: €{resale_value:.1f}M
- Expected ROI: {roi_percentage:+.1f}%
- Model confidence: {confidence}%
- Destination club factor: {club_multiplier}x

DETAILED VALUATION:
- Sporting value: €{sporting_value:.1f}M
- Resale potential: €{resale_potential:.1f}M
- Marketing impact: €{marketing_value:.1f}M

INSTRUCTIONS:
1. Analyze if the transfer is a good investment
2. Mention strengths and weaknesses
3. Give concrete recommendations
4. Be concise, professional and direct
5. DO NOT use asterisks or markdown formatting
6. Maximum 150 words

Analysis:"""
                system_content = "You are a professional football transfers analyst. You generate concise, accurate and professional analyses in English."
            else:
                prompt = f"""Eres un analista experto de fútbol y transferencias. Analiza la siguiente transferencia potencial y genera un análisis profesional en español de máximo 3 párrafos (150 palabras).

DATOS DEL JUGADOR:
- Nombre: {player_name}
- Edad: {age} años
- Posición: {position}
- Club actual: {current_club}
- Valor de mercado: €{market_value:.1f}M

CLUB DESTINO: {club_destino}

ANÁLISIS PREDICTIVO:
- Precio máximo recomendado: €{fair_price:.1f}M
- Valor futuro estimado: €{resale_value:.1f}M
- ROI esperado: {roi_percentage:+.1f}%
- Confianza del modelo: {confidence}%
- Factor del club destino: {club_multiplier}x

VALORACIÓN DETALLADA:
- Valor deportivo: €{sporting_value:.1f}M
- Potencial de reventa: €{resale_potential:.1f}M
- Impacto marketing: €{marketing_value:.1f}M

INSTRUCCIONES:
1. Analiza si la transferencia es una buena inversión
2. Menciona los puntos fuertes y débiles
3. Da recomendaciones concretas
4. Sé conciso, profesional y directo
5. NO uses asteriscos ni formato markdown
6. Máximo 150 palabras

Análisis:"""
                system_content = "Eres un analista profesional de transferencias de fútbol. Generas análisis concisos, precisos y profesionales en español."

            # Llamar a Groq API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 300,
                "top_p": 1,
                "stream": False
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content'].strip()
                return analysis_text
            else:
                print(f"⚠️ Groq API error: {response.status_code}")
                return self._generate_fallback_analysis(player_data, analysis_data, club_destino, language=language)
                
        except Exception as e:
            print(f"❌ Error generando análisis LLM: {e}")
            return self._generate_fallback_analysis(player_data, analysis_data, club_destino, language=language)
    
    def _generate_fallback_analysis(self, player_data: Dict, analysis_data: Dict, club_destino: str, language: str = 'es') -> str:
        """Genera un análisis básico sin LLM como fallback"""
        
        player_name = player_data.get('name', 'El jugador' if language == 'es' else 'The player')
        age = player_data.get('age', 25)
        position = player_data.get('position', 'jugador' if language == 'es' else 'player')
        roi_percentage = analysis_data.get('roi_estimate', {}).get('percentage', 0)
        fair_price = analysis_data.get('fair_price', 0) / 1_000_000
        confidence = analysis_data.get('confidence', 85)
        
        if language == 'en':
            # English version
            if roi_percentage >= 30:
                verdict = "an excellent investment"
                recommendation = "It is recommended to proceed with the transfer."
            elif roi_percentage >= 15:
                verdict = "a good opportunity"
                recommendation = "The transfer presents a favorable risk-benefit balance."
            elif roi_percentage >= 0:
                verdict = "a moderate investment"
                recommendation = "Carefully evaluate other factors before proceeding."
            else:
                verdict = "a high-risk investment"
                recommendation = "This transfer is not recommended under current conditions."
            
            # Age analysis
            if age <= 23:
                age_analysis = f"At {age} years old, {player_name} has great growth potential. "
            elif age <= 27:
                age_analysis = f"At {age} years old, the player is at his footballing maturity. "
            else:
                age_analysis = f"At {age} years old, his resale value could be limited. "
            
            analysis = f"""The analysis indicates that the transfer of {player_name} ({position}) to {club_destino} represents {verdict}. {age_analysis}The model predicts an ROI of {roi_percentage:+.1f}% with {confidence}% confidence, suggesting a maximum price of €{fair_price:.1f}M. {recommendation}"""
        else:
            # Spanish version
            if roi_percentage >= 30:
                verdict = "excelente inversión"
                recommendation = "Se recomienda proceder con la transferencia."
            elif roi_percentage >= 15:
                verdict = "buena oportunidad"
                recommendation = "La transferencia presenta un balance riesgo-beneficio favorable."
            elif roi_percentage >= 0:
                verdict = "inversión moderada"
                recommendation = "Evaluar cuidadosamente otros factores antes de proceder."
            else:
                verdict = "inversión de alto riesgo"
                recommendation = "No se recomienda esta transferencia bajo las condiciones actuales."
            
            # Análisis de edad
            if age <= 23:
                age_analysis = f"A sus {age} años, {player_name} tiene gran potencial de crecimiento. "
            elif age <= 27:
                age_analysis = f"Con {age} años, el jugador está en su momento de madurez futbolística. "
            else:
                age_analysis = f"A los {age} años, su valor de reventa podría ser limitado. "
            
            analysis = f"""El análisis indica que la transferencia de {player_name} ({position}) al {club_destino} representa una {verdict}. {age_analysis}El modelo predice un ROI de {roi_percentage:+.1f}% con {confidence}% de confianza, sugiriendo un precio máximo de €{fair_price:.1f}M. {recommendation}"""
        
        return analysis


# Función de conveniencia
def generate_analysis(player_data: Dict, analysis_data: Dict, club_destino: str, api_key: Optional[str] = None, language: str = 'es') -> str:
    """Genera análisis de texto usando LLM"""
    analyzer = LLMAnalyzer(api_key=api_key)
    return analyzer.generate_transfer_analysis(player_data, analysis_data, club_destino, language=language)


if __name__ == "__main__":
    # Test
    test_player = {
        'name': 'Kevin Lomónaco',
        'age': 23,
        'position': 'Defender',
        'club': 'Independiente',
        'market_value': 12000000
    }
    
    test_analysis = {
        'roi_estimate': {'percentage': 11.5},
        'fair_price': 21155279,
        'resale_value': 21439731,
        'confidence': 85,
        'club_multiplier': 1.4,
        'five_values': {
            'sporting_value': 4086815,
            'resale_potential': 5838308,
            'marketing_impact': 2919154
        }
    }
    
    analyzer = LLMAnalyzer()
    analysis = analyzer.generate_transfer_analysis(test_player, test_analysis, 'Paris Saint-Germain')
    
    print("=" * 70)
    print("📝 ANÁLISIS GENERADO:")
    print("=" * 70)
    print(analysis)
    print("=" * 70)

