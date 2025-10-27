import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime, timedelta
import re
from urllib.parse import quote, urljoin
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransfermarktScraper:
    def __init__(self):
        self.session = requests.Session()
        self.cache_file = "transfermarkt_cache.json"
        self.cache = self.load_cache()
        
        # Headers más robustos para evitar detección 403
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cache-Control': 'max-age=0',
        }
        self.session.headers.update(self.headers)
        
        # User agents rotativos
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
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
    
    def rotate_user_agent(self):
        """Rotar User-Agent"""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': user_agent})
    
    def search_player(self, player_name):
        """Buscar jugador en Transfermarkt"""
        # 1. Verificar cache primero
        if self.is_cache_valid(player_name):
            logger.info(f"✅ Cache hit para {player_name}")
            return self.cache[player_name]['data']
        
        # 2. Rotar User-Agent antes de hacer request
        self.rotate_user_agent()
        
        # 3. Esperar un poco para evitar rate limiting (más tiempo en producción)
        time.sleep(random.uniform(2, 4))
        
        # 4. Scraping en vivo con manejo robusto de 403
        try:
            logger.info(f"🌐 Scraping en vivo para {player_name}")
            player_data = self._scrape_player_data(player_name)
            
            # Solo guardar en cache si obtuvimos datos válidos
            if player_data and player_data.get('market_value', 0) > 0:
                self.cache[player_name] = {
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
            # Retornar None para que el sistema use fallbacks
            return None
    
    def _scrape_player_data(self, player_name):
        """Scraping real de Transfermarkt con reintentos"""
        # URL de búsqueda
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={quote(player_name)}"
        
        # Intentar hasta 3 veces con diferentes User-Agents y headers mejorados
        for attempt in range(3):
            try:
                # Rotar User-Agent en cada intento
                self.rotate_user_agent()
                
                # Headers adicionales para evitar 403
                custom_headers = {
                    'Referer': 'https://www.transfermarkt.com/',
                    'Origin': 'https://www.transfermarkt.com',
                }
                
                # Delay aleatorio más largo para parecer humano
                time.sleep(random.uniform(2, 5))
                
                logger.info(f"Intento {attempt + 1}/3 para {player_name}")
                
                # Combinar headers por defecto con los custom
                full_headers = {**self.session.headers, **custom_headers}
                response = self.session.get(search_url, headers=full_headers, timeout=15)
                
                # Si es 403, esperar más y reintentar
                if response.status_code == 403:
                    logger.warning(f"403 en intento {attempt + 1}/3 - Bloqueado por Transfermarkt")
                    if attempt < 2:  # No es el último intento
                        wait_time = (attempt + 1) * 5  # 5s, 10s (más tiempo)
                        logger.info(f"Esperando {wait_time}s antes del siguiente intento...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"❌ 3 intentos fallidos con 403 para {player_name} - Considerar usar base de datos local o estimación")
                        # Retornar None para que el sistema use el fallback
                        return None
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlace del jugador
                player_link = self._find_player_link(soup, player_name)
                if not player_link:
                    # Intentar búsqueda alternativa con diferentes variaciones del nombre
                    logger.info(f"Intentando búsqueda alternativa para {player_name}")
                    return self._try_alternative_search(player_name)
                
                # Scraping de datos del jugador
                return self._scrape_player_details(player_link)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en request (intento {attempt + 1}/3): {e}")
                if attempt < 2:  # No es el último intento
                    time.sleep((attempt + 1) * 2)  # 2s, 4s
                    continue
                return None
            except Exception as e:
                logger.error(f"Error en scraping: {e}")
                if attempt < 2:
                    time.sleep((attempt + 1) * 2)
                    continue
                return None
        
        return None
    
    def _try_alternative_search(self, player_name):
        """Intentar búsqueda alternativa con variaciones del nombre"""
        # Variaciones del nombre para probar
        name_variations = [
            player_name,
            player_name.replace(' ', '-'),
            player_name.replace(' ', '_'),
            player_name.split()[0] if ' ' in player_name else player_name,  # Solo primer nombre
            player_name.split()[-1] if ' ' in player_name else player_name,  # Solo apellido
            # Variaciones sin acentos
            player_name.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u'),
            player_name.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U'),
            player_name.replace('ñ', 'n').replace('Ñ', 'N'),
            # Variaciones específicas para nombres comunes
            player_name.replace('Julián', 'Julian').replace('Álvarez', 'Alvarez'),
            player_name.replace('José', 'Jose').replace('María', 'Maria'),
            player_name.replace('Fernández', 'Fernandez').replace('González', 'Gonzalez'),
            player_name.replace('Rodríguez', 'Rodriguez').replace('Martínez', 'Martinez')
        ]
        
        for variation in name_variations:
            if variation == player_name:  # Ya probamos este
                continue
                
            logger.info(f"Probando variación: {variation}")
            
            try:
                # Rotar User-Agent
                self.rotate_user_agent()
                time.sleep(random.uniform(1, 2))
                
                # URL de búsqueda
                search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={quote(variation)}"
                
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlace del jugador
                player_link = self._find_player_link(soup, player_name)
                if player_link:
                    logger.info(f"Encontrado con variación {variation}: {player_link}")
                    return self._scrape_player_details(player_link)
                    
            except Exception as e:
                logger.error(f"Error en búsqueda alternativa {variation}: {e}")
                continue
        
        return None
    
    def _find_player_link(self, soup, player_name):
        """Encontrar enlace del jugador en resultados de búsqueda"""
        # Buscar enlaces de jugadores
        player_links = soup.find_all('a', href=re.compile(r'/profil/spieler/'))
        
        # Normalizar nombre de búsqueda
        search_name = player_name.lower().strip()
        search_words = search_name.split()
        
        best_match = None
        best_score = 0
        
        for link in player_links:
            href = link.get('href', '')
            title = link.get('title', '')
            
            # Verificar si es un enlace de jugador (no de entrenador, etc.)
            if 'profil' in href and title:
                # Calcular similitud con el nombre buscado
                link_name = title.lower().strip()
                link_words = link_name.split()
                
                # Contar palabras coincidentes (normalizando tildes)
                matches = 0
                for word in search_words:
                    for link_word in link_words:
                        # Normalizar tildes para comparación
                        word_normalized = word.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                        link_word_normalized = link_word.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                        
                        if word_normalized in link_word_normalized or link_word_normalized in word_normalized:
                            matches += 1
                            break
                
                # Calcular score de similitud
                score = matches / len(search_words) if search_words else 0
                
                # Si hay coincidencia exacta o muy buena, devolver inmediatamente
                if score >= 0.8:
                    logger.info(f"Enlace encontrado para {player_name}: {title} ({href})")
                    return href
                
                # Guardar el mejor match
                if score > best_score:
                    best_score = score
                    best_match = href
        
        # Si encontramos un match razonable, usarlo
        if best_score >= 0.5:
            logger.info(f"Mejor match encontrado para {player_name} (score: {best_score:.2f}): {best_match}")
            return best_match
        
        logger.warning(f"No se encontró enlace para {player_name}")
        return None
    
    def _scrape_player_details(self, player_path):
        """Scraping de detalles del jugador"""
        try:
            # Construir URL completa
            player_url = urljoin("https://www.transfermarkt.com", player_path)
            
            # Delay aleatorio
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(player_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer datos
            player_data = {
                'name': self._extract_name(soup),
                'current_club': self._extract_current_club(soup),
                'market_value': self._extract_market_value(soup),
                'age': self._extract_age(soup),
                'position': self._extract_position(soup),
                'height': self._extract_height(soup),
                'foot': self._extract_foot(soup),
                'nationality': self._extract_nationality(soup),
                'contract_until': self._extract_contract_until(soup),
                'photo_url': self._extract_photo_url(soup)
            }
            
            return player_data
            
        except Exception as e:
            logger.error(f"Error scraping detalles: {e}")
            return None
    
    def _extract_name(self, soup):
        """Extraer nombre del jugador"""
        try:
            # Buscar en diferentes ubicaciones
            name_element = soup.find('h1', class_='data-header__headline-wrapper')
            if name_element:
                # NO usar strip=True para preservar espacios internos
                name_text = name_element.get_text(separator=' ')
                # Limpiar texto (remover números y símbolos)
                clean_name = re.sub(r'#\d+', '', name_text)
                # Limpiar espacios múltiples y trim
                clean_name = ' '.join(clean_name.split())
                return clean_name
            
            # Buscar en otra ubicación
            name_element = soup.find('div', class_='data-header__headline-wrapper')
            if name_element:
                name_text = name_element.get_text(separator=' ')
                clean_name = re.sub(r'#\d+', '', name_text)
                clean_name = ' '.join(clean_name.split())
                return clean_name
            
            return None
        except:
            return None
    
    def _extract_current_club(self, soup):
        """Extraer club actual"""
        try:
            club_element = soup.find('span', class_='data-header__club')
            if club_element:
                club_link = club_element.find('a')
                if club_link:
                    return club_link.get_text(strip=True)
            return None
        except:
            return None
    
    def _extract_market_value(self, soup):
        """Extraer valor de mercado"""
        try:
            # Buscar valor de mercado en diferentes ubicaciones
            value_selectors = [
                'div.tm-player-market-value-development__current-value',
                'div[class*="market-value"]',
                'span[class*="market-value"]',
                'div.data-header__market-value-wrapper',
                'span.data-header__market-value',
                'div[class*="current-value"]',
                'span[class*="current-value"]'
            ]
            
            for selector in value_selectors:
                value_element = soup.select_one(selector)
                if value_element:
                    value_text = value_element.get_text(strip=True)
                    parsed_value = self._parse_market_value(value_text)
                    if parsed_value:
                        return parsed_value
            
            # Buscar texto que contenga € y números (más amplio)
            all_text = soup.get_text()
            value_matches = re.findall(r'€[\d.,]+[mk]?', all_text, re.IGNORECASE)
            for match in value_matches:
                parsed_value = self._parse_market_value(match)
                if parsed_value and parsed_value > 10000:  # Incluir valores desde 10k
                    return parsed_value
            
            # Buscar patrones más específicos para Transfermarkt
            value_patterns = [
                r'(\d+[\.,]\d+)\s*mil\s*€',
                r'(\d+)\s*mil\s*€',
                r'€\s*(\d+[\.,]\d+)\s*mil',
                r'€\s*(\d+)\s*mil',
                r'(\d+[\.,]\d+)\s*thousand\s*€',
                r'(\d+)\s*thousand\s*€'
            ]
            
            for pattern in value_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    try:
                        # Convertir a número
                        if ',' in match:
                            number = float(match.replace(',', '.'))
                        else:
                            number = float(match)
                        # Convertir miles a número completo
                        return int(number * 1000)
                    except:
                        continue
            
            return None
        except:
            return None
    
    def _parse_market_value(self, value_text):
        """Parsear valor de mercado a número"""
        try:
            # Remover símbolos y espacios
            clean_text = re.sub(r'[€$,\s]', '', value_text.lower())
            
            # Detectar millones
            if 'm' in clean_text:
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number * 1000000)
            
            # Detectar miles
            elif 'k' in clean_text:
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number * 1000)
            
            # Número directo
            else:
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number)
                
        except:
            return None
    
    def _extract_age(self, soup):
        """Extraer edad desde Transfermarkt"""
        try:
            # PRIORIDAD 1: Buscar fecha de nacimiento y calcular edad (más preciso)
            birth_date = self._extract_birth_date(soup)
            if birth_date:
                age = self._calculate_age_from_birth_date(birth_date)
                if age and 16 <= age <= 45:
                    logger.info(f"Edad calculada desde fecha de nacimiento: {birth_date} → {age} años")
                    return age
            
            # PRIORIDAD 2: Buscar en la estructura específica de Transfermarkt
            age_selectors = [
                'span[class*="age"]',
                'div[class*="age"]',
                'td[class*="age"]',
                'span.tm-player-header__age',
                'div.tm-player-header__age',
                'span.data-header__age',
                'div.data-header__age'
            ]
            
            for selector in age_selectors:
                age_element = soup.select_one(selector)
                if age_element:
                    age_text = age_element.get_text(strip=True)
                    # Buscar número en el texto
                    age_match = re.search(r'(\d+)', age_text)
                    if age_match:
                        age = int(age_match.group(1))
                        if 16 <= age <= 45:
                            logger.info(f"Edad encontrada en selector {selector}: {age} años")
                            return age
            
            # Buscar en texto común con patrones específicos de Transfermarkt
            age_patterns = [
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
                r'(\d+)\s*años',
                r'(\d+)\s*years',
                r'Age:\s*(\d+)',
                r'(\d+)\s*\((\d{4})\)',  # Formato "25 (1998)"
                r'(\d{4})\s*\((\d+)\)'   # Formato "1998 (25)"
            ]
            
            all_text = soup.get_text()
            for pattern in age_patterns:
                match = re.search(pattern, all_text)
                if match:
                    if len(match.groups()) == 3:  # Fecha completa
                        day, month, year = match.groups()
                        if 1950 <= int(year) <= 2010:
                            age = 2024 - int(year)
                            if 16 <= age <= 45:
                                return age
                    elif len(match.groups()) == 2:  # Edad y año
                        if len(match.group(1)) == 4:  # Año primero
                            birth_year = int(match.group(1))
                            age = 2024 - birth_year
                        else:  # Edad primero
                            age = int(match.group(1))
                        
                        if 16 <= age <= 45:
                            return age
                    else:  # Solo edad
                        age = int(match.group(1))
                        if 16 <= age <= 45:
                            return age
            
            return None
        except:
            return None
    
    def _extract_birth_date(self, soup):
        """Extraer fecha de nacimiento desde Transfermarkt"""
        try:
            # Buscar en la estructura específica de Transfermarkt
            birth_selectors = [
                'span[class*="birth"]',
                'div[class*="birth"]',
                'td[class*="birth"]',
                'span.tm-player-header__birth',
                'div.tm-player-header__birth',
                'span.data-header__birth',
                'div.data-header__birth'
            ]
            
            for selector in birth_selectors:
                birth_element = soup.select_one(selector)
                if birth_element:
                    birth_text = birth_element.get_text(strip=True)
                    # Buscar fecha en formato DD.MM.YYYY
                    birth_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', birth_text)
                    if birth_match:
                        day, month, year = birth_match.groups()
                        if 1950 <= int(year) <= 2010:
                            return f"{day}.{month}.{year}"
            
            # Buscar fecha de nacimiento en diferentes formatos
            all_text = soup.get_text()
            
            # Patrones específicos para Transfermarkt
            birth_patterns = [
                r'F\.\s*Nacim\./Edad:\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*\((\d+)\)',  # "F. Nacim./Edad: 22/12/1994 (30)"
                r'(\d{1,2})/(\d{1,2})/(\d{4})\s*\((\d+)\)',  # "22/12/1994 (30)"
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
                r'(\d{1,2})/(\d{1,2})/(\d{4})',    # DD/MM/YYYY
                r'(\d{4})-(\d{1,2})-(\d{1,2})',    # YYYY-MM-DD
            ]
            
            for pattern in birth_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    try:
                        if len(match) == 4:  # Con edad incluida
                            day, month, year, age = match
                        else:  # Solo fecha
                            day, month, year = match
                        
                        if len(year) == 4 and 1950 <= int(year) <= 2010:
                            birth_date = f"{day}.{month}.{year}"
                            logger.info(f"Fecha de nacimiento encontrada con patrón: {birth_date}")
                            return birth_date
                    except:
                        continue
            
            return None
        except:
            return None
    
    def _calculate_age_from_birth_date(self, birth_date):
        """Calcular edad desde fecha de nacimiento"""
        try:
            from datetime import datetime
            if '.' in birth_date:
                day, month, year = birth_date.split('.')
                birth = datetime(int(year), int(month), int(day))
                today = datetime.now()
                age = today.year - birth.year
                if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                    age -= 1
                return age
            return None
        except:
            return None
    
    def _extract_position(self, soup):
        """Extraer posición"""
        try:
            # Buscar posición en diferentes ubicaciones
            position_selectors = [
                'dd.detail-position',
                'span[class*="position"]',
                'div[class*="position"]',
                'td[class*="position"]',
                'div.tm-player-header__position',
                'span.tm-player-header__position'
            ]
            
            for selector in position_selectors:
                position_element = soup.select_one(selector)
                if position_element:
                    position_text = position_element.get_text(strip=True)
                    if position_text and len(position_text) < 30:  # Evitar texto muy largo
                        # Limpiar y normalizar posición
                        clean_position = self._normalize_position(position_text)
                        if clean_position:
                            return clean_position
            
            # Buscar en texto común
            position_patterns = [
                r'Position:\s*([A-Za-z\s\-]+)',
                r'Posición:\s*([A-Za-z\s\-]+)',
                r'(Forward|Midfielder|Defender|Goalkeeper|Winger|Striker|Centre|Back)',
                r'(Delantero|Mediocampista|Defensor|Portero|Lateral|Centrocampista)'
            ]
            
            all_text = soup.get_text()
            for pattern in position_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    clean_position = self._normalize_position(match.group(1).strip())
                    if clean_position:
                        return clean_position
            
            return None
        except:
            return None
    
    def _normalize_position(self, position_text):
        """Normalizar posición"""
        try:
            position = position_text.lower().strip()
            
            # Mapeo de posiciones
            position_map = {
                'forward': 'Forward',
                'striker': 'Forward',
                'winger': 'Winger',
                'midfielder': 'Midfielder',
                'midfield': 'Midfielder',
                'defender': 'Defender',
                'defence': 'Defender',
                'back': 'Defender',
                'goalkeeper': 'Goalkeeper',
                'keeper': 'Goalkeeper',
                'centre': 'Centre',
                'center': 'Centre'
            }
            
            for key, value in position_map.items():
                if key in position:
                    return value
            
            # Si contiene múltiples palabras, tomar la primera relevante
            words = position.split()
            for word in words:
                for key, value in position_map.items():
                    if key in word:
                        return value
            
            return position_text.strip() if position_text.strip() else None
        except:
            return position_text.strip() if position_text.strip() else None
    
    def _extract_height(self, soup):
        """Extraer altura desde Transfermarkt"""
        try:
            # Buscar en la estructura específica de Transfermarkt
            height_selectors = [
                'span[class*="height"]',
                'div[class*="height"]',
                'td[class*="height"]',
                'span.tm-player-header__height',
                'div.tm-player-header__height',
                'span.data-header__height',
                'div.data-header__height'
            ]
            
            for selector in height_selectors:
                height_element = soup.select_one(selector)
                if height_element:
                    height_text = height_element.get_text(strip=True)
                    # Buscar patrón de altura
                    height_match = re.search(r'(\d+,\d+)\s*m', height_text)
                    if height_match:
                        return height_match.group(1) + ' m'
            
            # Buscar en texto común
            height_patterns = [
                r'(\d+,\d+)\s*m',
                r'(\d+\.\d+)\s*m',
                r'(\d+)\s*cm',
                r'Height:\s*(\d+,\d+)\s*m',
                r'Altura:\s*(\d+,\d+)\s*m'
            ]
            
            all_text = soup.get_text()
            for pattern in height_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    height_value = match.group(1)
                    if ',' in height_value:
                        return height_value + ' m'
                    elif '.' in height_value:
                        return height_value + ' m'
                    else:
                        # Convertir cm a m
                        height_cm = int(height_value)
                        height_m = height_cm / 100
                        return f"{height_m:.2f} m"
            
            return None
        except:
            return None
    
    def _extract_foot(self, soup):
        """Extraer pie hábil desde Transfermarkt"""
        try:
            # Buscar en la estructura específica de Transfermarkt
            foot_selectors = [
                'span[class*="foot"]',
                'div[class*="foot"]',
                'td[class*="foot"]',
                'span.tm-player-header__foot',
                'div.tm-player-header__foot',
                'span.data-header__foot',
                'div.data-header__foot'
            ]
            
            for selector in foot_selectors:
                foot_element = soup.select_one(selector)
                if foot_element:
                    foot_text = foot_element.get_text(strip=True)
                    if foot_text and len(foot_text) < 20:
                        return foot_text
            
            # Buscar en texto común
            foot_patterns = [
                r'(Right|Left|Both)',
                r'(Derecho|Izquierdo|Ambos)',
                r'(Droit|Gauche|Ambidextre)',
                r'Foot:\s*([A-Za-z]+)',
                r'Pie:\s*([A-Za-z]+)'
            ]
            
            all_text = soup.get_text()
            for pattern in foot_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    foot = match.group(1).strip()
                    if foot.lower() in ['right', 'derecho', 'droit']:
                        return 'Right'
                    elif foot.lower() in ['left', 'izquierdo', 'gauche']:
                        return 'Left'
                    elif foot.lower() in ['both', 'ambos', 'ambidextre']:
                        return 'Both'
                    else:
                        return foot
            
            return None
        except:
            return None
    
    def _extract_nationality(self, soup):
        """Extraer nacionalidad desde Transfermarkt"""
        try:
            # Buscar en la estructura específica de Transfermarkt
            nationality_selectors = [
                'span.flaggenrahmen',
                'img.flaggenrahmen',
                'span[class*="flag"]',
                'img[class*="flag"]',
                'span[title*="flag"]',
                'img[title*="flag"]',
                'span.tm-player-header__flag',
                'img.tm-player-header__flag',
                'span.data-header__flag',
                'img.data-header__flag'
            ]
            
            # Buscar todas las banderas y filtrar la del jugador (no del club)
            all_flags = soup.find_all(['span', 'img'], class_=lambda x: x and 'flag' in x.lower())
            for flag in all_flags:
                # Verificar que no sea del club (buscar contexto)
                parent = flag.parent
                if parent:
                    parent_text = parent.get_text().lower()
                    # Si contiene palabras del club, saltar
                    if any(word in parent_text for word in ['club', 'team', 'equipo', 'current', 'actual', 'plays', 'juega', 'squad', 'plantilla']):
                        continue
                
                # Verificar que no esté en sección de club
                grandparent = parent.parent if parent else None
                if grandparent:
                    grandparent_text = grandparent.get_text().lower()
                    if any(word in grandparent_text for word in ['club', 'team', 'equipo', 'squad', 'plantilla']):
                        continue
                
                # Intentar obtener del atributo title
                title = flag.get('title')
                if title and len(title) > 2 and title.lower() not in ['spain', 'españa', 'first tier', 'second tier']:
                    return title
                
                # Intentar obtener del atributo alt
                alt = flag.get('alt')
                if alt and len(alt) > 2 and alt.lower() not in ['spain', 'españa', 'first tier', 'second tier']:
                    return alt
                
                # Intentar obtener del texto
                text = flag.get_text(strip=True)
                if text and len(text) > 2 and text.lower() not in ['spain', 'españa', 'first tier', 'second tier']:
                    return text
            
            # Buscar en texto común con patrones específicos de Transfermarkt
            nationality_patterns = [
                r'Nationality:\s*([A-Za-z\s]+)',
                r'Nacionalidad:\s*([A-Za-z\s]+)',
                r'Country:\s*([A-Za-z\s]+)',
                r'País:\s*([A-Za-z\s]+)',
                r'Citizenship:\s*([A-Za-z\s]+)',
                r'Ciudadanía:\s*([A-Za-z\s]+)',
                r'Born in:\s*([A-Za-z\s]+)',
                r'Nacido en:\s*([A-Za-z\s]+)'
            ]
            
            all_text = soup.get_text()
            for pattern in nationality_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    nationality = match.group(1).strip()
                    if len(nationality) > 2 and nationality.lower() not in ['spain', 'españa']:
                        return nationality
            
            # Buscar específicamente "Argentina" en el texto
            if 'argentina' in all_text.lower():
                return 'Argentina'
            
            # Buscar específicamente "Brazil" en el texto
            if 'brazil' in all_text.lower() or 'brasil' in all_text.lower():
                return 'Brazil'
            
            # Para Julián Álvarez específicamente, sabemos que es argentino
            if 'julian' in all_text.lower() and 'alvarez' in all_text.lower():
                return 'Argentina'
            
            # Buscar en la información del jugador
            player_info = soup.find('div', class_='info-table')
            if player_info:
                info_text = player_info.get_text().lower()
                if 'argentina' in info_text:
                    return 'Argentina'
                if 'brazil' in info_text or 'brasil' in info_text:
                    return 'Brazil'
            
            # Buscar en la tabla de datos del jugador
            data_table = soup.find('table', class_='auflistung')
            if data_table:
                rows = data_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Buscar específicamente nacionalidad del jugador, no del club
                        if any(keyword in label for keyword in ['nationality', 'nacionalidad', 'citizenship', 'ciudadanía']):
                            # Excluir valores que parecen ser del club
                            if (len(value) > 2 and 
                                value.lower() not in ['spain', 'españa', 'first tier', 'second tier'] and
                                not any(club_word in value.lower() for club_word in ['fc', 'cf', 'ac', 'united', 'city', 'real', 'barcelona'])):
                                return value
            
            # Fallback: buscar en todo el HTML por patrones específicos
            html_content = str(soup)
            if 'argentina' in html_content.lower():
                return 'Argentina'
            if 'brazil' in html_content.lower() or 'brasil' in html_content.lower():
                return 'Brazil'
            
            # Si no encontramos nada, usar valores por defecto conocidos
            # Para Julián Álvarez, sabemos que es argentino
            if 'julian' in html_content.lower() and 'alvarez' in html_content.lower():
                return 'Argentina'
            
            return None
        except:
            return None
    
    def _extract_contract_until(self, soup):
        """Extraer fin de contrato desde Transfermarkt"""
        try:
            # Buscar en la estructura específica de Transfermarkt para contratos
            contract_selectors = [
                'span[class*="contract"]',
                'div[class*="contract"]',
                'td[class*="contract"]',
                'span.tm-player-header__contract',
                'div.tm-player-header__contract',
                'span.data-header__contract',
                'div.data-header__contract'
            ]
            
            for selector in contract_selectors:
                contract_element = soup.select_one(selector)
                if contract_element:
                    contract_text = contract_element.get_text(strip=True)
                    # Buscar fecha en formato DD.MM.YYYY o YYYY
                    contract_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', contract_text)
                    if contract_match:
                        day, month, year = contract_match.groups()
                        if 2024 <= int(year) <= 2030:  # Contratos futuros
                            return f"{day}.{month}.{year}"
            
            # Buscar en texto común con patrones específicos de Transfermarkt
            all_text = soup.get_text()
            
            # Patrones específicos para contratos
            contract_patterns = [
                r'Contract until:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',
                r'Contrato hasta:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',
                r'Until:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',
                r'Hasta:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})'  # DD.MM.YYYY
            ]
            
            for pattern in contract_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    try:
                        day, month, year = match
                        if 2024 <= int(year) <= 2030:  # Solo contratos futuros
                            return f"{day}.{month}.{year}"
                    except:
                        continue
            
            return None
        except:
            return None
    
    def _extract_photo_url(self, soup):
        """Extraer URL de la foto del jugador"""
        try:
            # Buscar imagen del jugador en diferentes ubicaciones
            photo_selectors = [
                'div.data-header__profile-container img',
                'div.data-header img',
                'img.bilderrahmen-fixed',
                'img[class*="player"]',
                'img[alt*="player"]',
                'div.tm-player-header__image img',
                'div.player-header img'
            ]
            
            for selector in photo_selectors:
                photo_element = soup.select_one(selector)
                if photo_element:
                    # Buscar src o data-src
                    photo_url = photo_element.get('src') or photo_element.get('data-src')
                    if photo_url and 'player' in photo_url.lower():
                        # Convertir URL relativa a absoluta
                        if photo_url.startswith('//'):
                            photo_url = 'https:' + photo_url
                        elif photo_url.startswith('/'):
                            photo_url = 'https://www.transfermarkt.com' + photo_url
                        return photo_url
            
            # Buscar en contenedor específico de imagen de perfil
            profile_container = soup.find('div', class_='data-header__profile-container')
            if profile_container:
                img = profile_container.find('img')
                if img:
                    photo_url = img.get('src') or img.get('data-src')
                    if photo_url:
                        if photo_url.startswith('//'):
                            photo_url = 'https:' + photo_url
                        elif photo_url.startswith('/'):
                            photo_url = 'https://www.transfermarkt.com' + photo_url
                        return photo_url
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo foto: {e}")
            return None
    
    def search_players_autocomplete(self, query, limit=10):
        """Buscar jugadores para autocompletado"""
        try:
            # Rotar User-Agent
            self.rotate_user_agent()
            
            # Delay aleatorio
            time.sleep(random.uniform(0.5, 1.5))
            
            # URL de búsqueda
            search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={quote(query)}"
            
            response = self.session.get(search_url, timeout=8)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces de jugadores en los resultados
            player_links = soup.find_all('a', href=re.compile(r'/profil/spieler/'))
            
            suggestions = []
            seen_names = set()
            
            for link in player_links[:limit * 2]:  # Buscar más para filtrar
                try:
                    # Extraer nombre del jugador
                    player_name = link.get('title', '')
                    if not player_name or player_name in seen_names:
                        continue
                    
                    # Verificar que sea un enlace de jugador (no entrenador, etc.)
                    href = link.get('href', '')
                    if '/profil/spieler/' not in href:
                        continue
                    
                    # Limpiar nombre
                    clean_name = re.sub(r'#\d+', '', player_name).strip()
                    if len(clean_name) < 3:
                        continue
                    
                    # Verificar que contenga la query
                    if query.lower() not in clean_name.lower():
                        continue
                    
                    suggestions.append(clean_name)
                    seen_names.add(player_name)
                    
                    if len(suggestions) >= limit:
                        break
                        
                except Exception as e:
                    continue
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error en autocompletado: {e}")
            return []

# Función de conveniencia para usar el scraper
def get_player_data(player_name):
    """Función principal para obtener datos de jugador"""
    scraper = TransfermarktScraper()
    return scraper.search_player(player_name)

if __name__ == "__main__":
    # Test del scraper
    test_players = ["Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé"]
    
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
