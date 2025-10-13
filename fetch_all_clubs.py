#!/usr/bin/env python3
"""
Script para obtener TODOS los clubes desde transfermarkt-api.fly.dev
Recorre todos los IDs y hace reintentos para los que fallan.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional, List
import sys

class ClubsFetcher:
    def __init__(self, start_id: int = 1, max_consecutive_404s: int = 50):
        self.base_url = "https://transfermarkt-api.fly.dev/clubs"
        self.start_id = start_id
        self.max_consecutive_404s = max_consecutive_404s  # Parar después de N 404s consecutivos
        self.clubs = {}
        self.failed_ids = {}  # {id: attempt_count}
        self.not_found_ids = []  # IDs definitivamente no encontrados después de 3 intentos
        self.consecutive_404s = 0
        self.total_requests = 0
        self.successful_requests = 0
        
    def fetch_club_profile(self, club_id: int) -> Optional[Dict]:
        """Obtener perfil de un club por ID"""
        url = f"{self.base_url}/{club_id}/profile"
        
        try:
            response = requests.get(url, timeout=10)
            self.total_requests += 1
            
            if response.status_code == 200:
                self.consecutive_404s = 0  # Reset contador
                self.successful_requests += 1
                return response.json()
            elif response.status_code == 404:
                self.consecutive_404s += 1
                return None
            else:
                print(f"   ⚠️  ID {club_id}: Status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  ID {club_id}: Timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"   ❌ ID {club_id}: Error - {str(e)}")
            return None
    
    def generate_aliases(self, name: str, official_name: str) -> List[str]:
        """Generar aliases automáticamente basados en el nombre"""
        aliases = []
        
        # Agregar nombre principal
        if name:
            aliases.append(name)
        
        # Agregar nombre oficial si es diferente
        if official_name and official_name != name:
            aliases.append(official_name)
        
        # Generar variaciones comunes
        if name:
            # Sin prefijos comunes (Club, FC, etc.)
            for prefix in ['Club ', 'FC ', 'CF ', 'CA ', 'CD ', 'CS ', 'AC ', 'SC ', 'Deportivo ']:
                if name.startswith(prefix):
                    short_name = name[len(prefix):].strip()
                    if short_name and short_name not in aliases:
                        aliases.append(short_name)
            
            # Sin sufijos comunes (FC, SC, etc.)
            for suffix in [' FC', ' SC', ' CF', ' AC', ' United', ' City']:
                if name.endswith(suffix):
                    short_name = name[:-len(suffix)].strip()
                    if short_name and short_name not in aliases:
                        aliases.append(short_name)
        
        return aliases[:5]  # Máximo 5 aliases
    
    def format_club_data(self, raw_data: Dict) -> Dict:
        """Formatear datos del club a la estructura esperada"""
        try:
            # Extraer campos básicos
            club_id = raw_data.get('id', '')
            name = raw_data.get('name', '')
            official_name = raw_data.get('officialName', name)
            
            # Extraer año de fundación
            founded_str = raw_data.get('foundedOn', '')
            founded = None
            if founded_str:
                try:
                    founded = int(founded_str.split('-')[0])
                except:
                    founded = None
            
            # Extraer datos de liga
            league_data = raw_data.get('league', {})
            country = league_data.get('countryName', '')
            league = league_data.get('name', '')
            league_id = league_data.get('id', '')
            tier_str = league_data.get('tier', '')
            
            # Convertir tier a entero
            tier = None
            if tier_str:
                try:
                    tier = int(tier_str)
                except:
                    tier = None
            
            # Market value
            market_value = raw_data.get('currentMarketValue', 0)
            if market_value is None:
                market_value = 0
            
            # Estadio
            stadium = raw_data.get('stadiumName', '')
            capacity = raw_data.get('stadiumSeats', 0)
            if capacity is None:
                capacity = 0
            
            # Imagen
            image = raw_data.get('image', '')
            
            # URL
            url = raw_data.get('url', '')
            
            # Squad size
            squad_data = raw_data.get('squad', {})
            squad_size = squad_data.get('size', 0) if squad_data else 0
            
            # Generar aliases
            aliases = self.generate_aliases(name, official_name)
            
            # Construir estructura
            formatted = {
                'name': name,
                'official_name': official_name,
                'country': country,
                'market_value': market_value,
                'league': league,
                'league_id': league_id,
                'tier': tier,
                'founded': founded,
                'stadium': stadium,
                'capacity': capacity,
                'squad_size': squad_size,
                'image': image,
                'url': url,
                'aliases': aliases
            }
            
            return formatted
            
        except Exception as e:
            print(f"   ❌ Error formateando datos: {e}")
            return None
    
    def fetch_all_clubs(self):
        """Obtener todos los clubes desde start_id hasta encontrar muchos 404s consecutivos"""
        print("🚀 INICIANDO OBTENCIÓN MASIVA DE CLUBES")
        print("=" * 70)
        print(f"🔗 Endpoint: {self.base_url}")
        print(f"📍 Desde ID: {self.start_id}")
        print(f"🛑 Parar después de {self.max_consecutive_404s} 404s consecutivos")
        print(f"🔄 Reintentos: 3 por cada ID fallido")
        print("=" * 70)
        
        current_id = self.start_id
        clubs_found_this_batch = 0
        save_interval = 50  # Guardar cada 50 clubes encontrados
        
        while self.consecutive_404s < self.max_consecutive_404s:
            # Mostrar progreso
            if current_id % 10 == 0:
                print(f"\n📊 Progreso: ID {current_id} | Encontrados: {len(self.clubs)} | "
                      f"404s consecutivos: {self.consecutive_404s}/{self.max_consecutive_404s}")
            
            # Intentar obtener club
            print(f"🔍 ID {current_id}...", end=" ")
            raw_data = self.fetch_club_profile(current_id)
            
            if raw_data:
                # Formatear y guardar
                formatted = self.format_club_data(raw_data)
                if formatted and formatted.get('name'):
                    self.clubs[str(current_id)] = formatted
                    clubs_found_this_batch += 1
                    print(f"✅ {formatted['name']} ({formatted.get('country', 'N/A')})")
                    
                    # Guardar incrementalmente
                    if clubs_found_this_batch >= save_interval:
                        self.save_clubs(incremental=True)
                        clubs_found_this_batch = 0
                else:
                    print(f"⚠️  Datos inválidos")
            else:
                print(f"❌ No encontrado")
                # Registrar para reintentos
                self.failed_ids[current_id] = 1
            
            current_id += 1
            
            # Rate limiting (evitar sobrecargar la API)
            time.sleep(0.1)  # 100ms entre requests
        
        print(f"\n\n🛑 Alcanzado límite de 404s consecutivos ({self.max_consecutive_404s})")
        print(f"📍 Último ID intentado: {current_id - 1}")
        
        # Guardar antes de reintentos
        self.save_clubs(incremental=True)
        
        # Fase de reintentos
        self.retry_failed_clubs()
        
        # Guardar final
        self.save_clubs(final=True)
        
        # Mostrar estadísticas
        self.print_statistics()
    
    def retry_failed_clubs(self):
        """Reintentar clubes que fallaron, hasta 3 intentos cada uno"""
        if not self.failed_ids:
            print("\n✅ No hay clubes para reintentar")
            return
        
        print(f"\n\n🔄 FASE DE REINTENTOS")
        print("=" * 70)
        print(f"🎯 Total IDs a reintentar: {len(self.failed_ids)}")
        print("=" * 70)
        
        failed_ids_list = list(self.failed_ids.keys())
        
        for club_id in failed_ids_list:
            attempts = self.failed_ids[club_id]
            
            while attempts < 3:
                attempts += 1
                print(f"🔄 Reintento {attempts}/3 para ID {club_id}...", end=" ")
                
                raw_data = self.fetch_club_profile(club_id)
                
                if raw_data:
                    formatted = self.format_club_data(raw_data)
                    if formatted and formatted.get('name'):
                        self.clubs[str(club_id)] = formatted
                        print(f"✅ {formatted['name']} ({formatted.get('country', 'N/A')})")
                        del self.failed_ids[club_id]
                        break
                    else:
                        print(f"⚠️  Datos inválidos")
                else:
                    print(f"❌ Intento {attempts} fallido")
                
                self.failed_ids[club_id] = attempts
                time.sleep(0.5)  # Esperar más entre reintentos
            
            # Si llegó a 3 intentos y sigue fallando
            if club_id in self.failed_ids and self.failed_ids[club_id] >= 3:
                self.not_found_ids.append(club_id)
                print(f"   ❌ ID {club_id} no encontrado después de 3 intentos")
        
        print(f"\n✅ Reintentos completados")
    
    def save_clubs(self, incremental=False, final=False):
        """Guardar clubes en archivo JSON"""
        if not self.clubs:
            return
        
        filename = 'clubs_database.json'
        
        # Cargar datos existentes si es incremental
        existing_data = {}
        if incremental:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = {
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_clubs': 0
                    },
                    'clubs': {}
                }
        
        # Preparar metadata
        metadata = {
            'generated_at': existing_data.get('metadata', {}).get('generated_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat(),
            'total_clubs': len(self.clubs),
            'source': 'transfermarkt-api.fly.dev',
            'stats': {
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'failed_ids_count': len(self.not_found_ids)
            }
        }
        
        # Combinar clubs existentes con nuevos
        all_clubs = existing_data.get('clubs', {})
        all_clubs.update(self.clubs)
        metadata['total_clubs'] = len(all_clubs)
        
        data = {
            'metadata': metadata,
            'clubs': all_clubs
        }
        
        # Guardar
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        status = "💾 GUARDADO FINAL" if final else "💾 Guardado incremental"
        print(f"\n{status}: {len(all_clubs)} clubes en {filename}")
    
    def print_statistics(self):
        """Mostrar estadísticas finales"""
        print("\n\n" + "=" * 70)
        print("📊 ESTADÍSTICAS FINALES")
        print("=" * 70)
        print(f"✅ Clubes encontrados: {len(self.clubs)}")
        print(f"📡 Total requests: {self.total_requests}")
        print(f"✅ Requests exitosos: {self.successful_requests}")
        print(f"❌ IDs no encontrados (después de 3 intentos): {len(self.not_found_ids)}")
        
        if self.not_found_ids:
            print(f"\n❌ LISTA DE IDs NO ENCONTRADOS:")
            print("=" * 70)
            # Mostrar en grupos de 10
            for i in range(0, len(self.not_found_ids), 10):
                batch = self.not_found_ids[i:i+10]
                print(f"   {', '.join(map(str, batch))}")
        
        # Estadísticas por país
        if self.clubs:
            countries = {}
            for club in self.clubs.values():
                country = club.get('country', 'Unknown')
                countries[country] = countries.get(country, 0) + 1
            
            print(f"\n🌍 DISTRIBUCIÓN POR PAÍS (Top 10):")
            print("=" * 70)
            sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]
            for country, count in sorted_countries:
                print(f"   {country}: {count} clubes")
        
        print("=" * 70)
        print("✅ Proceso completado!")
        print(f"💾 Datos guardados en: clubs_database.json")
        print("=" * 70)


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("🏆 FETCHER DE CLUBES - TRANSFERMARKT API")
    print("=" * 70)
    
    # Preguntar desde qué ID empezar
    try:
        start_input = input("\n📍 ID inicial (Enter para empezar desde 1): ").strip()
        start_id = int(start_input) if start_input else 1
    except ValueError:
        print("⚠️  ID inválido, usando 1")
        start_id = 1
    
    # Preguntar cuántos 404s consecutivos antes de parar
    try:
        max_404_input = input("🛑 Máximo de 404s consecutivos antes de parar (Enter para 50): ").strip()
        max_404s = int(max_404_input) if max_404_input else 50
    except ValueError:
        print("⚠️  Valor inválido, usando 50")
        max_404s = 50
    
    # Confirmación
    print(f"\n✅ Configuración:")
    print(f"   - ID inicial: {start_id}")
    print(f"   - Parar después de: {max_404s} 404s consecutivos")
    print(f"   - Reintentos por ID: 3")
    print(f"   - Guardado incremental: cada 50 clubes")
    
    confirm = input("\n¿Continuar? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # Iniciar fetcher
    fetcher = ClubsFetcher(start_id=start_id, max_consecutive_404s=max_404s)
    
    try:
        fetcher.fetch_all_clubs()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        fetcher.save_clubs(final=True)
        fetcher.print_statistics()
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        fetcher.save_clubs(final=True)
        fetcher.print_statistics()


if __name__ == "__main__":
    main()

