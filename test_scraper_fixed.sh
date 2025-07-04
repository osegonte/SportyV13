#!/bin/bash

# Fixed test runner for SportyBet scraper
echo "🧪 Testing SportyBet Scraper (Fixed Version)..."

# Check if we're in the right directory
if [ ! -f "scripts/sportybet_scraper.py" ]; then
    echo "❌ Please run from project root directory"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Verify Python3 works
echo "🔍 Verifying Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found!"
    exit 1
fi

echo "✅ Python3 version: $(python3 --version)"

# Run the scraper with proper error handling
echo "🚀 Running scraper..."
if python3 scripts/sportybet_scraper.py; then
    echo "✅ Scraper completed"
else
    echo "❌ Scraper failed with exit code: $?"
    echo "📋 Check logs for details:"
    find logs -name "*.log" -type f -exec tail -5 {} \; 2>/dev/null || echo "No logs found"
fi

# Check for output files
echo "📊 Checking output files..."
OUTPUT_FILES=$(find data/raw -name "test_scrape_*.json" -type f 2>/dev/null)

if [ -n "$OUTPUT_FILES" ]; then
    echo "✅ Output files created:"
    for file in $OUTPUT_FILES; do
        echo "  📄 $file ($(wc -c < "$file" 2>/dev/null || echo "0") bytes)"
    done
    
    # Show sample data from latest file
    LATEST_FILE=$(echo "$OUTPUT_FILES" | head -1)
    echo "📋 Sample from $LATEST_FILE:"
    python3 -c "
import json
try:
    with open('$LATEST_FILE', 'r') as f:
        data = json.load(f)
    print(f'Type: {type(data)}, Length: {len(data) if isinstance(data, (list, dict)) else \"N/A\"}')
    if isinstance(data, list) and data:
        print('First item:', json.dumps(data[0], indent=2)[:200], '...' if len(json.dumps(data[0], indent=2)) > 200 else '')
    elif isinstance(data, dict):
        print('Keys:', list(data.keys())[:5])
except Exception as e:
    print(f'Error reading file: {e}')
"
else
    echo "⚠️ No output files found"
    echo "This could mean:"
    echo "  • No matches were found on the website"
    echo "  • The HTML structure has changed"
    echo "  • Network connectivity issues"
    echo "  • The parsing logic needs improvement"
fi

# Show recent logs
echo "📋 Recent log entries:"
LATEST_LOG=$(find logs -name "scraper_*.log" -type f 2>/dev/null | sort | tail -1)
if [ -n "$LATEST_LOG" ]; then
    echo "Latest log: $LATEST_LOG"
    tail -10 "$LATEST_LOG"
else
    echo "No log files found"
fi
