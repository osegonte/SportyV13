#!/usr/bin/env python3
"""
SportyBet API Scraper
This scraper finds and uses SportyBet's API endpoints directly
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

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from settings import HEADERS, SPORTYBET_BASE_URL, SPORTYBET_LIVE_URL, SPORTYBET_UPCOMING_URL
except ImportError:
    print("Using default settings...")
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    SPORTYBET_UPCOMING_URL = "https://sportybet.com/ng/sport/football/sr:category:1/today"
    SPORTYBET_LIVE_URL = "https://sportybet.com/ng/sport/football/sr:category:1/live"

class SportyBetAPIecraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setup_logging()
        self.matches_data = []
        self.api_endpoints = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        Path("logs").mkdir(exist_ok=True)
        log_file = f"logs/api_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def intercept_network_requests(self, url, timeout=60):
        """Use Selenium to intercept network requests and find API endpoints"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Enable logging to capture network requests
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = None
        api_calls = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            self.logger.info(f"🔍 Intercepting network requests for: {url}")
            
            # Enable performance logging to capture network events
            driver.execute_cdp_cmd('Network.enable', {})
            
            # Navigate to the page
            driver.get(url)
            
            # Wait for page to start loading
            time.sleep(5)
            
            # Get network logs
            logs = driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response_url = message['message']['params']['response']['url']
                    
                    # Look for API endpoints
                    if any(keyword in response_url.lower() for keyword in ['api', 'ajax', 'json', 'data', 'match', 'event', 'odds']):
                        api_calls.append({
                            'url': response_url,
                            'method': message['message']['params']['response'].get('method', 'GET'),
                            'status': message['message']['params']['response']['status'],
                            'type': message['message']['params']['type']
                        })
                        self.logger.info(f"📡 Found API call: {response_url}")
            
            # Also try to wait for specific elements that might trigger API calls
            try:
                # Wait for any content to load
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                # Look for data in window variables
                js_data = driver.execute_script("""
                    var data = {};
                    for (var key in window) {
                        if (typeof window[key] === 'object' && window[key] !== null) {
                            try {
                                var str = JSON.stringify(window[key]);
                                if (str.includes('match') || str.includes('event') || str.includes('odds') || str.includes('team')) {
                                    data[key] = window[key];
                                }
                            } catch(e) {}
                        }
                    }
                    return data;
                """)
                
                if js_data:
                    self.logger.info(f"📊 Found JavaScript data: {list(js_data.keys())}")
                    return js_data, api_calls
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Timeout waiting for content: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Error intercepting requests: {e}")
            
        finally:
            if driver:
                driver.quit()
                
        return None, api_calls

    def find_api_endpoints_from_source(self, url):
        """Extract potential API endpoints from page source"""
        try:
            response = self.session.get(url, timeout=30)
            content = response.text
            
            # Save source for inspection
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            source_file = temp_dir / f"source_{datetime.now().strftime('%H%M%S')}.html"
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"📄 Source saved to: {source_file}")
            
            # Look for API endpoints in JavaScript
            api_patterns = [
                r'["\']https?://[^"\']*api[^"\']*["\']',
                r'["\']https?://[^"\']*ajax[^"\']*["\']',
                r'["\']https?://[^"\']*data[^"\']*["\']',
                r'["\']https?://[^"\']*match[^"\']*["\']',
                r'["\']https?://[^"\']*event[^"\']*["\']',
                r'["\']https?://[^"\']*odds[^"\']*["\']',
                r'baseUrl["\']?\s*:\s*["\'][^"\']+["\']',
                r'apiUrl["\']?\s*:\s*["\'][^"\']+["\']',
                r'endpoint["\']?\s*:\s*["\'][^"\']+["\']'
            ]
            
            endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Clean up the match
                    endpoint = match.strip('\'"')
                    if endpoint.startswith('http'):
                        endpoints.add(endpoint)
                        self.logger.info(f"🎯 Found potential endpoint: {endpoint}")
            
            # Look for JSON data in script tags
            script_data = []
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            for script in scripts:
                if any(keyword in script.lower() for keyword in ['match', 'event', 'odds', 'team', 'fixture']):
                    # Try to extract JSON objects
                    json_patterns = [
                        r'\{[^{}]*(?:"(?:match|event|odds|team|fixture)")[^{}]*\}',
                        r'\[[^\[\]]*(?:"(?:match|event|odds|team|fixture)")[^\[\]]*\]'
                    ]
                    
                    for json_pattern in json_patterns:
                        json_matches = re.findall(json_pattern, script, re.IGNORECASE)
                        for json_match in json_matches:
                            try:
                                data = json.loads(json_match)
                                script_data.append(data)
                                self.logger.info(f"📊 Found JSON data: {type(data)} with {len(data) if isinstance(data, (list, dict)) else 0} items")
                            except:
                                pass
            
            return list(endpoints), script_data
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing source: {e}")
            return [], []

    def test_api_endpoints(self, endpoints):
        """Test discovered API endpoints"""
        working_endpoints = []
        
        for endpoint in endpoints:
            try:
                self.logger.info(f"🧪 Testing endpoint: {endpoint}")
                
                # Try different HTTP methods and headers
                test_headers = [
                    self.session.headers,
                    {**self.session.headers, 'Accept': 'application/json'},
                    {**self.session.headers, 'X-Requested-With': 'XMLHttpRequest'},
                    {**self.session.headers, 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}
                ]
                
                for headers in test_headers:
                    try:
                        response = self.session.get(endpoint, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            
                            if 'json' in content_type:
                                try:
                                    data = response.json()
                                    if data:  # Not empty
                                        working_endpoints.append({
                                            'url': endpoint,
                                            'headers': headers,
                                            'response_size': len(response.text),
                                            'data_type': type(data).__name__,
                                            'sample_keys': list(data.keys()) if isinstance(data, dict) else None
                                        })
                                        self.logger.info(f"✅ Working endpoint: {endpoint}")
                                        break
                                except:
                                    pass
                            elif len(response.text) > 1000:  # Significant content
                                working_endpoints.append({
                                    'url': endpoint,
                                    'headers': headers,
                                    'response_size': len(response.text),
                                    'data_type': 'text',
                                    'sample_keys': None
                                })
                                self.logger.info(f"✅ Working endpoint (text): {endpoint}")
                                break
                                
                    except Exception as e:
                        continue
                        
            except Exception as e:
                self.logger.warning(f"⚠️ Error testing {endpoint}: {e}")
                
        return working_endpoints

    def extract_matches_from_api(self, endpoint_info):
        """Extract match data from working API endpoint"""
        try:
            response = self.session.get(
                endpoint_info['url'], 
                headers=endpoint_info['headers'], 
                timeout=30
            )
            
            if 'json' in response.headers.get('content-type', '').lower():
                data = response.json()
                return self.parse_json_matches(data)
            else:
                # Try to parse as HTML or other format
                return self.parse_text_matches(response.text)
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting from API: {e}")
            return []

    def parse_json_matches(self, data):
        """Parse matches from JSON data"""
        matches = []
        
        def extract_matches_recursive(obj, path=""):
            if isinstance(obj, dict):
                # Look for match-like objects
                if any(key in obj for key in ['home', 'away', 'team1', 'team2', 'homeTeam', 'awayTeam']):
                    match = self.extract_match_from_object(obj)
                    if match:
                        matches.append(match)
                
                # Recurse into nested objects
                for key, value in obj.items():
                    extract_matches_recursive(value, f"{path}.{key}" if path else key)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_matches_recursive(item, f"{path}[{i}]" if path else f"[{i}]")
        
        extract_matches_recursive(data)
        return matches

    def extract_match_from_object(self, obj):
        """Extract match data from a single object"""
        try:
            match = {
                'scraped_at': datetime.now().isoformat(),
                'source': 'api'
            }
            
            # Extract teams
            team_keys = [
                ('home', 'away'), ('home_team', 'away_team'),
                ('homeTeam', 'awayTeam'), ('team1', 'team2'),
                ('home_name', 'away_name')
            ]
            
            for home_key, away_key in team_keys:
                if home_key in obj and away_key in obj:
                    match['home_team'] = str(obj[home_key])
                    match['away_team'] = str(obj[away_key])
                    break
            
            # Extract time/date
            time_keys = ['time', 'start_time', 'kick_off', 'match_time', 'date', 'startTime']
            for key in time_keys:
                if key in obj:
                    match['match_time'] = str(obj[key])
                    break
            
            # Extract odds
            if 'odds' in obj:
                match['odds'] = obj['odds']
            
            # Extract competition/league
            comp_keys = ['competition', 'league', 'tournament', 'category']
            for key in comp_keys:
                if key in obj:
                    match['competition'] = str(obj[key])
                    break
            
            # Extract match ID
            id_keys = ['id', 'match_id', 'event_id', 'fixture_id']
            for key in id_keys:
                if key in obj:
                    match['match_id'] = str(obj[key])
                    break
            
            # Only return if we have at least teams
            if 'home_team' in match and 'away_team' in match:
                return match
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting match: {e}")
            
        return None

    def parse_text_matches(self, text):
        """Parse matches from text content"""
        # This is a fallback for non-JSON responses
        matches = []
        
        # Look for team vs team patterns
        patterns = [
            r'([A-Za-z\s]+)\s+vs?\s+([A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+-\s+([A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+x\s+([A-Za-z\s]+)'
        ]
        
        for pattern in patterns:
            matches_found = re.findall(pattern, text)
            for home, away in matches_found:
                match = {
                    'home_team': home.strip(),
                    'away_team': away.strip(),
                    'source': 'text_parsing',
                    'scraped_at': datetime.now().isoformat()
                }
                matches.append(match)
        
        return matches

    def save_data(self):
        """Save scraped data and API information"""
        if not self.matches_data and not self.api_endpoints:
            self.logger.warning("No data to save")
            return
            
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save matches data
        if self.matches_data:
            json_path = output_dir / f"sportybet_api_matches_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.matches_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Matches saved to {json_path}")
            
            # Save as CSV
            try:
                df = pd.DataFrame(self.matches_data)
                csv_path = json_path.with_suffix('.csv')
                df.to_csv(csv_path, index=False)
                self.logger.info(f"✅ CSV saved to {csv_path}")
            except Exception as e:
                self.logger.error(f"❌ Error saving CSV: {e}")
        
        # Save API endpoints info
        if self.api_endpoints:
            api_path = output_dir / f"sportybet_api_endpoints_{timestamp}.json"
            with open(api_path, 'w', encoding='utf-8') as f:
                json.dump(self.api_endpoints, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ API endpoints saved to {api_path}")

    def run(self):
        """Main scraping method"""
        self.logger.info("🚀 Starting SportyBet API scraper...")
        
        try:
            # Step 1: Intercept network requests
            self.logger.info("📡 Step 1: Intercepting network requests...")
            js_data, network_calls = self.intercept_network_requests(SPORTYBET_UPCOMING_URL)
            
            if js_data:
                self.logger.info("📊 Found JavaScript data, parsing...")
                for key, data in js_data.items():
                    matches = self.parse_json_matches(data)
                    self.matches_data.extend(matches)
            
            # Step 2: Find API endpoints from source
            self.logger.info("🔍 Step 2: Analyzing page source for endpoints...")
            endpoints, script_data = self.find_api_endpoints_from_source(SPORTYBET_UPCOMING_URL)
            
            if script_data:
                self.logger.info("📜 Found script data, parsing...")
                for data in script_data:
                    matches = self.parse_json_matches(data)
                    self.matches_data.extend(matches)
            
            # Step 3: Test discovered endpoints
            all_endpoints = list(set(endpoints + [call['url'] for call in network_calls]))
            if all_endpoints:
                self.logger.info(f"🧪 Step 3: Testing {len(all_endpoints)} discovered endpoints...")
                working_endpoints = self.test_api_endpoints(all_endpoints)
                self.api_endpoints = working_endpoints
                
                # Extract data from working endpoints
                for endpoint in working_endpoints:
                    matches = self.extract_matches_from_api(endpoint)
                    self.matches_data.extend(matches)
            
            # Save results
            self.save_data()
            
            self.logger.info(f"✅ API scraping completed!")
            self.logger.info(f"📊 Total matches found: {len(self.matches_data)}")
            self.logger.info(f"🔗 Working API endpoints: {len(self.api_endpoints)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error during API scraping: {e}")
            raise

if __name__ == "__main__":
    scraper = SportyBetAPIecraper()
    scraper.run()