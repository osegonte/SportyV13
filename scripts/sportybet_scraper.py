#!/usr/bin/env python3
"""
SportyBet Scraper - Stage 3 Clean Version
Ready for login issue resolution and proper implementation
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
        
    def inspect_page_structure(self, url, save_name):
        """Inspect page structure for development"""
        try:
            self.logger.info(f"🔍 Inspecting: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save HTML for analysis
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            html_file = temp_dir / f"{save_name}_{datetime.now().strftime('%H%M%S')}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.logger.info(f"📄 Page saved to: {html_file}")
            self.logger.info(f"📏 Page size: {len(response.text):,} characters")
            
            # Quick analysis
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.info(f"📊 Page analysis:")
            self.logger.info(f"  • Title: {soup.title.string if soup.title else 'No title'}")
            self.logger.info(f"  • Scripts: {len(soup.find_all('script'))}")
            self.logger.info(f"  • Total elements: {len(soup.find_all())}")
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"❌ Error inspecting {url}: {e}")
            return None
        
    def parse_matches(self, html_content, source="unknown"):
        """Parse match data from HTML - PLACEHOLDER FOR IMPLEMENTATION"""
        soup = BeautifulSoup(html_content, 'html.parser')
        matches = []
        
        self.logger.info(f"🔍 Analyzing {source} page structure...")
        
        # Check if this is the SPA loading page
        app_div = soup.find('div', {'id': 'app'})
        if app_div and 'logoLoading' in str(soup):
            self.logger.warning(f"⚠️ {source} is loading page, content is rendered by JavaScript")
            self.logger.info("💡 This confirms SportyBet uses a Single Page Application (SPA)")
            self.logger.info("🎯 Next step: Use Selenium or API endpoints for dynamic content")
            return matches
        
        # Look for potential match containers (placeholder logic)
        potential_selectors = [
            '.match', '.game', '.fixture', '.event',
            '[class*="match"]', '[class*="game"]', '[class*="event"]',
            'tbody tr', 'li[class*="event"]'
        ]
        
        for selector in potential_selectors:
            elements = soup.select(selector)
            if elements:
                self.logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
                break
        else:
            self.logger.info(f"ℹ️ No match elements found with common selectors")
        
        return matches
        
    def scrape_upcoming_matches(self):
        """Scrape upcoming matches"""
        self.logger.info("🔍 Scraping upcoming matches...")
        
        # First inspect the page structure
        html = self.inspect_page_structure(SPORTYBET_UPCOMING_URL, "upcoming_matches")
        
        if html:
            matches = self.parse_matches(html, "upcoming")
            self.matches_data.extend(matches)
            self.logger.info(f"Found {len(matches)} upcoming matches")
            
    def scrape_live_matches(self):
        """Scrape live matches"""
        self.logger.info("🔍 Scraping live matches...")
        
        # First inspect the page structure  
        html = self.inspect_page_structure(SPORTYBET_LIVE_URL, "live_matches")
        
        if html:
            matches = self.parse_matches(html, "live")
            self.matches_data.extend(matches)
            self.logger.info(f"Found {len(matches)} live matches")
            
    def save_data(self):
        """Save scraped data to file"""
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = output_dir / f"sportybet_stage3_{timestamp}.json"
        
        # Create summary report
        report = {
            'timestamp': timestamp,
            'status': 'analysis_complete',
            'findings': {
                'sportybet_is_spa': True,
                'requires_javascript': True,
                'recommended_approach': 'selenium_or_api',
                'matches_found': len(self.matches_data)
            },
            'matches_data': self.matches_data,
            'next_steps': [
                'Fix authentication in authenticated_scraper.py',
                'Use Selenium for dynamic content',
                'Discover API endpoints',
                'Implement proper match parsing'
            ]
        }
        
        # Save report
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"📊 Analysis report saved to {json_path}")
                
    def run(self):
        """Main scraping method"""
        self.logger.info("🚀 Starting SportyBet Stage 3 Analysis...")
        
        try:
            # Analyze both page types
            self.scrape_upcoming_matches()
            self.scrape_live_matches()
            
            # Save analysis report
            self.save_data()
            
            self.logger.info("✅ Stage 3 analysis completed!")
            self.logger.info("🎯 Ready for authentication fix and dynamic content handling")
            
        except Exception as e:
            self.logger.error(f"❌ Error during analysis: {e}")
            raise

if __name__ == "__main__":
    scraper = SportyBetScraper()
    scraper.run()
