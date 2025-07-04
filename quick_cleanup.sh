#!/bin/bash

# Quick Cleanup - Remove Irrelevant Files
echo "🧹 Quick SportyBet Project Cleanup"
echo "=================================="

# Remove debug and temporary files
echo "🗑️  Removing debug files..."
rm -f temp/login_page_*.html
rm -f temp/source_*.html
rm -f temp/auth_source_*.html
rm -f temp/debug_selenium_*.html

# Remove old log files (keep only the latest)
echo "📋 Cleaning old log files..."
find logs -name "*.log" -type f | sort | head -n -2 | xargs rm -f

# Remove old data files from failed attempts
echo "📊 Removing empty/failed data files..."
find data/raw -name "*.json" -size 0 -delete
find data/raw -name "*.csv" -size 0 -delete

# Remove session files
echo "🍪 Removing session files..."
rm -f temp/sportybet_session.json

# Clean up any backup files
echo "🔄 Removing backup files..."
find . -name "*.backup" -delete

echo "✅ Quick cleanup completed!"
echo ""
echo "📁 Current project structure:"
echo "  ├── scripts/sportybet_scraper.py (basic)"
echo "  ├── scripts/authenticated_scraper.py (auth)"
echo "  ├── scripts/api_scraper.py (api discovery)"
echo "  ├── test_simple.sh (basic test)"
echo "  ├── test_auth_scraper.sh (auth test)"
echo "  └── config/settings.py (configuration)"
echo ""
echo "🎯 Ready for next phase!"