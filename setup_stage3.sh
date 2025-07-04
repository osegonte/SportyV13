#!/bin/bash

# Setup Stage 3: SportyBet Scraper Implementation
# This script sets up the environment and creates the basic scraper structure

echo "🚀 Setting up Stage 3: SportyBet Scraper..."

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run setup_sportybet_scraper.sh first"
    exit 1
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs
mkdir -p temp

# Create log file with timestamp
LOG_FILE="logs/scraper_$(date +%Y%m%d_%H%M%S).log"
touch "$LOG_FILE"

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "import requests, bs4, pandas, selenium; print('✅ All dependencies are installed')" 2>/dev/null || {
    echo "❌ Some dependencies are missing. Installing..."
    pip install -r requirements.txt
}

# Create a test configuration file
echo "⚙️ Creating test configuration..."
cat > config/test_settings.py << 'EOF'
# Test configuration for SportyBet scraper
import os
from datetime import datetime

# Test mode settings
TEST_MODE = True
MAX_PAGES_TO_SCRAPE = 2  # Limit for testing
DELAY_BETWEEN_REQUESTS = 2  # seconds
VERBOSE_LOGGING = True

# Test URLs (start with these)
TEST_URLS = [
    "https://sportybet.com/ng/sport/football/sr:category:1/today",
    "https://sportybet.com/ng/sport/football/sr:category:1/live"
]

# Output file for test run
TEST_OUTPUT_FILE = f"data/raw/test_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Log file for this session
LOG_FILE = f"logs/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
EOF

# Create a basic scraper template
echo "📄 Creating scraper template..."
cat > scripts/sportybet_scraper.py << 'EOF'
#!/usr/bin/env python3
"""
SportyBet Scraper - Stage 3 Implementation
This script scrapes match data from SportyBet Nigeria
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
    from test_settings import TEST_MODE, MAX_PAGES_TO_SCRAPE, DELAY_BETWEEN_REQUESTS, TEST_OUTPUT_FILE, LOG_FILE
except ImportError as e:
    print(f"❌ Error importing settings: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

class SportyBetScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setup_logging()
        self.matches_data = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
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
        
        # TODO: Implement actual parsing logic
        # This is a placeholder structure
        matches = []
        
        self.logger.info("Parsing matches from HTML...")
        # Add your parsing logic here
        
        return matches
        
    def scrape_upcoming_matches(self):
        """Scrape upcoming matches"""
        self.logger.info("Scraping upcoming matches...")
        html = self.fetch_page(SPORTYBET_UPCOMING_URL)
        
        if html:
            matches = self.parse_matches(html)
            self.matches_data.extend(matches)
            
        if TEST_MODE:
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
    def scrape_live_matches(self):
        """Scrape live matches"""
        self.logger.info("Scraping live matches...")
        html = self.fetch_page(SPORTYBET_LIVE_URL)
        
        if html:
            matches = self.parse_matches(html)
            self.matches_data.extend(matches)
            
    def save_data(self):
        """Save scraped data to file"""
        if not self.matches_data:
            self.logger.warning("No data to save")
            return
            
        # Create output directory if it doesn't exist
        output_path = Path(TEST_OUTPUT_FILE)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.matches_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Data saved to {output_path}")
        
        # Also save as CSV if we have data
        if self.matches_data:
            try:
                df = pd.DataFrame(self.matches_data)
                csv_path = output_path.with_suffix('.csv')
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
            
            self.logger.info("✅ Scraping completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Error during scraping: {e}")
            raise

if __name__ == "__main__":
    scraper = SportyBetScraper()
    scraper.run()
EOF

# Make scripts executable
chmod +x scripts/sportybet_scraper.py

# Create a test runner script
echo "🧪 Creating test runner..."
cat > test_scraper.sh << 'EOF'
#!/bin/bash

# Test the SportyBet scraper
echo "🧪 Testing SportyBet Scraper..."

# Activate virtual environment
source venv/bin/activate

# Run the scraper in test mode
python scripts/sportybet_scraper.py

# Check if output files were created
if [ -f "data/raw/test_scrape_"*.json ]; then
    echo "✅ Test completed! Check data/raw/ for output files"
    echo "📊 Latest files:"
    ls -la data/raw/test_scrape_* | tail -5
else
    echo "❌ No output files found. Check logs/ for error details"
fi

# Show recent log entries
echo "📋 Recent log entries:"
tail -10 logs/scraper_*.log | tail -10
EOF

chmod +x test_scraper.sh

# Create a development helper script
echo "🛠️ Creating development helper..."
cat > dev_scraper.sh << 'EOF'
#!/bin/bash

# Development helper for SportyBet scraper
echo "🛠️ SportyBet Scraper Development Helper"

# Activate virtual environment
source venv/bin/activate

case "$1" in
    "test")
        echo "Running test scraper..."
        ./test_scraper.sh
        ;;
    "debug")
        echo "Running scraper with debug output..."
        python -u scripts/sportybet_scraper.py | tee logs/debug_$(date +%Y%m%d_%H%M%S).log
        ;;
    "clean")
        echo "Cleaning up test files..."
        rm -f data/raw/test_scrape_*.json
        rm -f data/raw/test_scrape_*.csv
        rm -f logs/scraper_*.log
        echo "✅ Cleanup complete"
        ;;
    "inspect")
        echo "Inspecting latest output..."
        LATEST_JSON=$(ls -t data/raw/test_scrape_*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_JSON" ]; then
            echo "📄 Latest file: $LATEST_JSON"
            python -c "import json; print(json.dumps(json.load(open('$LATEST_JSON')), indent=2)[:500])..."
        else
            echo "❌ No output files found"
        fi
        ;;
    *)
        echo "Usage: $0 {test|debug|clean|inspect}"
        echo "  test    - Run the scraper in test mode"
        echo "  debug   - Run with debug output"
        echo "  clean   - Clean up test files"
        echo "  inspect - Inspect latest output"
        ;;
esac
EOF

chmod +x dev_scraper.sh

# Create a simple HTML inspector for debugging
echo "🔍 Creating HTML inspector..."
cat > inspect_html.py << 'EOF'
#!/usr/bin/env python3
"""
HTML Inspector for SportyBet pages
Use this to examine the HTML structure before implementing parsing
"""

import requests
from bs4 import BeautifulSoup
import sys
import os

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    from settings import HEADERS, SPORTYBET_UPCOMING_URL
except ImportError:
    print("Using default headers")
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    SPORTYBET_UPCOMING_URL = "https://sportybet.com/ng/sport/football/sr:category:1/today"

def inspect_page(url):
    """Download and inspect page structure"""
    print(f"🔍 Inspecting: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save full HTML for manual inspection
        with open('temp/page_source.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("✅ Page downloaded successfully")
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"📏 Page size: {len(response.text)} characters")
        print(f"🏗️ HTML saved to: temp/page_source.html")
        
        # Look for common match-related elements
        print("\n🔍 Looking for match elements...")
        
        # Common selectors to try
        selectors = [
            '.match', '.game', '.fixture', '.event',
            '[class*="match"]', '[class*="game"]', '[class*="fixture"]',
            '[data-match]', '[data-game]', '[data-fixture]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                if len(elements) <= 5:
                    for i, elem in enumerate(elements):
                        print(f"  Element {i+1}: {elem.get('class', [])} - {elem.get_text()[:100]}...")
                break
        else:
            print("❌ No obvious match elements found. Manual inspection needed.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_page(SPORTYBET_UPCOMING_URL)
EOF

chmod +x inspect_html.py

echo "✅ Stage 3 setup complete!"
echo ""
echo "📋 What was created:"
echo "  • config/test_settings.py - Test configuration"
echo "  • scripts/sportybet_scraper.py - Main scraper (template)"
echo "  • test_scraper.sh - Test the scraper"
echo "  • dev_scraper.sh - Development helper"
echo "  • inspect_html.py - HTML structure inspector"
echo ""
echo "🚀 Next steps:"
echo "  1. Run: ./test_scraper.sh (test current template)"
echo "  2. Run: python inspect_html.py (inspect HTML structure)"
echo "  3. Edit scripts/sportybet_scraper.py to add parsing logic"
echo "  4. Use: ./dev_scraper.sh test (test your changes)"
echo ""
echo "🛠️ Development workflow:"
echo "  ./dev_scraper.sh test    - Test the scraper"
echo "  ./dev_scraper.sh debug   - Debug mode"
echo "  ./dev_scraper.sh clean   - Clean test files"
echo "  ./dev_scraper.sh inspect - Inspect output"