#!/usr/bin/env python3
"""
Sistema mejorado de fallback para clubes con más funcionalidades
"""

import json
import re
from typing import Dict, List, Optional

class EnhancedClubsFallback:
    """Sistema mejorado de fallback para clubes"""
    
    def __init__(self):
        self.clubs_database = self._load_enhanced_clubs_database()
        self.search_cache = {}
    
    def _load_enhanced_clubs_database(self) -> Dict:
        """Cargar base de datos mejorada de clubes"""
        return {
            # CLUBES ELITE (€1B+)
            'Real Madrid': {
                'name': 'Real Madrid',
                'country': 'Spain',
                'market_value': 1200000000,
                'league': 'La Liga',
                'tier': 1,
                'aliases': ['Real Madrid', 'Madrid', 'Real', 'RM', 'Los Blancos'],
                'founded': 1902,
                'stadium': 'Santiago Bernabéu',
                'capacity': 81044
            },
            'Barcelona': {
                'name': 'FC Barcelona',
                'country': 'Spain',
                'market_value': 1100000000,
                'league': 'La Liga',
                'tier': 1,
                'aliases': ['Barcelona', 'Barça', 'FC Barcelona', 'Barca', 'Blaugrana'],
                'founded': 1899,
                'stadium': 'Camp Nou',
                'capacity': 99354
            },
            'Manchester City': {
                'name': 'Manchester City',
                'country': 'England',
                'market_value': 1000000000,
                'league': 'Premier League',
                'tier': 1,
                'aliases': ['Manchester City', 'Man City', 'City', 'MCFC'],
                'founded': 1880,
                'stadium': 'Etihad Stadium',
                'capacity': 53400
            },
            'Bayern Munich': {
                'name': 'FC Bayern Munich',
                'country': 'Germany',
                'market_value': 900000000,
                'league': 'Bundesliga',
                'tier': 1,
                'aliases': ['Bayern Munich', 'Bayern', 'FC Bayern', 'Bayern München'],
                'founded': 1900,
                'stadium': 'Allianz Arena',
                'capacity': 75000
            },
            
            # CLUBES TOP (€500M-€1B)
            'Manchester United': {
                'name': 'Manchester United',
                'country': 'England',
                'market_value': 800000000,
                'league': 'Premier League',
                'tier': 1,
                'aliases': ['Manchester United', 'Man United', 'Man Utd', 'MUFC', 'Red Devils'],
                'founded': 1878,
                'stadium': 'Old Trafford',
                'capacity': 74879
            },
            'Liverpool': {
                'name': 'Liverpool FC',
                'country': 'England',
                'market_value': 800000000,
                'league': 'Premier League',
                'tier': 1,
                'aliases': ['Liverpool', 'Liverpool FC', 'LFC', 'Reds'],
                'founded': 1892,
                'stadium': 'Anfield',
                'capacity': 53394
            },
            'PSG': {
                'name': 'Paris Saint-Germain',
                'country': 'France',
                'market_value': 800000000,
                'league': 'Ligue 1',
                'tier': 1,
                'aliases': ['PSG', 'Paris Saint-Germain', 'Paris SG', 'Paris'],
                'founded': 1970,
                'stadium': 'Parc des Princes',
                'capacity': 47929
            },
            'Chelsea': {
                'name': 'Chelsea FC',
                'country': 'England',
                'market_value': 700000000,
                'league': 'Premier League',
                'tier': 1,
                'aliases': ['Chelsea', 'Chelsea FC', 'CFC', 'Blues'],
                'founded': 1905,
                'stadium': 'Stamford Bridge',
                'capacity': 40341
            },
            'Tottenham': {
                'name': 'Tottenham Hotspur',
                'country': 'England',
                'market_value': 600000000,
                'league': 'Premier League',
                'tier': 1,
                'aliases': ['Tottenham', 'Spurs', 'Tottenham Hotspur', 'THFC'],
                'founded': 1882,
                'stadium': 'Tottenham Hotspur Stadium',
                'capacity': 62850
            },
            'Juventus': {
                'name': 'Juventus FC',
                'country': 'Italy',
                'market_value': 600000000,
                'league': 'Serie A',
                'tier': 1,
                'aliases': ['Juventus', 'Juve', 'Juventus FC', 'Bianconeri'],
                'founded': 1897,
                'stadium': 'Allianz Stadium',
                'capacity': 41507
            },
            'Arsenal': {
                'name': 'Arsenal FC',
                'country': 'England',
                'market_value': 600000000,
                'league': 'Premier League',
                'tier': 1,
                'aliases': ['Arsenal', 'Arsenal FC', 'AFC', 'Gunners'],
                'founded': 1886,
                'stadium': 'Emirates Stadium',
                'capacity': 60704
            },
            
            # CLUBES ARGENTINOS
            'River Plate': {
                'name': 'River Plate',
                'country': 'Argentina',
                'market_value': 80000000,
                'league': 'Liga Profesional',
                'tier': 2,
                'aliases': ['River Plate', 'River', 'Millonarios'],
                'founded': 1901,
                'stadium': 'El Monumental',
                'capacity': 70074
            },
            'Boca Juniors': {
                'name': 'Boca Juniors',
                'country': 'Argentina',
                'market_value': 70000000,
                'league': 'Liga Profesional',
                'tier': 2,
                'aliases': ['Boca Juniors', 'Boca', 'Xeneizes'],
                'founded': 1905,
                'stadium': 'La Bombonera',
                'capacity': 54000
            },
            'Racing Club': {
                'name': 'Racing Club',
                'country': 'Argentina',
                'market_value': 45000000,
                'league': 'Liga Profesional',
                'tier': 2,
                'aliases': ['Racing Club', 'Racing', 'La Academia'],
                'founded': 1903,
                'stadium': 'El Cilindro',
                'capacity': 55000
            },
            'Independiente': {
                'name': 'Independiente',
                'country': 'Argentina',
                'market_value': 50000000,
                'league': 'Liga Profesional',
                'tier': 2,
                'aliases': ['Independiente', 'El Rojo', 'Rey de Copas'],
                'founded': 1905,
                'stadium': 'Libertadores de América',
                'capacity': 49000
            },
            'CA Talleres': {
                'name': 'CA Talleres',
                'country': 'Argentina',
                'market_value': 38950000,
                'league': 'Liga Profesional',
                'tier': 2,
                'aliases': ['CA Talleres', 'Talleres', 'Talleres de Córdoba', 'La T'],
                'founded': 1913,
                'stadium': 'Mario Alberto Kempes',
                'capacity': 57000
            },
            'Club Nacional': {
                'name': 'Club Nacional',
                'country': 'Uruguay',
                'market_value': 19600000,
                'league': 'Primera División',
                'tier': 2,
                'aliases': ['Club Nacional', 'Nacional', 'Nacional de Uruguay', 'Los Bolsos'],
                'founded': 1899,
                'stadium': 'Gran Parque Central',
                'capacity': 34000
            },
            'Peñarol': {
                'name': 'Peñarol',
                'country': 'Uruguay',
                'market_value': 35000000,
                'league': 'Primera División',
                'tier': 2,
                'aliases': ['Peñarol', 'Club Atlético Peñarol', 'Carboneros', 'Manyas'],
                'founded': 1891,
                'stadium': 'Estadio Campeón del Siglo',
                'capacity': 40000
            }
        }
    
    def search_clubs(self, query: str, limit: int = 20) -> List[Dict]:
        """Búsqueda mejorada de clubes"""
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower().strip()
        
        # Verificar cache
        if query_lower in self.search_cache:
            return self.search_cache[query_lower][:limit]
        
        results = []
        
        for club_data in self.clubs_database.values():
            score = self._calculate_search_score(club_data, query_lower)
            if score > 0:
                club_info = self._format_club_info(club_data)
                club_info['search_score'] = score
                results.append(club_info)
        
        # Ordenar por score
        results.sort(key=lambda x: x['search_score'], reverse=True)
        
        # Guardar en cache
        self.search_cache[query_lower] = results
        
        return results[:limit]
    
    def _calculate_search_score(self, club_data: Dict, query: str) -> float:
        """Calcular score de búsqueda"""
        score = 0.0
        
        # Búsqueda exacta en nombre
        if query in club_data['name'].lower():
            score += 100
        
        # Búsqueda en aliases
        for alias in club_data.get('aliases', []):
            if query in alias.lower():
                score += 80
        
        # Búsqueda parcial en nombre
        if query in club_data['name'].lower():
            score += 60
        
        # Búsqueda en país
        if query in club_data['country'].lower():
            score += 40
        
        # Búsqueda en liga
        if query in club_data.get('league', '').lower():
            score += 30
        
        # Búsqueda fuzzy (caracteres similares)
        if self._fuzzy_match(query, club_data['name'].lower()):
            score += 20
        
        return score
    
    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Búsqueda fuzzy simple"""
        if len(query) < 3:
            return False
        
        # Verificar si la mayoría de caracteres están presentes
        query_chars = set(query)
        text_chars = set(text)
        common_chars = query_chars.intersection(text_chars)
        
        return len(common_chars) >= len(query_chars) * 0.7
    
    def _format_club_info(self, club_data: Dict) -> Dict:
        """Formatear información del club"""
        market_value = club_data['market_value']
        
        # Formato mejorado de market value
        if market_value >= 1000000000:  # >= 1B
            formatted_value = f"€{market_value/1000000000:.1f}B"
        elif market_value >= 1000000:  # >= 1M
            formatted_value = f"€{market_value/1000000:.0f}M"
        elif market_value >= 1000:  # >= 1K
            formatted_value = f"€{market_value/1000:.0f}K"
        else:
            formatted_value = f"€{market_value:,.0f}"
        
        return {
            'name': club_data['name'],
            'country': club_data['country'],
            'market_value': formatted_value,  # Usar formato mejorado
            'market_value_raw': market_value,  # Valor numérico original
            'formatted_market_value': formatted_value,
            'display': f"{club_data['name']} ({club_data['country']}) - {formatted_value}",
            'economic_factor': self._calculate_economic_factor(market_value),
            'league_factor': self._calculate_league_factor(club_data['country']),
            'classification': self._classify_club(market_value, club_data['country']),
            'squad': 25,
            'squad_analysis': "Plantilla equilibrada",
            'transfer_potential': self._get_transfer_potential(market_value),
            'tier': club_data.get('tier', 2),
            'league': club_data.get('league', 'Unknown'),
            'founded': club_data.get('founded', 1900),
            'stadium': club_data.get('stadium', 'Unknown'),
            'capacity': club_data.get('capacity', 25000)
        }
    
    def _calculate_economic_factor(self, market_value: int) -> float:
        """Calcular factor económico"""
        if market_value >= 1000000000:
            return 1.5  # Elite
        elif market_value >= 500000000:
            return 1.3  # Top
        elif market_value >= 200000000:
            return 1.2  # Grande
        elif market_value >= 50000000:
            return 1.1  # Mediano
        else:
            return 1.0  # Pequeño
    
    def _calculate_league_factor(self, country: str) -> float:
        """Calcular factor de liga"""
        league_factors = {
            'Spain': 1.4, 'England': 1.5, 'Germany': 1.3, 'Italy': 1.3,
            'France': 1.2, 'Netherlands': 1.2, 'Portugal': 1.1,
            'Argentina': 1.1, 'Brazil': 1.1, 'Mexico': 1.1
        }
        return league_factors.get(country, 1.0)
    
    def _classify_club(self, market_value: int, country: str) -> str:
        """Clasificar club"""
        if market_value >= 1000000000:
            return "Elite Club"
        elif market_value >= 500000000:
            return "Top Club"
        elif market_value >= 200000000:
            return "Big Club"
        elif market_value >= 50000000:
            return "Medium Club"
        else:
            return "Small Club"
    
    def _get_transfer_potential(self, market_value: int) -> str:
        """Obtener potencial de transferencias"""
        if market_value >= 500000000:
            return "Muy Alto"
        elif market_value >= 200000000:
            return "Alto"
        elif market_value >= 50000000:
            return "Medio"
        else:
            return "Bajo"
    
    def get_club_by_name(self, club_name: str) -> Optional[Dict]:
        """Obtener club por nombre exacto"""
        for club_data in self.clubs_database.values():
            if club_name.lower() in [alias.lower() for alias in club_data.get('aliases', [])]:
                return self._format_club_info(club_data)
        return None
    
    def get_clubs_by_country(self, country: str) -> List[Dict]:
        """Obtener clubes por país"""
        results = []
        for club_data in self.clubs_database.values():
            if club_data['country'].lower() == country.lower():
                results.append(self._format_club_info(club_data))
        return results
    
    def get_clubs_by_tier(self, tier: int) -> List[Dict]:
        """Obtener clubes por tier"""
        results = []
        for club_data in self.clubs_database.values():
            if club_data.get('tier', 2) == tier:
                results.append(self._format_club_info(club_data))
        return results

def demonstrate_enhanced_fallback():
    """Demostrar el sistema mejorado"""
    print("🔍 SISTEMA MEJORADO DE FALLBACK DE CLUBES")
    print("=" * 60)
    
    fallback = EnhancedClubsFallback()
    
    # Pruebas de búsqueda
    test_queries = ['barcelona', 'real', 'manchester', 'racing', 'boca', 'bar']
    
    for query in test_queries:
        print(f"\n🔍 Búsqueda: '{query}'")
        results = fallback.search_clubs(query, 5)
        
        for i, club in enumerate(results, 1):
            print(f"   {i}. {club['name']} ({club['country']}) - {club['formatted_market_value']} - Score: {club['search_score']:.1f}")
    
    # Prueba de club específico
    print(f"\n🏆 Club específico: 'Barcelona'")
    club = fallback.get_club_by_name('Barcelona')
    if club:
        print(f"   Nombre: {club['name']}")
        print(f"   País: {club['country']}")
        print(f"   Valor: {club['formatted_market_value']}")
        print(f"   Tier: {club['tier']}")
        print(f"   Estadio: {club['stadium']}")
        print(f"   Capacidad: {club['capacity']:,}")
    
    # Estadísticas
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total clubes: {len(fallback.clubs_database)}")
    print(f"   Cache entries: {len(fallback.search_cache)}")
    
    tier_counts = {}
    for club_data in fallback.clubs_database.values():
        tier = club_data.get('tier', 2)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    for tier, count in sorted(tier_counts.items()):
        print(f"   Tier {tier}: {count} clubes")

if __name__ == "__main__":
    demonstrate_enhanced_fallback()
