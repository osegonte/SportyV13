#!/bin/bash

# Test the Advanced SportyBet Scraper
echo "🚀 Testing Advanced SportyBet Scraper with Selenium"
echo "=================================================="

# Activate virtual environment
source venv/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"

# Check if Chrome is available
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Google Chrome found"
elif command -v chromium >/dev/null 2>&1; then
    echo "✅ Chromium found" 
elif command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome >/dev/null 2>&1; then
    echo "✅ Google Chrome found (macOS)"
else
    echo "⚠️ Chrome not found. Selenium may not work."
    echo "💡 On macOS, install with: brew install --cask google-chrome"
    echo "💡 On Ubuntu: sudo apt install google-chrome-stable"
    echo "📋 Will try anyway, or use --no-selenium flag"
fi

# Test with Selenium first
echo ""
echo "🧪 Test 1: Using Selenium (headless)"
echo "======================================"
python3 scripts/advanced_scraper.py

echo ""
echo "📊 Checking results..."
if ls data/raw/sportybet_selenium_*.json 1> /dev/null 2>&1; then
    echo "✅ Selenium output files created:"
    for file in data/raw/sportybet_selenium_*.json; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes)"
        
        # Show sample content
        echo "📋 Sample content:"
        python3 -c "
import json
try:
    with open('$file', 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        print(f'  📊 Found {len(data)} items')
        if data:
            print('  📄 First item:')
            item = data[0]
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + '...'
                print(f'    {key}: {value}')
        else:
            print('  📄 Empty array')
    else:
        print(f'  📊 Data type: {type(data)}')
except Exception as e:
    print(f'  ❌ Error reading file: {e}')
"
    done
else
    echo "⚠️ No Selenium output files found"
fi

# Test without Selenium as comparison
echo ""
echo "🧪 Test 2: Without Selenium (requests only)"
echo "==========================================="
python3 scripts/advanced_scraper.py --no-selenium

# Show logs
echo ""
echo "📋 Recent log entries:"
LATEST_LOG=$(find logs -name "advanced_scraper_*.log" -type f 2>/dev/null | sort | tail -1)
if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
    echo "📄 Latest log: $LATEST_LOG"
    echo "----------------------------------------"
    tail -15 "$LATEST_LOG"
    echo "----------------------------------------"
else
    echo "⚠️ No log files found"
fi

# Show HTML debug files if any
echo ""
echo "🔍 Debug files created:"
if ls temp/debug_selenium_*.html 1> /dev/null 2>&1; then
    for file in temp/debug_selenium_*.html; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  🔍 $file ($SIZE bytes) - actual HTML content loaded by Selenium"
    done
    echo "💡 You can open these HTML files in a browser to see what Selenium captured"
else
    echo "  No debug HTML files found"
fi

echo ""
echo "🎯 Summary:"
echo "  📊 Check data/raw/ for output files"
echo "  📋 Check logs/ for detailed logs"
echo "  🔍 Check temp/ for debug HTML files"
echo ""
echo "💡 Next steps:"
echo "  1. If Selenium found matches → great! Review the data structure"
echo "  2. If no matches found → the site might use AJAX/API calls"
echo "  3. Check browser developer tools on sportybet.com to see how data loads"
echo "  4. Consider using browser automation to wait for specific elements"

echo ""
echo "🎉 Advanced scraper test completed!"