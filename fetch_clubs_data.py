#!/usr/bin/env python3
"""
Script para obtener información de clubes desde la API de Transfermarkt
y generar un JSON con los datos relevantes para la aplicación.
"""

import requests
import json
import time
from datetime import datetime

# Competencias a procesar
COMPETITIONS = ['ARG1', 'ARG2', 'URU1', 'URU2', 'CLPD', 'BRC', 'MEX1', 'MEX2']

BASE_URL = "https://transfermarkt-api.fly.dev"
HEADERS = {'accept': 'application/json'}

# Delay entre requests para no saturar la API
DELAY_BETWEEN_REQUESTS = 0.5
DELAY_BETWEEN_COMPETITIONS = 2.0

def fetch_competition_clubs(competition_id):
    """Obtener lista de clubes de una competencia"""
    url = f"{BASE_URL}/competitions/{competition_id}/clubs?season_id=2024"
    
    try:
        print(f"📡 Obteniendo clubes de {competition_id}...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            clubs = data.get('clubs', [])
            print(f"   ✅ {len(clubs)} clubes encontrados en {competition_id}")
            return clubs
        else:
            print(f"   ❌ Error {response.status_code} en {competition_id}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error obteniendo {competition_id}: {e}")
        return []

def fetch_club_profile(club_id, club_name):
    """Obtener perfil completo de un club"""
    url = f"{BASE_URL}/clubs/{club_id}/profile"
    
    try:
        print(f"   📊 Obteniendo perfil de {club_name} (ID: {club_id})...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ Perfil obtenido")
            return data
        else:
            print(f"      ⚠️ Error {response.status_code}")
            return None
            
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
        return None

def extract_relevant_data(profile):
    """Extraer solo los datos relevantes para la app"""
    if not profile:
        return None
    
    try:
        # Extraer league info
        league_info = profile.get('league', {})
        tier_text = league_info.get('tier', 'Unknown Tier')
        
        # Mapear tier text a número
        tier_mapping = {
            'First Tier': 1,
            'Second Tier': 2,
            'Third Tier': 3,
            'Fourth Tier': 4
        }
        tier = tier_mapping.get(tier_text, 2)
        
        # Procesar año de fundación
        founded_on = profile.get('foundedOn', '')
        try:
            founded = int(founded_on.split('-')[0]) if founded_on else 1900
        except:
            founded = 1900
        
        relevant_data = {
            'name': profile.get('name', ''),
            'official_name': profile.get('officialName', ''),
            'country': profile.get('addressLine3', ''),
            'market_value': profile.get('currentMarketValue', 0),
            'league': league_info.get('name', ''),
            'league_id': league_info.get('id', ''),
            'tier': tier,
            'founded': founded,
            'stadium': profile.get('stadiumName', ''),
            'capacity': profile.get('stadiumSeats', 0),
            'squad_size': profile.get('squad', {}).get('size', 0),
            'image': profile.get('image', ''),
            'url': profile.get('url', '')
        }
        
        return relevant_data
        
    except Exception as e:
        print(f"      ❌ Error extrayendo datos: {e}")
        return None

def generate_aliases(club_name):
    """Generar aliases comunes para un club"""
    aliases = [club_name]
    
    # Remover prefijos comunes
    prefixes_to_remove = ['Club ', 'CA ', 'CF ', 'CD ', 'FC ', 'AC ', 'AS ']
    for prefix in prefixes_to_remove:
        if club_name.startswith(prefix):
            aliases.append(club_name.replace(prefix, '', 1))
    
    # Agregar versión sin sufijos
    suffixes_to_remove = [' FC', ' CF', ' CD', ' CA', ' AC', ' AS']
    for suffix in suffixes_to_remove:
        if club_name.endswith(suffix):
            aliases.append(club_name.replace(suffix, '', 1))
    
    # Quitar duplicados
    return list(set(aliases))

def main():
    """Función principal"""
    print("=" * 70)
    print("🌐 RECOPILACIÓN DE DATOS DE CLUBES - TRANSFERMARKT API")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Competencias: {', '.join(COMPETITIONS)}")
    print("=" * 70)
    
    all_clubs_data = {}
    stats = {
        'total_competitions': len(COMPETITIONS),
        'total_clubs_found': 0,
        'total_profiles_fetched': 0,
        'errors': 0
    }
    
    for competition_id in COMPETITIONS:
        print(f"\n{'='*70}")
        print(f"🏆 Procesando competencia: {competition_id}")
        print(f"{'='*70}")
        
        # Obtener lista de clubes
        clubs = fetch_competition_clubs(competition_id)
        stats['total_clubs_found'] += len(clubs)
        
        if not clubs:
            print(f"⚠️ No se encontraron clubes en {competition_id}")
            time.sleep(DELAY_BETWEEN_COMPETITIONS)
            continue
        
        # Obtener perfil de cada club
        for i, club in enumerate(clubs, 1):
            club_id = club.get('id')
            club_name = club.get('name', 'Unknown')
            
            print(f"\n   [{i}/{len(clubs)}] Procesando: {club_name}")
            
            # Verificar si ya tenemos este club
            if club_id in all_clubs_data:
                print(f"      ⏭️  Club ya procesado, saltando...")
                continue
            
            # Obtener perfil
            profile = fetch_club_profile(club_id, club_name)
            
            if profile:
                relevant_data = extract_relevant_data(profile)
                
                if relevant_data:
                    # Agregar aliases
                    relevant_data['aliases'] = generate_aliases(relevant_data['name'])
                    
                    # Guardar
                    all_clubs_data[club_id] = relevant_data
                    stats['total_profiles_fetched'] += 1
                    
                    print(f"      ✅ Guardado: {relevant_data['name']}")
                    print(f"         País: {relevant_data['country']}")
                    print(f"         Valor: €{relevant_data['market_value']:,}")
                    print(f"         Liga: {relevant_data['league']}")
                else:
                    stats['errors'] += 1
            else:
                stats['errors'] += 1
            
            # Delay entre requests
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        # Delay entre competencias
        print(f"\n✅ Competencia {competition_id} completada")
        time.sleep(DELAY_BETWEEN_COMPETITIONS)
    
    # Guardar resultado
    output_file = 'clubs_database.json'
    
    result = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'competitions': COMPETITIONS,
            'total_clubs': len(all_clubs_data),
            'stats': stats
        },
        'clubs': all_clubs_data
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    print(f"✅ Competencias procesadas: {stats['total_competitions']}")
    print(f"✅ Clubes encontrados: {stats['total_clubs_found']}")
    print(f"✅ Perfiles obtenidos: {stats['total_profiles_fetched']}")
    print(f"⚠️ Errores: {stats['errors']}")
    print(f"💾 Archivo generado: {output_file}")
    print("=" * 70)
    
    # Mostrar algunos ejemplos
    print("\n📋 Ejemplos de clubes guardados:")
    for i, (club_id, club_data) in enumerate(list(all_clubs_data.items())[:5], 1):
        print(f"{i}. {club_data['name']} ({club_data['country']}) - €{club_data['market_value']:,}")
    
    print(f"\n🎉 ¡Proceso completado!")
    print(f"📁 Datos guardados en: {output_file}")

if __name__ == "__main__":
    main()

