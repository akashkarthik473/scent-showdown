import asyncio
import logging
import os
import random
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page, TimeoutError

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# List of common user agents that are known to work with Cloudflare
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

class FragranceScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.db_path = "fragrances.db"
        self.images_dir = Path("static/images/fragrances")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = random.choice(USER_AGENTS)

    async def setup_database(self):
        """Initialize the database with minimal schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Drop existing tables
            cursor.execute("DROP TABLE IF EXISTS wins")
            cursor.execute("DROP TABLE IF EXISTS fragrances")
            
            # Create simple tables
            cursor.execute('''
                CREATE TABLE fragrances (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    image_url TEXT,
                    local_image_path TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE wins (
                    id INTEGER PRIMARY KEY,
                    wins INTEGER DEFAULT 0,
                    FOREIGN KEY (id) REFERENCES fragrances(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Database setup completed successfully")
        except Exception as e:
            logging.error(f"Database setup failed: {str(e)}")
            raise

    async def download_image(self, url: str, fragrance_id: int) -> Optional[str]:
        """Download and save image"""
        if not url:
            logging.warning(f"No image URL provided for fragrance {fragrance_id}")
            return None
            
        try:
            local_path = self.images_dir / f"{fragrance_id}.jpg"
            
            # Skip if image already exists
            if local_path.exists():
                logging.info(f"Image already exists for fragrance {fragrance_id}")
                return str(local_path)
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    with open(local_path, 'wb') as f:
                        f.write(await response.read())
                    logging.info(f"Successfully downloaded image for fragrance {fragrance_id}")
                    return str(local_path)
                else:
                    logging.warning(f"Failed to download image for {fragrance_id}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logging.error(f"Error downloading image for {fragrance_id}: {str(e)}")
            return None

    async def setup_browser(self):
        """Initialize browser with advanced stealth settings for Cloudflare"""
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with additional arguments
            self.browser = await playwright.chromium.launch(
                headless=False,  # Cloudflare can detect headless browsers
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins',
                    '--disable-site-isolation-trials',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                    '--disable-extensions',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-default-apps',
                    '--mute-audio',
                    '--no-default-browser-check',
                    '--no-experiments',
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost',
                    '--disable-sync',
                    '--disable-translate',
                    '--metrics-recording-only',
                    '--safebrowsing-disable-auto-update',
                    '--password-store=basic',
                    '--use-mock-keychain',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-background-networking',
                    '--disable-breakpad',
                    '--disable-component-update',
                    '--disable-domain-reliability',
                    '--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process',
                    '--disable-hang-monitor',
                    '--disable-ipc-flooding-protection',
                    '--disable-notifications',
                    '--disable-setuid-sandbox',
                    '--disable-site-isolation-trials',
                    '--disable-speech-api',
                    '--disable-web-security',
                    '--hide-scrollbars',
                    '--ignore-certificate-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--mute-audio',
                    '--no-sandbox',
                    '--no-zygote',
                    '--window-size=1920,1080',
                ]
            )
            
            # Create a new context with specific settings
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self.user_agent,
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True,
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                permissions=['geolocation'],
                color_scheme='light',
                reduced_motion='no-preference',
                forced_colors='none',
                accept_downloads=True,
                has_touch=True,
                is_mobile=False,
                device_scale_factor=1
            )
            
            # Add advanced stealth scripts
            await context.add_init_script("""
                // Overwrite the 'webdriver' property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Add plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf"},
                            description: "Portable Document Format",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        },
                        {
                            0: {type: "application/x-nacl"},
                            description: "Native Client Executable",
                            filename: "internal-nacl-plugin",
                            length: 1,
                            name: "Native Client"
                        }
                    ]
                });
                
                // Add languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Add chrome object
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {
                        isInstalled: false,
                        InstallState: {
                            DISABLED: 'disabled',
                            INSTALLED: 'installed',
                            NOT_INSTALLED: 'not_installed'
                        },
                        RunningState: {
                            CANNOT_RUN: 'cannot_run',
                            READY_TO_RUN: 'ready_to_run',
                            RUNNING: 'running'
                        }
                    },
                    webstore: {
                        onInstallStageChanged: {},
                        onDownloadProgress: {}
                    }
                };
                
                // Add permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
                
                // Add WebGL
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, [parameter]);
                };
                
                // Add canvas fingerprint
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type) {
                    const context = originalGetContext.apply(this, arguments);
                    if (type === '2d') {
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function() {
                            const imageData = originalGetImageData.apply(this, arguments);
                            // Add some noise to the image data
                            for (let i = 0; i < imageData.data.length; i += 4) {
                                imageData.data[i] = imageData.data[i] + Math.random() * 2 - 1;
                            }
                            return imageData;
                        };
                    }
                    return context;
                };
            """)
            
            self.page = await context.new_page()
            
            # Set extra headers to look more like a real browser
            await self.page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'DNT': '1'
            })
            
            # Add random mouse movements
            for _ in range(3):
                await self.page.mouse.move(
                    random.randint(0, 1920),
                    random.randint(0, 1080),
                    steps=25
                )
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            self.session = aiohttp.ClientSession(headers={
                'User-Agent': self.user_agent,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'DNT': '1'
            })
            
            logging.info("Browser setup completed successfully")
            
        except Exception as e:
            logging.error(f"Browser setup failed: {str(e)}")
            raise

    async def handle_cloudflare(self):
        """Handle Cloudflare challenge if present"""
        try:
            # Wait for Cloudflare challenge
            challenge_present = await self.page.wait_for_selector(
                '#challenge-running, #challenge-stage, #cf-please-wait, #cf-challenge-running',
                timeout=5000
            )
            
            if challenge_present:
                logging.info("Cloudflare challenge detected, waiting for it to complete...")
                
                # Wait for the challenge to complete
                await self.page.wait_for_selector(
                    '#challenge-running, #challenge-stage, #cf-please-wait, #cf-challenge-running',
                    state='hidden',
                    timeout=30000
                )
                
                # Additional wait to ensure page is fully loaded
                await asyncio.sleep(5)
                
                logging.info("Cloudflare challenge completed")
                return True
                
        except TimeoutError:
            logging.info("No Cloudflare challenge detected")
            return False
        except Exception as e:
            logging.error(f"Error handling Cloudflare challenge: {str(e)}")
            return False

    async def extract_fragrance_data(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract just name and image data"""
        try:
            link_tag = card.select_one("a[href*='/perfume/']")
            if not link_tag:
                logging.debug("No link tag found in card")
                return None
            
            href = link_tag['href']
            name = link_tag.get_text(strip=True)
            
            if not name:
                logging.debug("No name found in link tag")
                return None
            
            # Extract ID from URL
            try:
                frag_id = int(href.split('-')[-1].replace('.html', ''))
            except (ValueError, IndexError) as e:
                logging.warning(f"Could not extract ID from URL {href}: {str(e)}")
                return None
            
            # Get image URL
            img_tag = card.select_one("img")
            image_url = img_tag['src'] if img_tag else None
            
            if not image_url:
                logging.warning(f"No image URL found for fragrance {name}")
            
            return {
                'id': frag_id,
                'name': name,
                'image_url': image_url
            }
            
        except Exception as e:
            logging.error(f"Error extracting data from card: {str(e)}")
            return None

    async def scrape_fragrances(self):
        """Main scraping function with Cloudflare handling"""
        try:
            await self.setup_browser()
            await self.setup_database()
            
            logging.info("Starting fragrance data collection...")
            
            # Try to load the page with multiple attempts
            for attempt in range(3):
                try:
                    logging.info(f"Attempt {attempt + 1} to load page...")
                    
                    # Add longer random delay before request
                    await asyncio.sleep(random.uniform(5, 10))
                    
                    # Try loading the search page directly
                    response = await self.page.goto(
                        "https://www.fragrantica.com/search/",
                        wait_until="domcontentloaded",
                        timeout=60000
                    )
                    
                    if not response:
                        logging.error("Failed to get response from search page")
                        continue
                        
                    logging.info(f"Search page status: {response.status}")
                    
                    # Handle Cloudflare challenge if present
                    await self.handle_cloudflare()
                    
                    # More human-like scrolling
                    for _ in range(3):
                        scroll_amount = random.randint(100, 300)
                        await self.page.evaluate(f"""
                            window.scrollTo({{
                                top: {scroll_amount},
                                behavior: 'smooth'
                            }});
                        """)
                        await asyncio.sleep(random.uniform(1, 3))
                    
                    # Take a screenshot for debugging
                    await self.page.screenshot(path="debug_screenshot.png")
                    logging.info("Saved debug screenshot")
                    
                    # Get the page content and log what we see
                    content = await self.page.content()
                    logging.debug(f"Page content length: {len(content)}")
                    
                    # Check if we're being blocked
                    if "captcha" in content.lower() or "robot" in content.lower():
                        logging.error("Detected anti-bot protection")
                        # Wait longer if captcha detected
                        if "captcha" in content.lower():
                            logging.info("Waiting 2 minutes before retrying...")
                            await asyncio.sleep(120)
                        raise Exception("Website is blocking automated access")
                    
                    # Try different selectors with longer timeouts
                    selectors = [
                        "div.card-product",
                        ".card-product",
                        "div[class*='card']",
                        "div[class*='product']"
                    ]
                    
                    for selector in selectors:
                        try:
                            logging.info(f"Trying selector: {selector}")
                            await self.page.wait_for_selector(selector, timeout=10000)  # Increased timeout
                            logging.info(f"Found selector: {selector}")
                            break
                        except Exception as e:
                            logging.debug(f"Selector {selector} not found: {str(e)}")
                            continue
                    else:
                        logging.error("Could not find any fragrance cards on the page")
                        logging.debug(f"Page content preview: {content[:1000]}")
                        raise Exception("No fragrance cards found")
                    
                    logging.info("Successfully loaded the search page")
                    break
                    
                except TimeoutError as e:
                    logging.warning(f"Timeout on attempt {attempt + 1}: {str(e)}")
                    if attempt == 2:
                        raise
                    await asyncio.sleep(random.uniform(10, 20))
                except Exception as e:
                    logging.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    if attempt == 2:
                        raise
                    await asyncio.sleep(random.uniform(10, 20))
            
            # Get the page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Try different selectors for the cards
            cards = []
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    logging.info(f"Found {len(cards)} cards using selector: {selector}")
                    break
            
            if not cards:
                logging.error("No fragrance cards found on the page")
                return
            
            # Limit the number of fragrances we process
            MAX_FRAGRANCES = 20  # Reduced from previous unlimited amount
            cards = cards[:MAX_FRAGRANCES]
            logging.info(f"Processing {len(cards)} fragrances (limited to {MAX_FRAGRANCES})")
            
            # Process fragrances with delays between each
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            processed_count = 0
            for card in cards:
                # Add delay between processing each fragrance
                await asyncio.sleep(random.uniform(2, 4))
                
                fragrance_data = await self.extract_fragrance_data(card)
                if fragrance_data:
                    # Add delay before downloading image
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    # Download image
                    local_image_path = await self.download_image(
                        fragrance_data['image_url'], 
                        fragrance_data['id']
                    )
                    
                    # Add delay before database operation
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    # Store in database
                    try:
                        cursor.execute('''
                            INSERT INTO fragrances (id, name, image_url, local_image_path)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            fragrance_data['id'],
                            fragrance_data['name'],
                            fragrance_data['image_url'],
                            local_image_path
                        ))
                        processed_count += 1
                        
                        # Commit more frequently
                        if processed_count % 5 == 0:  # Changed from 10 to 5
                            conn.commit()
                            logging.info(f"Committed {processed_count} fragrances to database")
                            
                    except sqlite3.Error as e:
                        logging.error(f"Database error for fragrance {fragrance_data['name']}: {str(e)}")
                        continue
            
            conn.commit()
            logging.info(f"Successfully stored {processed_count} fragrances in the database")
            
        except Exception as e:
            logging.error(f"An error occurred during scraping: {str(e)}")
            raise
        finally:
            if self.browser:
                await self.browser.close()
            if self.session:
                await self.session.close()
            if 'conn' in locals():
                conn.close()

async def main():
    try:
        scraper = FragranceScraper()
        await scraper.scrape_fragrances()
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
