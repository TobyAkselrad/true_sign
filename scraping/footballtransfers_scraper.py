import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime, timedelta
import re
from urllib.parse import quote
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballTransfersScraper:
    def __init__(self):
        self.session = requests.Session()
        self.cache_file = "footballtransfers_cache.json"
        self.cache = self.load_cache()
        
        # Headers para FootballTransfers
        # NOTA: No incluir Accept-Encoding explícitamente, requests lo maneja automáticamente
        # y puede causar problemas con la descompresión
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',  # Removido - requests lo maneja automáticamente
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        self.session.headers.update(self.headers)
    
    def load_cache(self):
        """Cargar cache desde archivo"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Guardar cache en archivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando cache: {e}")
    
    def is_cache_valid(self, player_name, ttl_hours=24):
        """Verificar si el cache es válido"""
        if player_name not in self.cache:
            return False
        
        cached_time = datetime.fromisoformat(self.cache[player_name]['timestamp'])
        return datetime.now() - cached_time < timedelta(hours=ttl_hours)
    
    def search_player(self, player_name):
        """Buscar jugador en FootballTransfers"""
        # 1. Verificar cache primero
        normalized_name = player_name.lower().strip()
        if self.is_cache_valid(normalized_name):
            logger.info(f"✅ Cache hit para {player_name}")
            return self.cache[normalized_name]['data']
        
        # 2. Scraping en vivo
        try:
            logger.info(f"🌐 Scraping en vivo para {player_name}")
            player_data = self._scrape_player_data(player_name)
            
            # Solo guardar en cache si obtuvimos datos válidos
            if player_data and player_data.get('market_value', 0) > 0:
                self.cache[normalized_name] = {
                    'data': player_data,
                    'timestamp': datetime.now().isoformat()
                }
                self.save_cache()
                logger.info(f"✅ Datos guardados en cache para {player_name}")
                return player_data
            else:
                logger.warning(f"⚠️ Scraping no obtuvo datos válidos para {player_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error scraping {player_name}: {e}")
            return None
    
    def _scrape_player_data(self, player_name):
        """Scraping real de FootballTransfers"""
        try:
            # Construir URL de búsqueda - primero intentar búsqueda directa
            # FootballTransfers usa slugs en la URL como: /en/players/lionel-messi
            search_slug = self._create_player_slug(player_name)
            search_url = f"https://www.footballtransfers.com/en/players/{search_slug}"
            
            logger.info(f"🔍 Buscando en FootballTransfers: {search_url}")
            
            # Delay aleatorio para evitar rate limiting
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(search_url, timeout=15)
            logger.info(f"📡 Response status: {response.status_code}")
            
            # Si no encontramos con el slug, intentar búsqueda alternativa
            if response.status_code == 404:
                logger.info(f"⚠️ 404 con slug directo, intentando búsqueda con variaciones...")
                return self._try_search_page(player_name)
            
            if response.status_code == 403:
                logger.warning(f"⚠️ 403 bloqueado por FootballTransfers")
                return None
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: verificar qué contiene la página
            title = soup.find('title')
            if title:
                logger.info(f"📄 Título de la página: {title.get_text()}")
            
            # Verificar que es una página de jugador (no de búsqueda)
            is_player = self._is_player_page(soup, player_name)
            logger.info(f"🔍 ¿Es página de jugador? {is_player}")
            
            if is_player:
                # Extraer datos del jugador
                player_data = {
                    'name': self._extract_name(soup),
                    'current_club': self._extract_current_club(soup),
                    'market_value': self._extract_market_value(soup),
                    'age': self._extract_age(soup),
                    'position': self._extract_position(soup),
                    'height': self._extract_height(soup),
                    'weight': self._extract_weight(soup),
                    'foot': self._extract_foot(soup),
                    'nationality': self._extract_nationality(soup),
                    'etv_range': self._extract_etv_range(soup),
                }
                
                logger.info(f"✅ Datos extraídos de FootballTransfers: {player_data.get('name')}")
                logger.info(f"   Market value: {player_data.get('market_value')}")
                return player_data
            else:
                # Si no es página de jugador, intentar búsqueda
                logger.info(f"⚠️ No es página de jugador, intentando búsqueda alternativa...")
                return self._try_search_page(player_name)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en request a FootballTransfers: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en scraping FootballTransfers: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _create_player_slug(self, player_name):
        """Crear slug para URL del jugador"""
        # Convertir nombre a formato slug: "Lionel Messi" -> "lionel-messi"
        # Intentar primero con el nombre original (puede tener tildes)
        slug = player_name.lower()
        # Reemplazar espacios con guiones
        slug = slug.replace(' ', '-')
        # Remover caracteres especiales pero mantener caracteres con tildes
        # Permitir caracteres unicode comunes (á, é, í, ó, ú, ñ)
        slug = re.sub(r'[^a-z0-9\-áéíóúñ]', '', slug)
        logger.debug(f"   🔍 Slug generado: {slug}")
        return slug
    
    def _is_player_page(self, soup, player_name):
        """Verificar si es una página de jugador"""
        # Buscar indicadores de página de jugador
        # 1. Verificar título
        title = soup.find('title')
        if title:
            title_text = title.get_text().lower()
            # No requiere que el nombre esté en el título (puede variar)
            if 'player' in title_text or 'footballtransfers' in title_text:
                logger.debug(f"   ✅ Título parece ser de jugador: {title_text[:100]}")
        
        # 2. Buscar sección de perfil (más confiable)
        # BeautifulSoup: usar string simple que funciona correctamente
        profile_section = soup.find('article', class_='playerProfile-panel')
        if profile_section:
            logger.debug("   ✅ Encontrado playerProfile-panel")
            return True
        
        # 3. Buscar valor ETV
        etv_element = soup.find('div', class_='player-value__holder')
        if etv_element:
            logger.debug("   ✅ Encontrado player-value__holder")
            return True
        
        # 4. Buscar h1 con el nombre del jugador (menos específico pero útil)
        h1 = soup.find('h1')
        if h1:
            h1_text = h1.get_text().strip().lower()
            player_name_lower = player_name.lower()
            # Verificar si el nombre del jugador está en el h1
            if any(word in h1_text for word in player_name_lower.split() if len(word) > 3):
                logger.debug(f"   ✅ H1 contiene nombre del jugador: {h1_text[:100]}")
                # Verificar que no sea página de búsqueda o lista
                if 'search' not in h1_text and 'results' not in h1_text:
                    return True
        
        logger.debug("   ❌ No se encontraron indicadores de página de jugador")
        return False
    
    def _try_search_page(self, player_name):
        """Intentar búsqueda en la página de búsqueda con variaciones de nombre"""
        try:
            import unicodedata
            
            # FootballTransfers puede usar diferentes formatos de URL
            # Intentar variaciones del slug del nombre
            name_variations = []
            
            # 1. Con el nombre original (con tildes si tiene)
            name_variations.append(player_name.lower().replace(' ', '-'))
            
            # 2. Sin tildes (normalizado)
            normalized = unicodedata.normalize('NFD', player_name)
            no_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
            name_variations.append(no_accents.lower().replace(' ', '-'))
            
            # 3. Otras variaciones sin tildes
            name_variations.append(player_name.lower().replace(' ', '_'))
            name_variations.append('-'.join(player_name.lower().split()))
            
            # 4. Intentar diferentes combinaciones de nombres y apellidos
            name_parts = player_name.lower().split()
            if len(name_parts) >= 2:
                # Primera y última palabra (nombre + apellido)
                # Con tildes original
                name_variations.append(f"{name_parts[0]}-{name_parts[-1]}")
                # Sin tildes
                first_normalized = unicodedata.normalize('NFD', name_parts[0])
                first_no_accents = ''.join(c for c in first_normalized if unicodedata.category(c) != 'Mn')
                last_normalized = unicodedata.normalize('NFD', name_parts[-1])
                last_no_accents = ''.join(c for c in last_normalized if unicodedata.category(c) != 'Mn')
                name_variations.append(f"{first_no_accents}-{last_no_accents}")
                
            # 5. Si hay 3 o más palabras, intentar con todas las palabras
            # Esto cubre casos como "Germán Alejandro Pezzella" -> "german-alejandro-pezzella"
            if len(name_parts) >= 3:
                # Todas las palabras con tildes
                all_with_accents = '-'.join(name_parts)
                name_variations.append(all_with_accents)
                # Todas las palabras sin tildes
                all_no_accents = '-'.join([''.join(c for c in unicodedata.normalize('NFD', part) if unicodedata.category(c) != 'Mn') for part in name_parts])
                name_variations.append(all_no_accents)
            
            # Eliminar duplicados
            name_variations = list(dict.fromkeys(name_variations))
            
            logger.info(f"🔍 Probando {len(name_variations)} variaciones del nombre...")
            
            for variation in name_variations:
                try:
                    # Limpiar caracteres especiales pero mantener guiones y caracteres con tildes
                    # Solo remover caracteres realmente problemáticos
                    variation = re.sub(r'[^a-z0-9\-áéíóúñü]', '', variation)
                    search_url = f"https://www.footballtransfers.com/en/players/{variation}"
                    
                    logger.info(f"🔍 Intentando búsqueda con variación: {search_url}")
                    
                    time.sleep(random.uniform(0.5, 1))
                    
                    response = self.session.get(search_url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Verificar que es una página de jugador
                        if self._is_player_page(soup, player_name):
                            logger.info(f"✅ Encontrado con variación: {variation}")
                            return self._scrape_player_from_url(search_url)
                        else:
                            # Debug: ver qué tipo de página es
                            title = soup.find('title')
                            if title:
                                logger.debug(f"   ⚠️ Página encontrada pero no es de jugador: {title.get_text()[:100]}")
                    
                    # Si es 404, continuar con la siguiente variación
                    if response.status_code == 404:
                        logger.debug(f"   ⚠️ 404 con variación: {variation}")
                        continue
                    
                    # Si es 403, parar
                    if response.status_code == 403:
                        logger.warning(f"⚠️ 403 bloqueado")
                        return None
                        
                except Exception as e:
                    logger.debug(f"⚠️ Error con variación {variation}: {e}")
                    continue
            
            logger.warning(f"⚠️ No se encontró jugador con ninguna variación para {player_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return None
    
    def _scrape_player_from_url(self, player_url):
        """Scraping de datos del jugador desde URL específica"""
        try:
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(player_url, timeout=15)
            
            if response.status_code == 403:
                logger.warning(f"⚠️ 403 al acceder a perfil")
                return None
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer datos del jugador
            player_data = {
                'name': self._extract_name(soup),
                'current_club': self._extract_current_club(soup),
                'market_value': self._extract_market_value(soup),
                'age': self._extract_age(soup),
                'position': self._extract_position(soup),
                'height': self._extract_height(soup),
                'weight': self._extract_weight(soup),
                'foot': self._extract_foot(soup),
                'nationality': self._extract_nationality(soup),
                'etv_range': self._extract_etv_range(soup),
            }
            
            return player_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping desde URL: {e}")
            return None
    
    def _extract_name(self, soup):
        """Extraer nombre del jugador"""
        try:
            # Buscar en h1 principal
            h1 = soup.find('h1')
            if h1:
                name = h1.get_text(strip=True)
                if name and len(name) > 2:
                    return name
            
            # Buscar en título
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                # Formato típico: "Lionel Messi - FootballTransfers.com"
                if ' - ' in title_text:
                    name = title_text.split(' - ')[0].strip()
                    if name:
                        return name
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo nombre: {e}")
            return None
    
    def _extract_current_club(self, soup):
        """Extraer club actual desde FootballTransfers"""
        try:
            # Buscar en el perfil con estructura: <div class="col"><strong>Team</strong><span>Inter Miami</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                # Buscar todas las columnas
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    # Buscar el label "Team"
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if label_text.lower() == 'team':
                            # Buscar el valor
                            span = col.find('span', class_='txt')
                            if span:
                                # Puede tener un link dentro
                                link = span.find('a')
                                if link:
                                    club_name = link.get_text(strip=True)
                                else:
                                    club_name = span.get_text(strip=True)
                                
                                if club_name:
                                    logger.info(f"🏟️ Club encontrado: {club_name}")
                                    return club_name
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo club: {e}")
            return None
    
    def _extract_market_value(self, soup):
        """Extraer valor de mercado (ETV) desde FootballTransfers"""
        try:
            # Buscar el div con clase player-value__holder
            value_holder = soup.find('div', class_='player-value__holder')
            if value_holder:
                # Buscar el valor principal - puede estar en varios lugares
                # Intentar buscar números con € en el texto
                value_text = value_holder.get_text()
                
                # Buscar patrón: €7.3M o €7.3 M
                etv_patterns = [
                    r'€\s*([\d.,]+)\s*M',
                    r'€\s*([\d.,]+)M',
                    r'([\d.,]+)\s*M\s*€',
                    r'([\d.,]+)M\s*€',
                ]
                
                for pattern in etv_patterns:
                    match = re.search(pattern, value_text, re.IGNORECASE)
                    if match:
                        value_str = match.group(1).replace(',', '.')
                        try:
                            value_millions = float(value_str)
                            value_euros = int(value_millions * 1_000_000)
                            logger.info(f"💰 Market value encontrado: €{value_euros:,}")
                            return value_euros
                        except ValueError:
                            continue
            
            # Buscar en todo el HTML por ETV
            all_text = soup.get_text()
            etv_match = re.search(r'€\s*([\d.,]+)\s*M', all_text, re.IGNORECASE)
            if etv_match:
                value_str = etv_match.group(1).replace(',', '.')
                try:
                    value_millions = float(value_str)
                    value_euros = int(value_millions * 1_000_000)
                    return value_euros
                except ValueError:
                    pass
            
            # Buscar en el rango ETV si no encontramos valor exacto
            etv_range = self._extract_etv_range(soup)
            if etv_range:
                # Tomar el promedio del rango
                range_match = re.search(r'€\s*([\d.,]+)\s*M\s*–\s*€\s*([\d.,]+)\s*M', etv_range)
                if range_match:
                    min_val = float(range_match.group(1).replace(',', '.'))
                    max_val = float(range_match.group(2).replace(',', '.'))
                    avg_val = (min_val + max_val) / 2
                    return int(avg_val * 1_000_000)
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo market value: {e}")
            return None
    
    def _extract_age(self, soup):
        """Extraer edad desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>Age</strong><span>38 years old (24 Jun 1987)</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if label_text.lower() == 'age':
                            span = col.find('span', class_='txt')
                            if span:
                                age_text = span.get_text(strip=True)
                                # Extraer número de edad: "38 years old"
                                age_match = re.search(r'(\d+)\s*years?\s*old', age_text, re.IGNORECASE)
                                if age_match:
                                    age = int(age_match.group(1))
                                    if 16 <= age <= 50:
                                        logger.info(f"👤 Edad encontrada: {age} años")
                                        return age
                                
                                # Si no, intentar extraer de fecha de nacimiento
                                birth_match = re.search(r'\((\d{1,2})\s+(\w+)\s+(\d{4})\)', age_text)
                                if birth_match:
                                    # Calcular edad desde fecha de nacimiento
                                    from datetime import datetime
                                    try:
                                        birth_year = int(birth_match.group(3))
                                        current_year = datetime.now().year
                                        age = current_year - birth_year
                                        if 16 <= age <= 50:
                                            return age
                                    except:
                                        pass
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo edad: {e}")
            return None
    
    def _extract_position(self, soup):
        """Extraer posición desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>Best Playing Role</strong><span>Wide Playmaker</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if 'role' in label_text.lower() or 'position' in label_text.lower():
                            span = col.find('span', class_='txt')
                            if span:
                                position = span.get_text(strip=True)
                                if position:
                                    # Normalizar posición
                                    normalized = self._normalize_position(position)
                                    logger.info(f"⚽ Posición encontrada: {position} -> {normalized}")
                                    return normalized
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo posición: {e}")
            return None
    
    def _normalize_position(self, position):
        """Normalizar posición a formato estándar"""
        position_lower = position.lower()
        
        # Mapeo de posiciones de FootballTransfers a formato estándar
        position_map = {
            'wide playmaker': 'Winger',
            'winger': 'Winger',
            'forward': 'Forward',
            'striker': 'Forward',
            'attacking midfielder': 'Attacking Midfielder',
            'central midfielder': 'Midfielder',
            'defensive midfielder': 'Defensive Midfielder',
            'midfielder': 'Midfielder',
            'centre back': 'Defender',
            'left back': 'Defender',
            'right back': 'Defender',
            'defender': 'Defender',
            'goalkeeper': 'Goalkeeper',
            'inside forward': 'Forward',
        }
        
        for key, value in position_map.items():
            if key in position_lower:
                return value
        
        return position
    
    def _extract_height(self, soup):
        """Extraer altura desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>Height</strong><span>170cm</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if label_text.lower() == 'height':
                            span = col.find('span', class_='txt')
                            if span:
                                height_text = span.get_text(strip=True)
                                # Extraer cm: "170cm" -> "170 cm"
                                height_match = re.search(r'(\d+)', height_text)
                                if height_match:
                                    height_cm = int(height_match.group(1))
                                    if 150 <= height_cm <= 220:
                                        logger.info(f"📏 Altura encontrada: {height_cm} cm")
                                        return f"{height_cm} cm"
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo altura: {e}")
            return None
    
    def _extract_weight(self, soup):
        """Extraer peso desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>Weight</strong><span>72 kg</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if label_text.lower() == 'weight':
                            span = col.find('span', class_='txt')
                            if span:
                                weight_text = span.get_text(strip=True)
                                # Extraer kg: "72 kg"
                                weight_match = re.search(r'(\d+)', weight_text)
                                if weight_match:
                                    weight_kg = int(weight_match.group(1))
                                    if 50 <= weight_kg <= 120:
                                        logger.info(f"⚖️ Peso encontrado: {weight_kg} kg")
                                        return f"{weight_kg} kg"
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo peso: {e}")
            return None
    
    def _extract_foot(self, soup):
        """Extraer pie predominante desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>Preferred foot</strong><span>Left</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if 'foot' in label_text.lower():
                            span = col.find('span', class_='txt')
                            if span:
                                foot_text = span.get_text(strip=True)
                                # Normalizar: "Left" -> "Left", "Right" -> "Right"
                                if foot_text.lower() in ['left', 'right', 'both']:
                                    foot_capitalized = foot_text.capitalize()
                                    logger.info(f"🦶 Pie encontrado: {foot_capitalized}")
                                    return foot_capitalized
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo pie: {e}")
            return None
    
    def _extract_nationality(self, soup):
        """Extraer nacionalidad desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>Nationality</strong><span><i class="flag">...ARG</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if label_text.lower() == 'nationality':
                            span = col.find('span', class_='txt')
                            if span:
                                # Puede tener una imagen de bandera y texto
                                # Buscar el texto después de la imagen
                                nationality_text = span.get_text(strip=True)
                                
                                # Si tiene código de país (ARG, etc.), extraer el nombre
                                # Buscar en el alt de la imagen de bandera
                                flag_img = span.find('img', class_='flag')
                                if flag_img:
                                    alt = flag_img.get('alt', '')
                                    if alt and alt.lower() not in ['flag', '']:
                                        logger.info(f"🌍 Nacionalidad encontrada (flag alt): {alt}")
                                        return alt
                                
                                # Si tiene código como "ARG", buscar el nombre completo
                                if len(nationality_text) <= 4:
                                    # Es probablemente un código de país
                                    # Buscar el nombre completo en el texto del span
                                    full_text = span.get_text()
                                    # Remover el código y tomar el nombre si existe
                                    full_text_clean = re.sub(r'\b[A-Z]{2,3}\b', '', full_text).strip()
                                    if full_text_clean:
                                        logger.info(f"🌍 Nacionalidad encontrada: {full_text_clean}")
                                        return full_text_clean
                                
                                # Si tiene texto más largo, usar ese
                                if len(nationality_text) > 4:
                                    logger.info(f"🌍 Nacionalidad encontrada: {nationality_text}")
                                    return nationality_text
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo nacionalidad: {e}")
            return None
    
    def _extract_etv_range(self, soup):
        """Extraer rango ETV desde FootballTransfers"""
        try:
            # Buscar en el perfil: <div class="col"><strong>ETV Range</strong><span>€6.2M – €8.3M</span></div>
            profile_section = soup.find('article', class_='playerProfile-panel')
            if profile_section:
                cols = profile_section.find_all('div', class_='col')
                for col in cols:
                    strong = col.find('strong', class_='ttl')
                    if strong:
                        label_text = strong.get_text(strip=True)
                        if 'etv' in label_text.lower() and 'range' in label_text.lower():
                            span = col.find('span', class_='txt')
                            if span:
                                etv_range = span.get_text(strip=True)
                                if etv_range:
                                    logger.info(f"💰 Rango ETV encontrado: {etv_range}")
                                    return etv_range
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo rango ETV: {e}")
            return None

# Función de conveniencia
def get_player_data(player_name):
    """Función principal para obtener datos de jugador"""
    scraper = FootballTransfersScraper()
    return scraper.search_player(player_name)

if __name__ == "__main__":
    # Test del scraper
    test_players = ["Lionel Messi", "Cristiano Ronaldo"]
    
    for player in test_players:
        print(f"\n=== Scraping {player} ===")
        data = get_player_data(player)
        if data:
            print(f"Nombre: {data.get('name')}")
            print(f"Club: {data.get('current_club')}")
            market_value = data.get('market_value', 0)
            if market_value:
                print(f"Valor: €{market_value:,}")
            else:
                print("Valor: No disponible")
            print(f"Edad: {data.get('age')}")
            print(f"Posición: {data.get('position')}")
        else:
            print("No se encontraron datos")
        
        time.sleep(2)  # Delay entre requests

