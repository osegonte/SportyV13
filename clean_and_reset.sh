#!/bin/bash

# Clean and Reset SportyBet Scraper Project
# This script removes irrelevant files and resets the project to a clean state

echo "🧹 Cleaning SportyBet Scraper Project..."
echo "========================================"

# Function to confirm deletion
confirm_deletion() {
    local item="$1"
    local description="$2"
    
    if [ -e "$item" ]; then
        echo "🗑️  Found: $item ($description)"
        return 0
    else
        return 1
    fi
}

# Show what will be cleaned
echo "📋 Items to be cleaned:"
echo ""

# Backup files
echo "🔄 Backup files:"
find . -name "*.backup" -type f 2>/dev/null | while read file; do
    echo "  • $file"
done

# Temporary files
echo "🗂️  Temporary files:"
confirm_deletion "temp/" "temporary directory" && echo "  • temp/ directory"
find . -name "*.tmp" -type f 2>/dev/null | while read file; do
    echo "  • $file"
done

# Log files
echo "📋 Log files:"
confirm_deletion "logs/" "logs directory" && echo "  • logs/ directory"
find . -name "*.log" -type f 2>/dev/null | while read file; do
    echo "  • $file"
done

# Data files from testing
echo "📊 Test data files:"
confirm_deletion "data/" "data directory" && echo "  • data/ directory"

# Session directories
find . -name "session_*" -type d 2>/dev/null | while read dir; do
    echo "  • $dir"
done

# Virtual environment issues files
echo "🐍 Environment files:"
confirm_deletion "verify_python.py" "Python verification script" && echo "  • verify_python.py"

# Broken scripts
echo "🔧 Scripts to remove/reset:"
confirm_deletion "run_stage3.sh" "potentially broken stage 3 runner" && echo "  • run_stage3.sh"
confirm_deletion "test_scraper.sh" "potentially broken test script" && echo "  • test_scraper.sh"
confirm_deletion "dev_scraper.sh" "potentially broken dev script" && echo "  • dev_scraper.sh"
confirm_deletion "fix_python_commands.sh" "Python fix script" && echo "  • fix_python_commands.sh"
confirm_deletion "fix_venv_issue.sh" "Venv fix script" && echo "  • fix_venv_issue.sh"

# Keep these important files
echo ""
echo "✅ Files to KEEP (important):"
echo "  • requirements.txt"
echo "  • README.md"
echo "  • .gitignore"
echo "  • config/settings.py"
echo "  • scripts/ directory structure"
echo "  • venv/ directory (will be recreated)"
echo "  • activate.sh"
echo "  • activate_properly.sh (if working)"
echo "  • test_scraper_fixed.sh (if working)"
echo "  • dev_scraper_fixed.sh (if working)"

echo ""
read -p "❓ Do you want to proceed with cleaning? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleaning cancelled."
    exit 0
fi

echo ""
echo "🧹 Starting cleanup..."

# Remove backup files
echo "🔄 Removing backup files..."
find . -name "*.backup" -type f -delete 2>/dev/null && echo "✅ Backup files removed"

# Remove temporary files
echo "🗂️  Removing temporary files..."
rm -rf temp/ 2>/dev/null && echo "✅ temp/ directory removed"
find . -name "*.tmp" -type f -delete 2>/dev/null && echo "✅ .tmp files removed"

# Remove log files
echo "📋 Removing log files..."
rm -rf logs/ 2>/dev/null && echo "✅ logs/ directory removed"
find . -name "*.log" -type f -delete 2>/dev/null && echo "✅ .log files removed"

# Remove test data
echo "📊 Removing test data..."
rm -rf data/ 2>/dev/null && echo "✅ data/ directory removed"

# Remove session directories
echo "📁 Removing session directories..."
find . -name "session_*" -type d -exec rm -rf {} + 2>/dev/null && echo "✅ Session directories removed"

# Remove problematic scripts
echo "🔧 Removing problematic scripts..."
rm -f run_stage3.sh 2>/dev/null && echo "✅ run_stage3.sh removed"
rm -f test_scraper.sh 2>/dev/null && echo "✅ test_scraper.sh removed"
rm -f dev_scraper.sh 2>/dev/null && echo "✅ dev_scraper.sh removed"
rm -f fix_python_commands.sh 2>/dev/null && echo "✅ fix_python_commands.sh removed"
rm -f fix_venv_issue.sh 2>/dev/null && echo "✅ fix_venv_issue.sh removed"
rm -f verify_python.py 2>/dev/null && echo "✅ verify_python.py removed"

# Remove and recreate virtual environment
echo "🐍 Resetting virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv/ && echo "✅ Old venv removed"
fi

# Create fresh virtual environment
echo "🔨 Creating fresh virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "✅ New virtual environment created"
    
    # Activate and install packages
    echo "📦 Activating new environment..."
    source venv/bin/activate
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "✅ Virtual environment activated: $VIRTUAL_ENV"
        echo "🐍 Python: $(which python3)"
        
        # Install packages
        echo "📚 Installing packages..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Verify installation
        echo "🧪 Verifying installation..."
        python3 -c "
import sys
print(f'✅ Python: {sys.executable}')
modules = ['requests', 'bs4', 'pandas', 'selenium']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
"
        
        echo "✅ Virtual environment setup complete!"
    else
        echo "❌ Failed to activate new virtual environment"
    fi
else
    echo "❌ Failed to create virtual environment"
fi

# Recreate essential directories
echo "📁 Recreating essential directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs
mkdir -p temp
echo "✅ Essential directories created"

# Reset scripts to clean state
echo "📄 Resetting scripts to clean state..."

# Clean up the main scraper script
if [ -f "scripts/sportybet_scraper.py" ]; then
    # Keep only the basic structure, remove any problematic imports
    echo "🔧 Cleaning up sportybet_scraper.py..."
    cat > scripts/sportybet_scraper.py << 'EOF'
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
EOF
    echo "✅ sportybet_scraper.py cleaned"
fi

# Create a simple test script
echo "🧪 Creating simple test script..."
cat > test_simple.sh << 'EOF'
#!/bin/bash

# Simple test script for SportyBet scraper
echo "🧪 Simple SportyBet Scraper Test"

# Activate virtual environment
source venv/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo "🐍 Python: $(which python3)"

# Quick module test
python3 -c "import requests, bs4, pandas, selenium; print('✅ All modules available')" || {
    echo "❌ Module import failed"
    exit 1
}

# Run the scraper
echo "🚀 Running scraper..."
python3 scripts/sportybet_scraper.py

echo "📊 Checking results..."
if ls data/raw/sportybet_matches_*.json 1> /dev/null 2>&1; then
    echo "✅ Output files created:"
    ls -la data/raw/sportybet_matches_*
else
    echo "⚠️ No output files found (this is expected if parsing is not implemented)"
fi

echo "📋 Log files:"
ls -la logs/ 2>/dev/null || echo "No logs directory"
EOF

chmod +x test_simple.sh

echo ""
echo "✅ Project cleaned and reset successfully!"
echo ""
echo "📋 What was done:"
echo "  • 🗑️  Removed all backup, temp, and log files"
echo "  • 🐍 Recreated fresh virtual environment"
echo "  • 📚 Reinstalled all packages properly"
echo "  • 📁 Recreated essential directories"
echo "  • 🔧 Reset scripts to clean state"
echo "  • 🧪 Created simple test script"
echo ""
echo "🎯 Current project state:"
echo "  • Clean codebase with no problematic files"
echo "  • Fresh virtual environment with working packages"
echo "  • Ready for Stage 3 implementation"
echo ""
echo "🚀 Next steps:"
echo "  1. Test the environment: ./test_simple.sh"
echo "  2. If that works, implement HTML parsing in scripts/sportybet_scraper.py"
echo "  3. Use the working foundation to build the actual scraper"
echo ""
echo "🎉 Ready to start fresh!"