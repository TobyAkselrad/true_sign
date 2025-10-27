import sys
import os

# Agregar directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd
import json
from datetime import datetime, timedelta
from scraping.transfermarkt_scraper import TransfermarktScraper
import logging

logger = logging.getLogger(__name__)

class HybridPlayerSearch:
    def __init__(self, csv_file="players_data.csv"):
        self.csv_file = csv_file
        self.scraper = TransfermarktScraper()
        self.df = None
        self.load_database()
    
    def load_database(self):
        """Cargar base de datos local"""
        try:
            if os.path.exists(self.csv_file):
                self.df = pd.read_csv(self.csv_file)
                logger.info(f"Base de datos cargada: {len(self.df)} jugadores")
            else:
                logger.warning(f"Archivo {self.csv_file} no encontrado")
                self.df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error cargando base de datos: {e}")
            self.df = pd.DataFrame()
    
    def search_player(self, player_name, use_scraping=True):
        """
        Buscar jugador con sistema híbrido:
        1. Cache del scraper (últimas 24h)
        2. Scraping en vivo (solo si use_scraping=True)
        3. Fallback a base de datos local
        """
        logger.info(f"Buscando jugador: {player_name}")
        
        # 1. Verificar cache primero (más rápido y evita 403)
        try:
            cache_data = self.scraper.cache
            if cache_data:
                normalized_cache_key = player_name.lower()
                if normalized_cache_key in cache_data:
                    cached_entry = cache_data[normalized_cache_key]
                    if cached_entry and cached_entry.get('data'):
                        cached_data = cached_entry['data']
                        if cached_data and self._validate_scraped_data(cached_data):
                            logger.info(f"Datos obtenidos del cache para {player_name}")
                            return self._format_scraped_data(cached_data)
        except Exception as e:
            logger.warning(f"Error verificando cache: {e}")
        
        # 2. Intentar scraping en vivo (solo si está habilitado)
        if use_scraping:
            try:
                scraped_data = self.scraper.search_player(player_name)
                if scraped_data and self._validate_scraped_data(scraped_data):
                    logger.info(f"Datos obtenidos por scraping para {player_name}")
                    return self._format_scraped_data(scraped_data)
            except Exception as e:
                logger.warning(f"Error en scraping para {player_name}: {e}")
                # Si falla el scraping en vivo, continuar sin romper
        
        # 3. Fallback a base de datos local
        try:
            db_data = self._search_in_database(player_name)
            if db_data is not None:
                logger.info(f"Datos obtenidos de base de datos para {player_name}")
                return db_data
        except Exception as e:
            logger.warning(f"Error en búsqueda en BD para {player_name}: {e}")
        
        # 4. No se encontró el jugador
        logger.warning(f"Jugador no encontrado: {player_name}")
        return None
    
    def _validate_scraped_data(self, data):
        """Validar que los datos scrapeados sean válidos"""
        if not data:
            return False
        
        # Verificar campos mínimos
        required_fields = ['name', 'market_value']
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        
        return True
    
    def _format_scraped_data(self, scraped_data):
        """Formatear datos scrapeados al formato esperado"""
        try:
            formatted_data = {
                'player_name': scraped_data.get('name', ''),
                'current_club_name': scraped_data.get('current_club', ''),
                'market_value': scraped_data.get('market_value', 0),
                'age': scraped_data.get('age', 0),
                'position': scraped_data.get('position', ''),
                'height': scraped_data.get('height', ''),
                'foot': scraped_data.get('foot', ''),
                'nationality': scraped_data.get('nationality', ''),
                'contract_until': scraped_data.get('contract_until', ''),
                'source': 'scraping'
            }
            
            # Convertir valor de mercado a float si es necesario
            if isinstance(formatted_data['market_value'], str):
                formatted_data['market_value'] = float(formatted_data['market_value'])
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formateando datos scrapeados: {e}")
            return None
    
    def _search_in_database(self, player_name):
        """Buscar jugador en base de datos local"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            # Búsqueda exacta primero
            exact_match = self.df[self.df['player_name'].str.lower() == player_name.lower()]
            if not exact_match.empty:
                return exact_match.iloc[0].to_dict()
            
            # Búsqueda parcial
            partial_match = self.df[self.df['player_name'].str.contains(player_name, case=False, na=False)]
            if not partial_match.empty:
                return partial_match.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Error en búsqueda en BD: {e}")
            return None
    
    def get_autocomplete_suggestions(self, query, limit=10):
        """Obtener sugerencias de autocompletado con scraping en vivo"""
        suggestions = []
        
        # 1. Buscar en cache del scraper primero (más rápido)
        try:
            cache_suggestions = []
            for player_name in self.scraper.cache.keys():
                if query.lower() in player_name.lower():
                    cache_suggestions.append(player_name)
            
            suggestions.extend(cache_suggestions[:limit])
        except Exception as e:
            logger.error(f"Error en autocompletado cache: {e}")
        
        # 2. Si no hay suficientes sugerencias, hacer scraping en vivo
        if len(suggestions) < limit and len(query) >= 3:
            try:
                logger.info(f"🌐 Autocompletado en vivo para: {query}")
                live_suggestions = self.scraper.search_players_autocomplete(query, limit - len(suggestions))
                
                # Agregar sugerencias en vivo que no estén ya en la lista
                for suggestion in live_suggestions:
                    if suggestion not in suggestions:
                        suggestions.append(suggestion)
                        
            except Exception as e:
                logger.error(f"Error en autocompletado en vivo: {e}")
        
        # 3. Fallback a base de datos local si aún no hay suficientes
        if len(suggestions) < limit and self.df is not None and not self.df.empty:
            try:
                db_suggestions = self.df[
                    self.df['player_name'].str.contains(query, case=False, na=False)
                ]['player_name'].head(limit - len(suggestions)).tolist()
                
                for suggestion in db_suggestions:
                    if suggestion not in suggestions:
                        suggestions.append(suggestion)
            except Exception as e:
                logger.error(f"Error en autocompletado BD: {e}")
        
        return suggestions[:limit]
    
    def get_club_suggestions(self, query, limit=10):
        """Obtener sugerencias de clubes"""
        suggestions = []
        
        # Buscar en base de datos local
        if self.df is not None and not self.df.empty:
            try:
                club_suggestions = self.df[
                    self.df['current_club_name'].str.contains(query, case=False, na=False)
                ]['current_club_name'].dropna().unique().tolist()
                suggestions.extend(club_suggestions[:limit])
            except Exception as e:
                logger.error(f"Error en sugerencias de clubes: {e}")
        
        return suggestions[:limit]
    
    def update_database(self, player_data):
        """Actualizar base de datos con nuevos datos"""
        try:
            if self.df is None:
                self.df = pd.DataFrame()
            
            # Verificar si el jugador ya existe
            existing = self.df[self.df['player_name'].str.lower() == player_data['player_name'].lower()]
            
            if not existing.empty:
                # Actualizar jugador existente
                idx = existing.index[0]
                for key, value in player_data.items():
                    self.df.at[idx, key] = value
            else:
                # Agregar nuevo jugador
                new_row = pd.DataFrame([player_data])
                self.df = pd.concat([self.df, new_row], ignore_index=True)
            
            # Guardar base de datos
            self.df.to_csv(self.csv_file, index=False)
            logger.info(f"Base de datos actualizada con {player_data['player_name']}")
            
        except Exception as e:
            logger.error(f"Error actualizando base de datos: {e}")
    
    def get_cache_stats(self):
        """Obtener estadísticas del cache"""
        try:
            total_cached = len(self.scraper.cache)
            valid_cached = sum(1 for player in self.scraper.cache.values() 
                             if self.scraper.is_cache_valid(player, 24))
            
            return {
                'total_cached': total_cached,
                'valid_cached': valid_cached,
                'expired_cached': total_cached - valid_cached
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'total_cached': 0, 'valid_cached': 0, 'expired_cached': 0}

# Función de conveniencia
def search_player_hybrid(player_name, use_scraping=True):
    """Función principal para búsqueda híbrida"""
    searcher = HybridPlayerSearch()
    return searcher.search_player(player_name, use_scraping)

if __name__ == "__main__":
    # Test del sistema híbrido
    searcher = HybridPlayerSearch()
    
    test_players = ["Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé", "Jugador Inexistente"]
    
    for player in test_players:
        print(f"\n=== Buscando {player} ===")
        data = searcher.search_player(player)
        if data:
            print(f"Nombre: {data.get('player_name')}")
            print(f"Club: {data.get('current_club_name')}")
            print(f"Valor: €{data.get('market_value', 0):,}")
            print(f"Fuente: {data.get('source', 'desconocida')}")
        else:
            print("No se encontraron datos")
        
        print(f"Estadísticas cache: {searcher.get_cache_stats()}")
