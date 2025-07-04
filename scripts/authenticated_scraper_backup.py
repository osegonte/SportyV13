#!/usr/bin/env python3
"""
Authenticated SportyBet Scraper
This scraper logs in first, then accesses protected content and APIs
"""

import requests
import json
import time
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from settings import HEADERS, SPORTYBET_BASE_URL, SPORTYBET_LIVE_URL, SPORTYBET_UPCOMING_URL
except ImportError:
    print("Using default settings...")
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    SPORTYBET_BASE_URL = "https://sportybet.com/ng"
    SPORTYBET_UPCOMING_URL = "https://sportybet.com/ng/sport/football/sr:category:1/today"
    SPORTYBET_LIVE_URL = "https://sportybet.com/ng/sport/football/sr:category:1/live"

class AuthenticatedSportyBetScraper:
    def __init__(self, headless=True, save_session=True):
        self.headless = headless
        self.save_session = save_session
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setup_logging()
        self.matches_data = []
        self.network_requests = []
        self.is_logged_in = False
        self.session_cookies = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        Path("logs").mkdir(exist_ok=True)
        log_file = f"logs/auth_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_selenium(self):
        """Setup Selenium WebDriver with network logging"""
        if self.driver:
            return True
            
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Performance and stability options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={HEADERS['User-Agent']}")
            
            # Enable network logging (different approach for compatibility)
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # Add prefs to handle notifications, etc.
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("✅ Chrome WebDriver initialized for authentication")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up Selenium: {e}")
            return False

    def login_to_sportybet(self, username=None, password=None):
        """Login to SportyBet - will prompt for credentials if not provided"""
        if not self.setup_selenium():
            return False
            
        try:
            self.logger.info("🔐 Starting SportyBet login process...")
            
            # Navigate to login page
            login_url = f"{SPORTYBET_BASE_URL}/auth/login"
            self.logger.info(f"📱 Navigating to login page: {login_url}")
            self.driver.get(login_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for login form elements
            login_selectors = [
                'input[type="email"]', 'input[name="email"]', 'input[placeholder*="email"]',
                'input[type="text"]', 'input[name="username"]', 'input[placeholder*="phone"]',
                '#email', '#username', '#phone', '.login-input'
            ]
            
            password_selectors = [
                'input[type="password"]', 'input[name="password"]', 
                '#password', '.password-input'
            ]
            
            login_button_selectors = [
                'button[type="submit"]', 'input[type="submit"]', 
                'button:contains("Login")', 'button:contains("Sign")',
                '.login-btn', '.submit-btn', '#login-btn'
            ]
            
            username_field = None
            password_field = None
            login_button = None
            
            # Find username field
            for selector in login_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"✅ Found username field: {selector}")
                    break
                except:
                    continue
            
            # Find password field
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"✅ Found password field: {selector}")
                    break
                except:
                    continue
            
            # Find login button
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"✅ Found login button: {selector}")
                    break
                except:
                    continue
            
            if not username_field or not password_field:
                self.logger.error("❌ Could not find login form fields")
                # Save page source for debugging
                debug_file = Path("temp") / f"login_page_{datetime.now().strftime('%H%M%S')}.html"
                debug_file.parent.mkdir(exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                self.logger.info(f"🔍 Login page saved to: {debug_file}")
                return False
            
            # Get credentials if not provided
            if not username:
                print("\n🔐 SportyBet Login Required")
                print("=" * 30)
                username = input("📧 Enter your SportyBet email/phone: ").strip()
                
            if not password:
                import getpass
                password = getpass.getpass("🔒 Enter your password: ").strip()
            
            if not username or not password:
                self.logger.error("❌ Username or password not provided")
                return False
            
            # Fill in credentials
            self.logger.info("📝 Filling in credentials...")
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Click login button
            self.logger.info("🚀 Clicking login button...")
            if login_button:
                login_button.click()
            else:
                # Try pressing Enter as fallback
                password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            self.logger.info("⏳ Waiting for login to complete...")
            
            # Check for successful login indicators
            success_indicators = [
                "dashboard", "account", "balance", "profile", "logout"
            ]
            
            # Wait up to 15 seconds for login
            login_successful = False
            for i in range(15):
                time.sleep(1)
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # Check if redirected away from login page
                if "login" not in current_url.lower():
                    login_successful = True
                    break
                    
                # Check for success indicators in page content
                if any(indicator in page_source for indicator in success_indicators):
                    login_successful = True
                    break
                    
                # Check for error messages
                error_indicators = ["error", "invalid", "incorrect", "failed"]
                if any(error in page_source for error in error_indicators):
                    self.logger.error("❌ Login failed - error message detected")
                    break
            
            if login_successful:
                self.logger.info("✅ Login successful!")
                self.is_logged_in = True
                
                # Save session cookies
                self.session_cookies = self.driver.get_cookies()
                self.logger.info(f"🍪 Saved {len(self.session_cookies)} session cookies")
                
                # Transfer cookies to requests session
                for cookie in self.session_cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                # Save session if requested
                if self.save_session:
                    self.save_session_data()
                
                return True
            else:
                self.logger.error("❌ Login failed - timeout or error")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error during login: {e}")
            return False

    def save_session_data(self):
        """Save session data for future use"""
        try:
            session_data = {
                'cookies': self.session_cookies,
                'timestamp': datetime.now().isoformat(),
                'user_agent': HEADERS['User-Agent']
            }
            
            session_file = Path("temp") / "sportybet_session.json"
            session_file.parent.mkdir(exist_ok=True)
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            self.logger.info(f"💾 Session data saved to: {session_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving session: {e}")

    def load_session_data(self):
        """Load previously saved session data"""
        try:
            session_file = Path("temp") / "sportybet_session.json"
            
            if not session_file.exists():
                return False
                
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is not too old (24 hours)
            session_time = datetime.fromisoformat(session_data['timestamp'])
            if (datetime.now() - session_time).total_seconds() > 86400:
                self.logger.info("⏰ Session data is too old, will login fresh")
                return False
            
            # Restore cookies to requests session
            for cookie in session_data['cookies']:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            self.session_cookies = session_data['cookies']
            self.is_logged_in = True
            
            self.logger.info("✅ Session data loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading session: {e}")
            return False

    def capture_network_requests(self, url, wait_time=30):
        """Capture network requests after login"""
        if not self.driver:
            return []
            
        network_requests = []
        
        try:
            self.logger.info(f"📡 Capturing network requests for: {url}")
            
            # Navigate to the page
            self.driver.get(url)
            
            # Wait for page to load and capture any AJAX requests
            time.sleep(wait_time)
            
            # Execute JavaScript to capture any fetch/xhr requests
            # This is a workaround since performance logs didn't work
            captured_requests = self.driver.execute_script("""
                // Override fetch and XMLHttpRequest to capture requests
                var capturedRequests = [];
                
                // Capture existing requests in memory (if any tracking exists)
                if (window.performance && window.performance.getEntriesByType) {
                    var entries = window.performance.getEntriesByType('resource');
                    for (var i = 0; i < entries.length; i++) {
                        var entry = entries[i];
                        if (entry.name.includes('api') || entry.name.includes('ajax') || 
                            entry.name.includes('data') || entry.name.includes('match') ||
                            entry.name.includes('event') || entry.name.includes('odds')) {
                            capturedRequests.push({
                                url: entry.name,
                                type: entry.initiatorType,
                                duration: entry.duration
                            });
                        }
                    }
                }
                
                return capturedRequests;
            """)
            
            if captured_requests:
                network_requests.extend(captured_requests)
                self.logger.info(f"📊 Captured {len(captured_requests)} network requests")
            
        except Exception as e:
            self.logger.error(f"❌ Error capturing network requests: {e}")
            
        return network_requests

    def scrape_authenticated_content(self, url):
        """Scrape content after authentication"""
        matches = []
        
        try:
            self.logger.info(f"🔓 Scraping authenticated content: {url}")
            
            # Method 1: Use Selenium to get fully loaded page
            if self.driver:
                self.driver.get(url)
                time.sleep(10)  # Wait longer for authenticated content
                
                # Save the authenticated page source
                auth_source_file = Path("temp") / f"auth_source_{datetime.now().strftime('%H%M%S')}.html"
                auth_source_file.parent.mkdir(exist_ok=True)
                with open(auth_source_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                self.logger.info(f"💾 Authenticated page saved to: {auth_source_file}")
                
                # Parse the authenticated page
                matches.extend(self.parse_authenticated_page(self.driver.page_source))
                
                # Capture network requests
                network_requests = self.capture_network_requests(url, wait_time=15)
                self.network_requests.extend(network_requests)
            
            # Method 2: Use requests session with cookies
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    self.logger.info(f"✅ Requests session access successful: {len(response.text)} chars")
                    matches.extend(self.parse_authenticated_page(response.text))
                else:
                    self.logger.warning(f"⚠️ Requests session returned: {response.status_code}")
            except Exception as e:
                self.logger.error(f"❌ Requests session error: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ Error scraping authenticated content: {e}")
            
        return matches

    def parse_authenticated_page(self, html_content):
        """Parse matches from authenticated page content"""
        matches = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for match data in the authenticated content
            # This would be similar to previous parsing but might find more content
            
            # Check for JavaScript variables with match data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Look for JSON data structures
                    json_patterns = [
                        r'matches\s*[:=]\s*(\[.*?\])',
                        r'events\s*[:=]\s*(\[.*?\])',
                        r'fixtures\s*[:=]\s*(\[.*?\])',
                        r'data\s*[:=]\s*(\{.*?\})'
                    ]
                    
                    for pattern in json_patterns:
                        json_matches = re.findall(pattern, script_content, re.DOTALL)
                        for json_match in json_matches:
                            try:
                                data = json.loads(json_match)
                                if isinstance(data, list):
                                    for item in data:
                                        match = self.extract_match_from_data(item)
                                        if match:
                                            matches.append(match)
                                elif isinstance(data, dict):
                                    match = self.extract_match_from_data(data)
                                    if match:
                                        matches.append(match)
                            except:
                                continue
            
            self.logger.info(f"📊 Parsed {len(matches)} matches from authenticated content")
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing authenticated page: {e}")
            
        return matches

    def extract_match_from_data(self, data):
        """Extract match information from data object"""
        if not isinstance(data, dict):
            return None
            
        match = {
            'scraped_at': datetime.now().isoformat(),
            'source': 'authenticated'
        }
        
        # Extract teams
        team_mappings = [
            ('home', 'away'), ('homeTeam', 'awayTeam'), ('team1', 'team2'),
            ('home_team', 'away_team'), ('home_name', 'away_name')
        ]
        
        for home_key, away_key in team_mappings:
            if home_key in data and away_key in data:
                match['home_team'] = str(data[home_key])
                match['away_team'] = str(data[away_key])
                break
        
        # Extract other fields
        field_mappings = {
            'match_time': ['time', 'start_time', 'kick_off', 'startTime', 'date'],
            'competition': ['competition', 'league', 'tournament', 'category'],
            'match_id': ['id', 'match_id', 'event_id', 'fixture_id'],
            'status': ['status', 'state', 'match_status']
        }
        
        for match_field, possible_keys in field_mappings.items():
            for key in possible_keys:
                if key in data:
                    match[match_field] = str(data[key])
                    break
        
        # Extract odds if present
        if 'odds' in data:
            match['odds'] = data['odds']
        
        # Only return if we have team information
        if 'home_team' in match and 'away_team' in match:
            return match
            
        return None

    def test_authenticated_apis(self):
        """Test API endpoints with authentication"""
        working_endpoints = []
        
        # Common SportyBet API patterns
        api_endpoints = [
            f"{SPORTYBET_BASE_URL}/api/ng/football/fixtures",
            f"{SPORTYBET_BASE_URL}/api/ng/football/live",
            f"{SPORTYBET_BASE_URL}/api/ng/football/today",
            f"{SPORTYBET_BASE_URL}/api/ng/sports/football",
            f"{SPORTYBET_BASE_URL}/api/ng/matches",
            f"{SPORTYBET_BASE_URL}/api/ng/events",
            "https://api.sportybet.com/api/ng/football/fixtures",
            "https://api.sportybet.com/api/ng/football/live"
        ]
        
        for endpoint in api_endpoints:
            try:
                self.logger.info(f"🧪 Testing authenticated API: {endpoint}")
                response = self.session.get(endpoint, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data:
                            working_endpoints.append({
                                'url': endpoint,
                                'status': response.status_code,
                                'data_type': type(data).__name__,
                                'content_length': len(response.text)
                            })
                            self.logger.info(f"✅ Working authenticated API: {endpoint}")
                            
                            # Parse matches from API response
                            api_matches = self.parse_json_matches(data)
                            self.matches_data.extend(api_matches)
                    except:
                        pass
                        
            except Exception as e:
                self.logger.warning(f"⚠️ API test failed for {endpoint}: {e}")
                
        return working_endpoints

    def parse_json_matches(self, data):
        """Parse matches from JSON API response"""
        matches = []
        
        def recursive_parse(obj):
            if isinstance(obj, dict):
                match = self.extract_match_from_data(obj)
                if match:
                    matches.append(match)
                for value in obj.values():
                    recursive_parse(value)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_parse(item)
        
        recursive_parse(data)
        return matches

    def save_data(self):
        """Save all collected data"""
        if not self.matches_data and not self.network_requests:
            self.logger.warning("No data to save")
            return
            
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save matches
        if self.matches_data:
            matches_file = output_dir / f"sportybet_authenticated_{timestamp}.json"
            with open(matches_file, 'w', encoding='utf-8') as f:
                json.dump(self.matches_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Matches saved to: {matches_file}")
            
            # Save as CSV
            try:
                df = pd.DataFrame(self.matches_data)
                csv_file = matches_file.with_suffix('.csv')
                df.to_csv(csv_file, index=False)
                self.logger.info(f"✅ CSV saved to: {csv_file}")
            except Exception as e:
                self.logger.error(f"❌ Error saving CSV: {e}")
        
        # Save network requests
        if self.network_requests:
            network_file = output_dir / f"network_requests_{timestamp}.json"
            with open(network_file, 'w', encoding='utf-8') as f:
                json.dump(self.network_requests, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Network requests saved to: {network_file}")

    def run(self, username=None, password=None, use_saved_session=True):
        """Main execution method"""
        self.logger.info("🚀 Starting Authenticated SportyBet scraper...")
        
        try:
            # Try to load saved session first
            if use_saved_session and self.load_session_data():
                self.logger.info("✅ Using saved session")
            else:
                # Login required
                if not self.login_to_sportybet(username, password):
                    self.logger.error("❌ Login failed, cannot proceed")
                    return False
            
            # Test authenticated APIs
            self.logger.info("🔗 Testing authenticated APIs...")
            working_apis = self.test_authenticated_apis()
            
            # Scrape authenticated content
            pages_to_scrape = [SPORTYBET_UPCOMING_URL, SPORTYBET_LIVE_URL]
            
            for url in pages_to_scrape:
                self.logger.info(f"📖 Scraping: {url}")
                matches = self.scrape_authenticated_content(url)
                self.matches_data.extend(matches)
            
            # Save all data
            self.save_data()
            
            self.logger.info(f"✅ Authenticated scraping completed!")
            self.logger.info(f"📊 Total matches found: {len(self.matches_data)}")
            self.logger.info(f"🔗 Working APIs: {len(working_apis)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error during authenticated scraping: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔧 WebDriver closed")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Authenticated SportyBet Scraper')
    parser.add_argument('--username', help='SportyBet username/email')
    parser.add_argument('--password', help='SportyBet password')
    parser.add_argument('--no-headless', action='store_true', help='Show browser window')
    parser.add_argument('--no-session', action='store_true', help='Always login fresh')
    
    args = parser.parse_args()
    
    scraper = AuthenticatedSportyBetScraper(
        headless=not args.no_headless,
        save_session=not args.no_session
    )
    
    success = scraper.run(
        username=args.username,
        password=args.password,
        use_saved_session=not args.no_session
    )
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()