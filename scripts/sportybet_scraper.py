#!/usr/bin/env python3
"""
SportyBet Scraper - Clean Version
Ready for implementation
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

class SportyBetScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setup_logging()
        self.matches_data = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        log_file = f"logs/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def fetch_page(self, url):
        """Fetch a page with error handling"""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
            
    def parse_matches(self, html_content):
        """Parse match data from HTML - TO BE IMPLEMENTED"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        self.logger.info("Parsing matches from HTML...")
        
        # TODO: Implement actual parsing logic
        # This is a placeholder
        matches = []
        
        # Example structure for match data:
        # match = {
        #     'home_team': 'Team A',
        #     'away_team': 'Team B',
        #     'match_time': '2025-07-04 15:00',
        #     'odds': {'1': 1.50, 'X': 3.20, '2': 6.00},
        #     'competition': 'Premier League'
        # }
        
        return matches
        
    def scrape_upcoming_matches(self):
        """Scrape upcoming matches"""
        self.logger.info("Scraping upcoming matches...")
        html = self.fetch_page(SPORTYBET_UPCOMING_URL)
        
        if html:
            matches = self.parse_matches(html)
            self.matches_data.extend(matches)
            self.logger.info(f"Found {len(matches)} upcoming matches")
            
    def scrape_live_matches(self):
        """Scrape live matches"""
        self.logger.info("Scraping live matches...")
        html = self.fetch_page(SPORTYBET_LIVE_URL)
        
        if html:
            matches = self.parse_matches(html)
            self.matches_data.extend(matches)
            self.logger.info(f"Found {len(matches)} live matches")
            
    def save_data(self):
        """Save scraped data to file"""
        if not self.matches_data:
            self.logger.warning("No data to save")
            return
            
        # Create output directory
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = output_dir / f"sportybet_matches_{timestamp}.json"
        
        # Save as JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.matches_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Data saved to {json_path}")
        
        # Also save as CSV if we have data
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
        self.logger.info("🚀 Starting SportyBet scraper...")
        
        try:
            # Scrape upcoming matches
            self.scrape_upcoming_matches()
            
            # Scrape live matches  
            self.scrape_live_matches()
            
            # Save all data
            self.save_data()
            
            self.logger.info(f"✅ Scraping completed! Total matches: {len(self.matches_data)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error during scraping: {e}")
            raise

if __name__ == "__main__":
    scraper = SportyBetScraper()
    scraper.run()
