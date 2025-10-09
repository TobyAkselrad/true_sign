#!/usr/bin/env python3
"""
Script para integrar los clubes del JSON en enhanced_clubs_fallback.py
"""

import json

def load_clubs_database():
    """Cargar base de datos de clubes"""
    with open('clubs_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['clubs']

def generate_python_dict():
    """Generar diccionario Python para enhanced_clubs_fallback.py"""
    clubs = load_clubs_database()
    
    print("# CLUBES GENERADOS AUTOMÁTICAMENTE")
    print("# Total: {} clubes".format(len(clubs)))
    print("# Generado desde: clubs_database.json")
    print()
    
    # Agrupar por país para mejor organización
    clubs_by_country = {}
    for club_id, club_data in clubs.items():
        country = club_data['country'] or 'Unknown'
        if country not in clubs_by_country:
            clubs_by_country[country] = []
        clubs_by_country[country].append((club_id, club_data))
    
    # Ordenar por valor de mercado dentro de cada país
    for country in clubs_by_country:
        clubs_by_country[country].sort(key=lambda x: x[1]['market_value'], reverse=True)
    
    # Generar código Python
    print("clubs_database = {")
    
    for country in sorted(clubs_by_country.keys(), key=lambda x: (x == 'Unknown', x)):
        clubs_list = clubs_by_country[country]
        print(f"    # CLUBES DE {country.upper()} ({len(clubs_list)} clubes)")
        
        for club_id, club_data in clubs_list:
            name = club_data['name']
            safe_key = name.replace("'", "\\'")
            
            print(f"    '{safe_key}': {{")
            print(f"        'name': '{safe_key}',")
            print(f"        'country': '{club_data['country']}',")
            print(f"        'market_value': {club_data['market_value']},")
            print(f"        'league': '{club_data['league']}',")
            print(f"        'tier': {club_data['tier']},")
            print(f"        'aliases': {club_data['aliases']},")
            print(f"        'founded': {club_data['founded']},")
            print(f"        'stadium': '{club_data['stadium']}',")
            print(f"        'capacity': {club_data['capacity']}")
            print(f"    }},")
        
        print()
    
    print("}")

def generate_summary():
    """Generar resumen de clubes"""
    clubs = load_clubs_database()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE CLUBES")
    print("=" * 70)
    
    # Agrupar por país
    by_country = {}
    for club_data in clubs.values():
        country = club_data['country'] or 'Unknown'
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(club_data)
    
    for country, clubs_list in sorted(by_country.items()):
        total_value = sum(c['market_value'] for c in clubs_list)
        avg_value = total_value / len(clubs_list) if clubs_list else 0
        
        print(f"\n🌍 {country}:")
        print(f"   Clubes: {len(clubs_list)}")
        print(f"   Valor total: €{total_value:,}")
        print(f"   Valor promedio: €{avg_value:,.0f}")
        
        # Top 3 del país
        top_3 = sorted(clubs_list, key=lambda x: x['market_value'], reverse=True)[:3]
        print(f"   Top 3:")
        for i, club in enumerate(top_3, 1):
            print(f"      {i}. {club['name']} - €{club['market_value']:,}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'summary':
        generate_summary()
    else:
        generate_python_dict()

