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

# Intentar importar Selenium (opcional)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("⚠️ Selenium no está instalado. BeSoccer scraper necesita Selenium.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BeSoccerScraper:
    def __init__(self):
        print("🔧 BeSoccerScraper.__init__ iniciando...")
        print(f"🔍 Selenium disponible: {SELENIUM_AVAILABLE}")
        
        try:
            self.session = requests.Session()
            self.cache_file = "besoccer_cache.json"
            self.cache = self.load_cache()
            
            # Headers para BeSoccer
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
            self.session.headers.update(self.headers)
            print("✅ BeSoccerScraper.__init__ completado sin errores")
        except Exception as e:
            print(f"❌ Error en BeSoccerScraper.__init__: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            raise
    
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
        """Buscar jugador en BeSoccer usando Selenium"""
        # Verificar si Selenium está disponible
        if not SELENIUM_AVAILABLE:
            logger.warning("⚠️ Selenium no está disponible - instalarlo con: pip install selenium")
            return None
        
        # 1. Verificar cache
        if self.is_cache_valid(player_name):
            logger.info(f"✅ Cache hit para {player_name}")
            return self.cache[player_name]['data']
        
        # 2. Scraping con Selenium
        try:
            print(f"🌐 BeSoccer: Scraping en vivo para {player_name}")
            logger.info(f"🌐 Scraping en vivo en BeSoccer para {player_name}")
            player_data = self._scrape_with_selenium(player_name)
            
            # Solo guardar si obtuvimos datos válidos
            if player_data and player_data.get('name'):
                # Verificar si tiene market_value válido (no None)
                market_value = player_data.get('market_value')
                if market_value is not None and market_value > 0:
                    self.cache[player_name] = {
                        'data': player_data,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.save_cache()
                    print(f"✅ BeSoccer: Jugador encontrado - {player_data.get('name')} (€{market_value:,})")
                    logger.info(f"✅ Datos guardados en cache para {player_name}")
                    return player_data
                else:
                    print(f"⚠️ BeSoccer: No market_value para {player_name} (valor: {market_value})")
                    logger.warning(f"⚠️ BeSoccer no tiene market_value para {player_name} (valor: {market_value})")
                    return None
            else:
                print(f"⚠️ BeSoccer: No obtuvo datos válidos para {player_name}")
                logger.warning(f"⚠️ BeSoccer no obtuvo datos válidos para {player_name}")
                return None
            
        except Exception as e:
            print(f"❌ BeSoccer ERROR para {player_name}: {e}")
            logger.error(f"❌ Error scraping BeSoccer {player_name}: {e}")
            return None
    
    def _scrape_with_selenium(self, player_name):
        """Scraping de BeSoccer usando Selenium para interactuar con JavaScript"""
        driver = None
        try:
            # Configurar driver de Chrome
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Ejecutar sin ventana
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            # Configuración especial para Render
            if os.environ.get('RENDER'):
                logger.info("🌐 Detectado Render, configurando Chrome para producción...")
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-software-rasterizer')
                options.add_argument('--single-process')
                options.add_argument('--disable-background-networking')
                options.add_argument('--disable-background-timer-throttling')
                options.add_argument('--disable-renderer-backgrounding')
                options.add_argument('--disable-backgrounding-occluded-windows')
                options.add_argument('--disable-ipc-flooding-protection')
                
                # Configurar ChromeDriver para Render - usar ubicaciones por defecto
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
                
                # Intentar múltiples ubicaciones posibles
                possible_driver_paths = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    'chromedriver'
                ]
                
                chromedriver_path = None
                for path in possible_driver_paths:
                    if os.path.exists(path) or not os.path.exists(path):  # Intentar incluso si no existe (selenium lo manejará)
                        chromedriver_path = path
                        break
                
                chrome_binary = '/usr/bin/chromium-browser'
                options.binary_location = chrome_binary
                
                try:
                    if chromedriver_path:
                        driver = webdriver.Chrome(options=options, service=Service(chromedriver_path))
                        logger.info(f"✅ ChromeDriver configurado para Render: {chromedriver_path}")
                    else:
                        driver = webdriver.Chrome(options=options)
                        logger.info("✅ ChromeDriver configurado para Render (ruta por defecto)")
                except Exception as e:
                    logger.error(f"❌ Error configurando ChromeDriver: {e}")
                    logger.info("⚠️ Intentando sin service explícito...")
                    driver = webdriver.Chrome(options=options)
                    logger.info("✅ ChromeDriver configurado para Render (sin service)")
            else:
                driver = webdriver.Chrome(options=options)
                logger.info("✅ ChromeDriver configurado para desarrollo local")
            
            logger.info(f"🔍 Buscando en BeSoccer con Selenium: {player_name}")
            
            # TIMEOUT TOTAL: 30 segundos para todo el proceso
            start_time = time.time()
            max_duration = 30
            
            # 1. Ir a la página principal
            driver.get("https://www.besoccer.com")
            logger.info("📄 Página cargada")
            
            # Verificar timeout
            if time.time() - start_time > max_duration:
                logger.error("⏱️ Timeout excedido antes de buscar")
                return None
            
            # Log: Verificar que la página cargó
            logger.info(f"📄 Título de la página: {driver.title}")
            
            # 2. Cerrar popups/cookies si aparecen (rápido, max 2s)
            try:
                cookie_button = driver.find_elements(By.CSS_SELECTOR, "button[data-action='accept']")
                if cookie_button:
                    cookie_button[0].click()
                    time.sleep(0.5)
            except:
                pass
            
            # Verificar timeout
            if time.time() - start_time > max_duration:
                logger.error("⏱️ Timeout excedido después de cerrar popup")
                return None
            
            # 3. Encontrar el input de búsqueda y escribir usando JavaScript directamente
            logger.info("🔍 Buscando input de búsqueda...")
            
            # Intentar con JavaScript puro primero
            driver.execute_script("""
                const input = document.getElementById('search_input');
                if (input) {
                    input.value = '""" + player_name + """';
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('keyup', { bubbles: true }));
                }
            """)
            
            logger.info(f"⌨️ Texto escrito")
            time.sleep(2)  # Menos tiempo de espera
            
            # Verificar timeout
            if time.time() - start_time > max_duration:
                logger.error("⏱️ Timeout excedido después de escribir")
                return None
            
            logger.info(f"⏳ Esperando autocomplete...")
            
            # 4. Esperar a que aparezca el autocomplete (reducido a 5s)
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "autocomplete_values"))
                )
                logger.info("✅ Autocomplete apareció")
            except TimeoutException:
                logger.warning("⚠️ Autocomplete no apareció - timeout de 5s excedido")
                logger.warning("⚠️ Retornando None - no se puede completar búsqueda sin autocomplete")
                return None  # Retornar temprano para evitar más esperas
                
                # Reintentar con click en el input (SOLO si eliminamos el return de arriba)
                try:
                    search_input = driver.find_element(By.ID, "search_input")
                    search_input.click()
                    time.sleep(2)
                except:
                    pass
            
            # Buscar el segundo <li> en el autocomplete que sea jugador
            autocomplete_values = driver.find_elements(By.CSS_SELECTOR, "#autocomplete_values li")
            logger.info(f"📋 Encontrados {len(autocomplete_values)} elementos en autocomplete")
            
            # Log de todos los elementos del autocomplete para debug
            for i, li_element in enumerate(autocomplete_values):
                links = li_element.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    text_parts = link.find_elements(By.CSS_SELECTOR, ".text-box .main-text")
                    if text_parts:
                        main_text = text_parts[0].text
                        logger.info(f"   [{i}] Link: {href} - Text: {main_text}")
            
            player_link = None
            for li_element in autocomplete_values:
                # Buscar links dentro del li
                links = li_element.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    # Verificar si es un link de jugador (no de equipo o competición)
                    if href and "/player/" in href:
                        # Verificar que no sea "search"
                        text_parts = link.find_elements(By.CSS_SELECTOR, ".text-box .main-text")
                        if text_parts:
                            main_text = text_parts[0].text
                            logger.info(f"   Probando match: '{player_name.lower()}' in '{main_text.lower()}'")
                            # Intentar match con el nombre buscado (más flexible)
                            if (player_name.lower() in main_text.lower() or 
                                main_text.lower() in player_name.lower() or
                                any(word in main_text.lower() for word in player_name.lower().split() if len(word) > 3)):
                                player_link = href
                                logger.info(f"✅ Enlace de jugador encontrado: {href}")
                                break
                if player_link:
                    break
            
            if not player_link:
                logger.warning(f"⚠️ No se encontró jugador en el autocomplete para {player_name}")
                return None
            
            # 5. Ir a la página del jugador
            driver.get(player_link)
            logger.info(f"🌐 Navegando a página del jugador: {player_link}")
            time.sleep(2)  # Esperar a que cargue la página
            
            # 6. Extraer datos del HTML de la página
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            logger.info("📊 Extrayendo datos del jugador...")
            
            # Extraer datos del jugador
            player_data = {
                'name': self._extract_name(soup),
                'current_club': self._extract_current_club(soup),
                'market_value': self._extract_market_value(soup),
                'age': self._extract_age(soup),
                'position': self._extract_position(soup),
                'height': self._extract_height(soup),
                'foot': self._extract_foot(soup),
                'nationality': self._extract_nationality(soup),
            }
            
            # Normalizar formato para que coincida con Transfermarkt
            player_data = self._normalize_to_transfermarkt_format(player_data)
            
            # Log de lo que se extrajo
            logger.info(f"✅ Datos extraídos de BeSoccer:")
            logger.info(f"   Nombre: {player_data.get('name')}")
            logger.info(f"   Club: {player_data.get('current_club')}")
            market_value = player_data.get('market_value', 0)
            if market_value:
                logger.info(f"   Valor: €{market_value:,}")
            else:
                logger.info(f"   Valor: {market_value}")
            logger.info(f"   Edad: {player_data.get('age')}")
            logger.info(f"   Posición: {player_data.get('position')}")
            logger.info(f"   Altura: {player_data.get('height')}")
            logger.info(f"   Pie: {player_data.get('foot')}")
            logger.info(f"   Nacionalidad: {player_data.get('nationality')}")
            
            return player_data
            
        except TimeoutException:
            logger.error("❌ Timeout esperando elementos de BeSoccer")
            return None
        except Exception as e:
            logger.error(f"❌ Error en scraping con Selenium: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def _scrape_player_data(self, player_name):
        """Scraping real de BeSoccer - Usando búsqueda directa en la página principal"""
        try:
            # BeSoccer usa un sistema de búsqueda en la página principal
            # Intentar buscar directamente usando la página principal con query
            search_url = f"https://www.besoccer.com/search?q={quote(player_name)}"
            
            logger.info(f"🔍 Buscando en BeSoccer: {player_name}")
            logger.info(f"📡 URL: {search_url}")
            
            time.sleep(random.uniform(2, 3))
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 403:
                logger.warning(f"⚠️ 403 en BeSoccer para {player_name}")
                return None
            
            if response.status_code == 404:
                logger.warning(f"⚠️ 404 en BeSoccer - intentando URL alternativa")
                # Intentar sin parámetros
                search_url = f"https://www.besoccer.com/"
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                # Aquí necesitaríamos simular el input del buscador
                logger.warning("⚠️ Necesitamos acceder al input de búsqueda dinámicamente")
                return None
            
            response.raise_for_status()
            
            # Probar si es JSON primero (API de autocomplete)
            try:
                data = response.json()
                # Si es JSON (autocomplete API)
                player_id = self._extract_player_id_from_json(data, player_name)
                if player_id:
                    logger.info(f"✅ ID encontrado en JSON: {player_id}")
                    return self._scrape_player_details_by_id(player_id)
            except:
                # No es JSON, continuar con HTML
                pass
            
            # Si no es JSON, parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar en el autocomplete - Estructura de BeSoccer:
            # <a href="https://www.besoccer.com/player/k-mbappe-lottin-234474" class="pl5">
            player_links = soup.find_all('a', href=re.compile(r'/player/'))
            
            # También buscar en lista autocomplete_values
            autocomplete_links = soup.find('ul', id='autocomplete_values')
            if autocomplete_links:
                player_links = autocomplete_links.find_all('a', href=re.compile(r'/player/'))
            
            search_name = player_name.lower()
            for link in player_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Extraer ID del href (formato: /player/nombre-apellido-123456)
                href_parts = href.split('/player/')
                if len(href_parts) > 1:
                    player_slug = href_parts[-1]
                    # El ID es la última parte después del último "-"
                    player_id = player_slug.split('-')[-1]
                    
                    # Verificar si el texto coincide con el nombre buscado
                    if search_name in text.lower() or any(word in text.lower() for word in search_name.split()):
                        logger.info(f"✅ Enlace encontrado: {href} -> ID: {player_id}")
                        return self._scrape_player_details_by_slug(player_slug)
            
            logger.warning(f"⚠️ No se encontró jugador en BeSoccer para {player_name}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en request a BeSoccer: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en scraping BeSoccer: {e}")
            return None
    
    def _extract_player_id_from_json(self, data, player_name):
        """Extraer ID del jugador desde respuesta JSON del autocomplete"""
        try:
            # La estructura JSON depende de la respuesta de BeSoccer
            # Buscar en diferentes estructuras posibles
            if isinstance(data, dict):
                # Buscar en 'results', 'players', 'data', etc.
                for key in ['results', 'players', 'data', 'items']:
                    if key in data and isinstance(data[key], list):
                        for item in data[key]:
                            if 'name' in item and player_name.lower() in item['name'].lower():
                                return item.get('id') or item.get('player_id')
            return None
        except:
            return None
    
    def _scrape_player_details_by_slug(self, player_slug):
        """Scraping de detalles del jugador usando el slug completo"""
        try:
            # Construir URL del jugador con slug completo
            # Ejemplo: fausto-vera-365506
            player_url = f"https://www.besoccer.com/player/{player_slug}"
            
            logger.info(f"🌐 Escrapeando perfil de BeSoccer: {player_url}")
            
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(player_url, timeout=10)
            
            if response.status_code == 403:
                logger.warning(f"⚠️ 403 al acceder a perfil de BeSoccer")
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
                'nationality': self._extract_nationality(soup),
            }
            
            logger.info(f"✅ Datos extraídos de BeSoccer: {player_data.get('name')}")
            return player_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping detalles de BeSoccer: {e}")
            return None
    
    def _scrape_player_details_by_id(self, player_id):
        """Scraping de detalles del jugador usando su ID"""
        # Usar slug en lugar de ID directamente
        return self._scrape_player_details_by_slug(f"player-{player_id}")
    
    
    def _extract_name(self, soup):
        """Extraer nombre del jugador desde BeSoccer"""
        try:
            # Estructura: <div class="img-container"> <div class="img-wrapper"> <img alt="Fausto Vera">
            # Buscar la foto del jugador en img-wrapper (NO la bandera en el img-container)
            img_wrapper = soup.find('div', class_='img-wrapper')
            if img_wrapper:
                img = img_wrapper.find('img')
                if img:
                    alt = img.get('alt', '')
                    # Ignorar códigos de país (2 letras)
                    if alt and len(alt) > 3 and 'Profile of' not in alt:
                        return alt.strip()
            
            # Buscar en title y limpiar
            title = soup.find('title')
            if title:
                name_text = title.get_text(strip=True)
                if ' - ' in name_text:
                    name = name_text.split(' - ')[0].strip()
                    # Limpiar "Profile of"
                    if 'Profile of' in name:
                        name = name.replace('Profile of', '').strip()
                    if name and name != 'ar':
                        return name
            
            # Buscar en breadcrumb
            breadcrumb = soup.find('nav', class_=re.compile(r'breadcrumb'))
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if links and len(links) > 0:
                    text = links[-1].get_text(strip=True)
                    if 'Profile of' in text:
                        text = text.replace('Profile of', '').strip()
                    return text
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo nombre: {e}")
            return None
    
    def _extract_current_club(self, soup):
        """Extraer club actual desde BeSoccer - Estructura real de tabla"""
        try:
            # Estructura REAL de BeSoccer:
            # <div class="table-body">
            #   <div class="table-row pr10">
            #     <div>Current club</div>
            #     <a class="image-row link" href="...">
            #       <img alt="Atl. Mineiro">
            #       Atl. Mineiro
            #     </a>
            #   </div>
            
            # Buscar tabla con class='table-body' o 'table-row pr10'
            table_body = soup.find('div', class_='table-body')
            if not table_body:
                table_body = soup
            
            # Buscar directamente rows con 'Current club'
            rows = soup.find_all('div', class_='table-row pr10')
            if not rows:
                rows = soup.find_all('div', class_='table-row')
            
            logger.info(f"🔍 Buscando en {len(rows)} rows...")
            
            for row in rows:
                # Buscar el primer div (label)
                all_divs = row.find_all('div', recursive=False)
                
                if all_divs and len(all_divs) > 0:
                    label_div = all_divs[0]
                    label_text = label_div.get_text(strip=True)
                    
                    if label_text == 'Current club':
                        # Buscar el <a> con class='image-row link'
                        club_link = row.find('a', class_='image-row link')
                        if club_link:
                            club_name = club_link.get_text(strip=True)
                            logger.info(f"🏟️ Club encontrado: {club_name}")
                            return club_name
            
            logger.warning("⚠️ No se encontró club en la tabla")
            return None
        except Exception as e:
            logger.error(f"Error extrayendo club: {e}")
            return None
    
    def _extract_market_value(self, soup):
        """Extraer valor de mercado desde BeSoccer - Estructura real"""
        try:
            # Estructura real de BeSoccer:
            # <div class="data-box">
            #   <p class="number">11.2</p>
            #   <p class="info">M.€</p>
            # </div>
            # O también:
            # <div class="panel-body stat-list"> con:
            #   <div class="big-row">2</div>
            #   <div class="small-row">K.€</div>
            
            # Buscar primero en panel-body stat-list (estructura nueva)
            panel_body = soup.find('div', class_='panel-body stat-list')
            if panel_body:
                stats = panel_body.find_all('div', class_='stat')
                for stat in stats:
                    small_rows = stat.find_all('div', class_='small-row')
                    big_row = stat.find('div', class_='big-row')
                    for small in small_rows:
                        small_text = small.get_text(strip=True)
                        if (small_text in ['M.€', 'K.€'] or small_text.endswith('.€')) and big_row:
                            value_text = big_row.get_text(strip=True)
                            if value_text in ['-', '']:
                                continue
                            try:
                                value = float(value_text)
                                if small_text == 'M.€' or small_text == 'M€':
                                    value_euros = int(value * 1_000_000)
                                elif small_text == 'K.€' or small_text == 'K€':
                                    value_euros = int(value * 1_000)
                                else:
                                    value_euros = int(value)
                                logger.info(f"💰 Market value encontrado: {value_text} {small_text} = €{value_euros:,}")
                                return value_euros
                            except:
                                continue
            
            # Buscar todos los data-box que contengan "M.€" o "K.€" en el info
            data_boxes = soup.find_all('div', class_='data-box')
            
            for box in data_boxes:
                # Buscar si tiene "M.€" o "K.€" en el info
                info_elem = box.find('p', class_='info')
                if info_elem:
                    info_text = info_elem.get_text(strip=True)
                    if 'M.€' in info_text or 'K.€' in info_text:
                        # Buscar el número
                        number_elem = box.find('p', class_='number')
                        if number_elem:
                            value_text = number_elem.get_text(strip=True)
                            try:
                                value = float(value_text)
                                # Convertir según la unidad
                                if 'M.€' in info_text:
                                    value_euros = int(value * 1_000_000)
                                    logger.info(f"💰 Market value encontrado (data-box): {value_text} M€ = €{value_euros:,}")
                                elif 'K.€' in info_text:
                                    value_euros = int(value * 1_000)
                                    logger.info(f"💰 Market value encontrado (data-box): {value_text} K€ = €{value_euros:,}")
                                return value_euros
                            except ValueError:
                                continue
            
            # Fallback: buscar en texto
            all_text = soup.get_text()
            value_match = re.search(r'([\d.]+)\s*M\.€', all_text)
            if value_match:
                try:
                    value_millions = float(value_match.group(1))
                    return int(value_millions * 1_000_000)
                except ValueError:
                    pass
            
            logger.warning("⚠️ No se encontró market value en BeSoccer")
            return None
        except Exception as e:
            logger.error(f"Error extrayendo market value: {e}")
            return None
    
    def _parse_market_value(self, value_text):
        """Parsear valor de mercado a número"""
        try:
            clean_text = re.sub(r'[€$,\s]', '', value_text.lower())
            
            if 'm' in clean_text:
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number * 1000000)
            elif 'k' in clean_text:
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number * 1000)
            else:
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number)
        except:
            return None
    
    def _extract_age(self, soup):
        """Extraer edad desde BeSoccer - Estructura real"""
        try:
            # Estructura real de BeSoccer:
            # <div class="data-box">
            #   <p class="number">25</p>
            #   <p class="info">years</p>
            # </div>
            
            # Buscar todos los data-box que contengan "years"
            data_boxes = soup.find_all('div', class_='data-box')
            
            for box in data_boxes:
                # Buscar si tiene "years" en el info
                info_elem = box.find('p', class_='info')
                if info_elem and 'years' in info_elem.get_text().lower():
                    # Buscar el número
                    number_elem = box.find('p', class_='number')
                    if number_elem:
                        age_text = number_elem.get_text(strip=True)
                        try:
                            age = int(age_text)
                            if 16 <= age <= 45:  # Validar rango
                                logger.info(f"👤 Edad encontrada: {age} años")
                                return age
                        except ValueError:
                            continue
            
            # Fallback: buscar en texto
            all_text = soup.get_text()
            age_patterns = [
                r'(\d+)\s*years',
                r'(\d+)\s*años',
                r'age:\s*(\d+)',
                r'edad:\s*(\d+)',
            ]
            
            for pattern in age_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    try:
                        age = int(match.group(1))
                        if 16 <= age <= 45:
                            return age
                    except ValueError:
                        continue
            
            logger.warning("⚠️ No se encontró edad en BeSoccer")
            return None
        except Exception as e:
            logger.error(f"Error extrayendo edad: {e}")
            return None
    
    def _extract_position(self, soup):
        """Extraer posición desde BeSoccer - Estructura real de stat"""
        try:
            # Estructura REAL: <div class="panel-body stat-list"> con <div class="stat"> dentro
            # <div class="stat">
            #   <div class="big-row">72</div>
            #   <div class="small-row">kgs</div>
            #   <div class="round-row mb5 bg-role rol3"><span>Mid</span></div>
            #   <div class="small-row">position</div>
            # </div>
            
            panel_body = soup.find('div', class_='panel-body stat-list')
            if panel_body:
                stats = panel_body.find_all('div', class_='stat')
                
                for stat in stats:
                    # Buscar round-row con bg-role (es el que tiene la posición)
                    round_row = stat.find('div', class_=re.compile(r'round-row.*bg-role'))
                    if round_row:
                        # Buscar el span dentro
                        span = round_row.find('span')
                        if span:
                            position = span.get_text(strip=True)
                            # Verificar que haya un small-row que diga "position"
                            small_rows = stat.find_all('div', class_='small-row')
                            for small in small_rows:
                                if small.get_text(strip=True).lower() == 'position':
                                    logger.info(f"⚽ Posición encontrada: {position}")
                                    return position
            
            # Fallback: buscar directamente round-row con bg-role
            round_rows = soup.find_all('div', class_=re.compile(r'round-row.*bg-role'))
            for row in round_rows:
                span = row.find('span')
                if span:
                    position = span.get_text(strip=True)
                    return position
            
            logger.warning("⚠️ No se encontró posición en BeSoccer")
            return None
        except Exception as e:
            logger.error(f"Error extrayendo posición: {e}")
            return None
    
    def _extract_height(self, soup):
        """Extraer altura desde BeSoccer - Estructura real de stat"""
        try:
            # Estructura REAL: <div class="stat">
            #   <div class="big-row">180</div>
            #   <div class="small-row">cms</div>
            # </div>
            
            panel_body = soup.find('div', class_='panel-body stat-list')
            if panel_body:
                stats = panel_body.find_all('div', class_='stat')
                
                for stat in stats:
                    # Buscar small-row que diga "cms"
                    small_rows = stat.find_all('div', class_='small-row')
                    big_row = stat.find('div', class_='big-row')
                    
                    for small in small_rows:
                        if small.get_text(strip=True).lower() == 'cms' and big_row:
                            height_text = big_row.get_text(strip=True)
                            height_match = re.search(r'(\d+)', height_text)
                            if height_match:
                                height_cm = int(height_match.group(1))
                                # Validar que sea una altura razonable (150-220 cm)
                                if 150 <= height_cm <= 220:
                                    logger.info(f"📏 Altura encontrada: {height_cm} cm")
                                    return str(height_cm) + ' cm'
            
            # Fallback: buscar directamente small-row con "cms"
            small_rows = soup.find_all('div', class_='small-row')
            for small in small_rows:
                if small.get_text(strip=True).lower() == 'cms':
                    # Buscar el big-row en el mismo nivel que el small-row
                    parent = small.parent
                    if parent:
                        big_row = parent.find('div', class_='big-row')
                        if big_row:
                            height_text = big_row.get_text(strip=True)
                            height_match = re.search(r'(\d+)', height_text)
                            if height_match:
                                height_cm = int(height_match.group(1))
                                if 150 <= height_cm <= 220:
                                    return str(height_cm) + ' cm'
            
            logger.warning("⚠️ No se encontró altura en BeSoccer")
            return None
        except Exception as e:
            logger.error(f"Error extrayendo altura: {e}")
            return None
    
    def _extract_foot(self, soup):
        """Extraer pie predominante desde BeSoccer"""
        try:
            # Buscar en la tabla "Preferred foot"
            rows = soup.find_all('div', class_='table-row pr10')
            
            for row in rows:
                all_divs = row.find_all('div', recursive=False)
                if all_divs and len(all_divs) > 0:
                    label = all_divs[0].get_text(strip=True)
                    
                    if label == 'Preferred foot':
                        foot_text = all_divs[1].get_text(strip=True)
                        # Normalizar: "Right foot" -> "Right", "Left foot" -> "Left"
                        if 'Right' in foot_text:
                            logger.info("🦶 Pie encontrado: Right")
                            return 'Right'
                        elif 'Left' in foot_text:
                            logger.info("🦶 Pie encontrado: Left")
                            return 'Left'
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo pie: {e}")
            return None
    
    def _normalize_to_transfermarkt_format(self, player_data):
        """Normalizar datos de BeSoccer al formato de Transfermarkt"""
        try:
            # Normalizar posición: "Mid" -> "Midfielder", etc.
            position_map = {
                'Mid': 'Midfielder',
                'Midfielder': 'Midfielder',
                'F': 'Forward',
                'Forward': 'Forward',
                'DF': 'Defender',
                'Defender': 'Defender',
                'GK': 'Goalkeeper',
                'Goalkeeper': 'Goalkeeper',
                'ST': 'Forward',
                'CF': 'Forward',
                'LW': 'Winger',
                'RW': 'Winger',
                'CM': 'Midfielder',
                'DM': 'Defensive Midfielder',
                'CDM': 'Defensive Midfielder',
                'CAM': 'Attacking Midfielder',
                'CB': 'Centre Back',
                'LB': 'Left Back',
                'RB': 'Right Back',
            }
            
            if player_data.get('position'):
                position = player_data['position']
                normalized = position_map.get(position, position)
                player_data['position'] = normalized
            
            # Normalizar altura: "180 cm" -> "1.80 m"
            if player_data.get('height') and 'cm' in str(player_data['height']):
                height_match = re.search(r'(\d+)', str(player_data['height']))
                if height_match:
                    height_cm = int(height_match.group(1))
                    height_m = height_cm / 100
                    player_data['height'] = f"{height_m:.2f} m"
            
            return player_data
        except Exception as e:
            logger.error(f"Error normalizando formato: {e}")
            return player_data
    
    def _extract_nationality(self, soup):
        """Extraer nacionalidad desde BeSoccer - Estructura de tabla"""
        try:
            # Buscar en la tabla "Country of birth"
            rows = soup.find_all('div', class_='table-row pr10')
            if not rows:
                rows = soup.find_all('div', class_='table-row')
            
            for row in rows:
                # Buscar el primer div (label)
                all_divs = row.find_all('div', recursive=False)
                
                if all_divs and len(all_divs) > 0:
                    label_text = all_divs[0].get_text(strip=True)
                    
                    if label_text == 'Country of birth':
                        # Buscar el <a> con class='image-row link'
                        country_link = row.find('a', class_='image-row link')
                        if country_link:
                            # Extraer texto, puede estar en <div class="image-row"> dentro del <a>
                            inner_div = country_link.find('div', class_='image-row')
                            if inner_div:
                                country_name = inner_div.get_text(strip=True)
                            else:
                                country_name = country_link.get_text(strip=True)
                            
                            logger.info(f"🌍 País de nacimiento encontrado: {country_name}")
                            return country_name
                        
                        # O buscar la img alt
                        img = country_link.find('img') if country_link else None
                        if img:
                            alt = img.get('alt', '')
                            if alt:
                                logger.info(f"🌍 Nacionalidad (img alt): {alt}")
                                return alt
            
            # Fallback: buscar en las imágenes de bandera del img-container
            img_container = soup.find('div', class_='img-container')
            if img_container:
                flag_img = img_container.find('img', class_='flag')
                if flag_img:
                    flag_src = flag_img.get('src', '')
                    # Extraer código de país del src
                    match = re.search(r'/flags.*?/([a-z]{2})', flag_src)
                    if match:
                        country_code = match.group(1).upper()
                        country_map = {
                            'AR': 'Argentina', 'BR': 'Brazil', 'ES': 'Spain',
                            'FR': 'France', 'DE': 'Germany', 'IT': 'Italy',
                            'PT': 'Portugal', 'NL': 'Netherlands', 'GB': 'England',
                            'UY': 'Uruguay', 'CL': 'Chile', 'CO': 'Colombia',
                            'MX': 'Mexico', 'US': 'United States', 'UA': 'Ukraine', 'RO': 'Romania'
                        }
                        return country_map.get(country_code, country_code)
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo nacionalidad: {e}")
            return None
