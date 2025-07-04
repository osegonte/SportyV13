#!/usr/bin/env python3
"""
Advanced SportyBet Scraper using Selenium
This handles JavaScript-heavy pages that load content dynamically
"""

import requests
import json
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from settings import HEADERS, SPORTYBET_BASE_URL, SPORTYBET_LIVE_URL, SPORTYBET_UPCOMING_URL
except ImportError as e:
    print(f"❌ Error importing settings: {e}")
    print("Using default settings...")
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    SPORTYBET_UPCOMING_URL = "https://sportybet.com/ng/sport/football/sr:category:1/today"
    SPORTYBET_LIVE_URL = "https://sportybet.com/ng/sport/football/sr:category:1/live"

class AdvancedSportyBetScraper:
    def __init__(self, use_selenium=True, headless=True):
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setup_logging()
        self.matches_data = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        Path("logs").mkdir(exist_ok=True)
        log_file = f"logs/advanced_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
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
        """Setup Selenium WebDriver"""
        if self.driver:
            return True
            
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={HEADERS['User-Agent']}")
            
            # Try to use system Chrome first
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.logger.info("✅ Chrome WebDriver initialized")
                return True
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Chrome: {e}")
                self.logger.info("💡 Make sure Chrome is installed. On macOS: brew install --cask google-chrome")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up Selenium: {e}")
            return False
    
    def wait_for_content(self, url, timeout=30):
        """Wait for dynamic content to load"""
        if not self.driver:
            return None
            
        try:
            self.logger.info(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for the main app container
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "app"))
            )
            
            # Wait a bit more for dynamic content
            time.sleep(5)
            
            # Try to find common match-related elements
            potential_selectors = [
                "[class*='match']",
                "[class*='event']", 
                "[class*='fixture']",
                "[class*='game']",
                "[class*='sport']",
                "[class*='team']",
                "[class*='odds']",
                "tbody tr",  # Table rows
                ".market",
                ".bet-item"
            ]
            
            for selector in potential_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
                        # Log sample content
                        for i, elem in enumerate(elements[:3]):
                            try:
                                text = elem.text[:100] if elem.text else elem.get_attribute('innerHTML')[:100]
                                self.logger.info(f"  Sample {i+1}: {text}...")
                            except:
                                pass
                        break
                except:
                    continue
            
            return self.driver.page_source
            
        except TimeoutException:
            self.logger.error(f"❌ Timeout waiting for page to load: {url}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error loading page: {e}")
            return None
    
    def fetch_page_selenium(self, url):
        """Fetch page using Selenium for JavaScript content"""
        if not self.setup_selenium():
            self.logger.error("❌ Cannot use Selenium, falling back to requests")
            return self.fetch_page_requests(url)
            
        return self.wait_for_content(url)
    
    def fetch_page_requests(self, url):
        """Fetch page using requests (for comparison)"""
        try:
            self.logger.info(f"Fetching with requests: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_matches_selenium(self, html_content):
        """Parse matches from Selenium-rendered HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        matches = []
        
        self.logger.info("Parsing matches from Selenium HTML...")
        
        # Try different selectors based on common sports betting patterns
        selectors_to_try = [
            # Table-based layouts
            ("tbody tr", "table rows"),
            ("tr[class*='match']", "match table rows"),
            ("tr[class*='event']", "event table rows"),
            
            # Div-based layouts
            ("div[class*='match']", "match divs"),
            ("div[class*='event']", "event divs"), 
            ("div[class*='fixture']", "fixture divs"),
            ("div[class*='game']", "game divs"),
            
            # List-based layouts
            ("li[class*='match']", "match list items"),
            ("li[class*='event']", "event list items"),
            
            # Generic containers
            ("[data-match]", "data-match elements"),
            ("[data-event]", "data-event elements"),
            ("[data-fixture]", "data-fixture elements"),
        ]
        
        for selector, description in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                self.logger.info(f"✅ Found {len(elements)} {description}")
                
                for i, element in enumerate(elements):
                    try:
                        match_data = self.extract_match_data(element, i)
                        if match_data:
                            matches.append(match_data)
                    except Exception as e:
                        self.logger.error(f"Error parsing match {i}: {e}")
                        
                break  # Use first successful selector
        
        if not matches:
            self.logger.warning("No matches found with any selector")
            # Save HTML for manual inspection
            debug_file = Path("temp") / f"debug_selenium_{datetime.now().strftime('%H%M%S')}.html"
            debug_file.parent.mkdir(exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"🔍 Selenium HTML saved to: {debug_file}")
            
        return matches
    
    def extract_match_data(self, element, index):
        """Extract match data from an element"""
        try:
            # Try to extract team names, odds, time, etc.
            text = element.get_text(strip=True)
            
            # Look for team names (common patterns)
            team_patterns = ['vs', 'v.', ' - ', ' x ', ' : ']
            teams = None
            for pattern in team_patterns:
                if pattern in text.lower():
                    parts = text.split(pattern, 1)
                    if len(parts) == 2:
                        teams = [parts[0].strip(), parts[1].strip()]
                        break
            
            # Extract any numeric values (potential odds)
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            
            match_data = {
                'index': index,
                'raw_text': text[:200],  # Limit length
                'element_tag': element.name,
                'element_classes': element.get('class', []),
                'teams': teams,
                'potential_odds': numbers[:10],  # Limit to first 10 numbers
                'scraped_at': datetime.now().isoformat()
            }
            
            # Only return if we found something meaningful
            if teams or len(numbers) >= 2:
                return match_data
                
        except Exception as e:
            self.logger.error(f"Error extracting match data: {e}")
            
        return None
    
    def parse_matches_requests(self, html_content):
        """Parse matches from requests HTML (minimal content)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        self.logger.info("Parsing matches from requests HTML...")
        
        # For requests-based content, look for initial data or config
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('match' in script.string.lower() or 'event' in script.string.lower()):
                self.logger.info("Found potential match data in script tag")
                # You could try to parse JavaScript variables here
                
        return []  # Requests likely won't find dynamic content
    
    def scrape_page(self, url, page_type):
        """Scrape a single page"""
        self.logger.info(f"Scraping {page_type} from: {url}")
        
        # Try Selenium first for dynamic content
        if self.use_selenium:
            html = self.fetch_page_selenium(url)
            if html:
                matches = self.parse_matches_selenium(html)
                self.logger.info(f"Found {len(matches)} matches using Selenium")
                return matches
        
        # Fallback to requests
        html = self.fetch_page_requests(url)
        if html:
            matches = self.parse_matches_requests(html)
            self.logger.info(f"Found {len(matches)} matches using requests")
            return matches
            
        return []
    
    def save_data(self):
        """Save scraped data to file"""
        if not self.matches_data:
            self.logger.warning("No data to save")
            return
            
        # Create output directory
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = output_dir / f"sportybet_selenium_{timestamp}.json"
        
        # Save as JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.matches_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Data saved to {json_path}")
        
        # Also save as CSV if we have structured data
        if self.matches_data:
            try:
                df = pd.DataFrame(self.matches_data)
                csv_path = json_path.with_suffix('.csv')
                df.to_csv(csv_path, index=False)
                self.logger.info(f"CSV saved to {csv_path}")
            except Exception as e:
                self.logger.error(f"Error saving CSV: {e}")
    
    def run(self):
        """Main scraping method"""
        self.logger.info("🚀 Starting Advanced SportyBet scraper...")
        
        try:
            # Scrape upcoming matches
            upcoming_matches = self.scrape_page(SPORTYBET_UPCOMING_URL, "upcoming matches")
            self.matches_data.extend(upcoming_matches)
            
            # Scrape live matches
            live_matches = self.scrape_page(SPORTYBET_LIVE_URL, "live matches")
            self.matches_data.extend(live_matches)
            
            # Save all data
            self.save_data()
            
            self.logger.info(f"✅ Scraping completed! Total matches: {len(self.matches_data)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error during scraping: {e}")
            raise
        finally:
            # Clean up Selenium
            if self.driver:
                self.driver.quit()
                self.logger.info("🔧 WebDriver closed")

def main():
    """Main function with options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced SportyBet Scraper')
    parser.add_argument('--no-selenium', action='store_true', help='Use only requests (no Selenium)')
    parser.add_argument('--no-headless', action='store_true', help='Show browser window (not headless)')
    
    args = parser.parse_args()
    
    use_selenium = not args.no_selenium
    headless = not args.no_headless
    
    scraper = AdvancedSportyBetScraper(use_selenium=use_selenium, headless=headless)
    scraper.run()

if __name__ == "__main__":
    main()