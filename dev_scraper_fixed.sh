#!/bin/bash

# Fixed development helper for SportyBet scraper
echo "🛠️ SportyBet Scraper Development Helper (Fixed)"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

case "$1" in
    "test")
        echo "Running test scraper..."
        ./test_scraper_fixed.sh
        ;;
    "debug")
        echo "Running scraper with debug output..."
        python3 -u scripts/sportybet_scraper.py | tee logs/debug_$(date +%Y%m%d_%H%M%S).log
        ;;
    "clean")
        echo "Cleaning up test files..."
        rm -f data/raw/test_scrape_*.json
        rm -f data/raw/test_scrape_*.csv
        rm -f logs/scraper_*.log
        rm -f logs/debug_*.log
        echo "✅ Cleanup complete"
        ;;
    "inspect")
        echo "Inspecting latest output..."
        LATEST_JSON=$(ls -t data/raw/test_scrape_*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_JSON" ]; then
            echo "📄 Latest file: $LATEST_JSON"
            echo "📊 File size: $(wc -c < "$LATEST_JSON") bytes"
            echo "📋 Content preview:"
            python3 -c "
import json
try:
    with open('$LATEST_JSON', 'r') as f:
        data = json.load(f)
    print(json.dumps(data, indent=2)[:500])
    if len(json.dumps(data, indent=2)) > 500:
        print('...')
except Exception as e:
    print(f'Error: {e}')
"
        else
            echo "❌ No output files found"
        fi
        ;;
    "html")
        echo "Inspecting HTML structure..."
        python3 inspect_html.py
        ;;
    "verify")
        echo "Verifying Python environment..."
        python3 verify_python.py
        ;;
    *)
        echo "Usage: $0 {test|debug|clean|inspect|html|verify}"
        echo "  test    - Run the scraper in test mode"
        echo "  debug   - Run with debug output"
        echo "  clean   - Clean up test files"
        echo "  inspect - Inspect latest output"
        echo "  html    - Inspect HTML structure"
        echo "  verify  - Verify Python environment"
        ;;
esac
