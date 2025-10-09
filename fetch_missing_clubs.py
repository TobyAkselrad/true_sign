#!/usr/bin/env python3
"""
Script para agregar los clubes faltantes (MEX1 y BRC) a clubs_database.json
"""

import requests
import json
import time
from datetime import datetime

# Competencias faltantes
MISSING_COMPETITIONS = ['MEX1', 'BRC']

BASE_URL = "https://transfermarkt-api.fly.dev"
HEADERS = {'accept': 'application/json'}
DELAY = 0.5

def fetch_competition_clubs(competition_id):
    """Obtener lista de clubes de una competencia"""
    url = f"{BASE_URL}/competitions/{competition_id}/clubs?season_id=2024"
    
    try:
        print(f"📡 Obteniendo clubes de {competition_id}...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            clubs = data.get('clubs', [])
            print(f"   ✅ {len(clubs)} clubes encontrados")
            return clubs
        else:
            print(f"   ❌ Error {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def fetch_club_profile(club_id, club_name):
    """Obtener perfil completo de un club"""
    url = f"{BASE_URL}/clubs/{club_id}/profile"
    
    try:
        print(f"      📊 {club_name}...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"      ⚠️ Error {response.status_code}")
            return None
            
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
        return None

def extract_relevant_data(profile):
    """Extraer datos relevantes"""
    if not profile:
        return None
    
    try:
        league_info = profile.get('league', {})
        tier_text = league_info.get('tier', 'Unknown Tier')
        
        tier_mapping = {
            'First Tier': 1,
            'Second Tier': 2,
            'Third Tier': 3,
            'Fourth Tier': 4
        }
        tier = tier_mapping.get(tier_text, 2)
        
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
        
        # Generar aliases
        aliases = [relevant_data['name']]
        for prefix in ['Club ', 'CA ', 'CF ', 'CD ', 'FC ', 'AC ', 'AS ']:
            if relevant_data['name'].startswith(prefix):
                aliases.append(relevant_data['name'].replace(prefix, '', 1))
        for suffix in [' FC', ' CF', ' CD', ' CA', ' AC', ' AS']:
            if relevant_data['name'].endswith(suffix):
                aliases.append(relevant_data['name'].replace(suffix, '', 1))
        
        relevant_data['aliases'] = list(set(aliases))
        
        return relevant_data
        
    except Exception as e:
        print(f"      ❌ Error extrayendo: {e}")
        return None

def main():
    """Agregar clubes faltantes"""
    print("=" * 70)
    print("🔄 AGREGANDO CLUBES FALTANTES (MEX1 y BRC)")
    print("=" * 70)
    
    # Cargar JSON actual
    print("\n📂 Cargando clubs_database.json...")
    try:
        with open('clubs_database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        print("❌ No se pudo cargar clubs_database.json")
        return
    
    print(f"   Clubes actuales: {len(db['clubs'])}")
    
    added_count = 0
    errors_count = 0
    
    for comp_id in MISSING_COMPETITIONS:
        print(f"\n{'='*70}")
        print(f"🏆 Procesando: {comp_id}")
        print(f"{'='*70}")
        
        clubs = fetch_competition_clubs(comp_id)
        
        if not clubs:
            continue
        
        print(f"\n   Procesando {len(clubs)} clubes...")
        
        for i, club in enumerate(clubs, 1):
            club_id = club.get('id')
            club_name = club.get('name', 'Unknown')
            
            # Verificar si ya existe
            if club_id in db['clubs']:
                print(f"   [{i}/{len(clubs)}] {club_name} - Ya existe ⏭️")
                continue
            
            print(f"   [{i}/{len(clubs)}] {club_name}...", end=' ')
            
            # Obtener perfil
            profile = fetch_club_profile(club_id, club_name)
            time.sleep(DELAY)
            
            if profile:
                relevant_data = extract_relevant_data(profile)
                
                if relevant_data:
                    db['clubs'][club_id] = relevant_data
                    added_count += 1
                    print(f"✅ Agregado (€{relevant_data['market_value']:,})")
                else:
                    errors_count += 1
                    print("❌ Error extrayendo")
            else:
                errors_count += 1
                print("❌ Error obteniendo perfil")
    
    # Actualizar metadata
    db['metadata']['total_clubs'] = len(db['clubs'])
    db['metadata']['stats']['total_profiles_fetched'] = len(db['clubs'])
    db['metadata']['updated_at'] = datetime.now().isoformat()
    
    # Guardar
    print(f"\n{'='*70}")
    print("💾 Guardando clubs_database.json...")
    with open('clubs_database.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print("📊 RESUMEN")
    print(f"{'='*70}")
    print(f"✅ Clubes agregados: {added_count}")
    print(f"⚠️ Errores: {errors_count}")
    print(f"📊 Total clubes ahora: {len(db['clubs'])}")
    print(f"💾 Archivo actualizado: clubs_database.json")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()

