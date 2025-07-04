#!/bin/bash

# Test the SportyBet API Scraper
echo "🚀 Testing SportyBet API Scraper"
echo "================================"

# Activate virtual environment
source venv/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"

# Check Chrome availability
if command -v google-chrome >/dev/null 2>&1 || command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome >/dev/null 2>&1; then
    echo "✅ Chrome available for network interception"
else
    echo "⚠️ Chrome not found - will skip network interception"
fi

echo ""
echo "🔍 Running API Discovery and Scraping..."
echo "========================================"

# Run the API scraper
python3 scripts/api_scraper.py

echo ""
echo "📊 Checking Results..."
echo "====================="

# Check for matches data
if ls data/raw/sportybet_api_matches_*.json 1> /dev/null 2>&1; then
    echo "✅ Match data files found:"
    for file in data/raw/sportybet_api_matches_*.json; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes)"
        
        # Show sample content
        echo "📋 Sample matches:"
        python3 -c "
import json
try:
    with open('$file', 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        print(f'  📊 Total matches: {len(data)}')
        for i, match in enumerate(data[:3]):  # Show first 3
            print(f'  🏈 Match {i+1}:')
            for key, value in match.items():
                if isinstance(value, str) and len(value) > 60:
                    value = value[:60] + '...'
                print(f'    {key}: {value}')
            print()
    else:
        print(f'  📊 Data type: {type(data)}')
        if isinstance(data, dict):
            print(f'  🔑 Keys: {list(data.keys())[:5]}')
except Exception as e:
    print(f'  ❌ Error reading matches: {e}')
"
    done
else
    echo "⚠️ No match data files found"
fi

# Check for API endpoints data
if ls data/raw/sportybet_api_endpoints_*.json 1> /dev/null 2>&1; then
    echo ""
    echo "✅ API endpoint data found:"
    for file in data/raw/sportybet_api_endpoints_*.json; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes)"
        
        # Show API endpoints
        echo "🔗 Discovered API endpoints:"
        python3 -c "
import json
try:
    with open('$file', 'r') as f:
        endpoints = json.load(f)
    if isinstance(endpoints, list):
        print(f'  📊 Total endpoints: {len(endpoints)}')
        for i, endpoint in enumerate(endpoints):
            print(f'  🌐 Endpoint {i+1}:')
            print(f'    URL: {endpoint.get(\"url\", \"N/A\")}')
            print(f'    Response size: {endpoint.get(\"response_size\", \"N/A\")} bytes')
            print(f'    Data type: {endpoint.get(\"data_type\", \"N/A\")}')
            if endpoint.get('sample_keys'):
                print(f'    Keys: {endpoint.get(\"sample_keys\", [])}')
            print()
    else:
        print(f'  📊 Data type: {type(endpoints)}')
except Exception as e:
    print(f'  ❌ Error reading endpoints: {e}')
"
    done
else
    echo "⚠️ No API endpoint data found"
fi

# Check temp files for source analysis
echo ""
echo "🔍 Source Analysis Files:"
if ls temp/source_*.html 1> /dev/null 2>&1; then
    for file in temp/source_*.html; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes) - page source for analysis"
    done
else
    echo "  No source files found"
fi

# Show recent logs
echo ""
echo "📋 Recent Log Entries:"
echo "====================="
LATEST_LOG=$(find logs -name "api_scraper_*.log" -type f 2>/dev/null | sort | tail -1)
if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
    echo "📄 Latest log: $LATEST_LOG"
    echo "----------------------------------------"
    tail -20 "$LATEST_LOG"
    echo "----------------------------------------"
else
    echo "⚠️ No log files found"
fi

echo ""
echo "🎯 Summary & Next Steps:"
echo "========================"

# Count results
MATCH_COUNT=0
ENDPOINT_COUNT=0

if ls data/raw/sportybet_api_matches_*.json 1> /dev/null 2>&1; then
    MATCH_COUNT=$(python3 -c "
import json
import glob
total = 0
for file in glob.glob('data/raw/sportybet_api_matches_*.json'):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            total += len(data)
    except: pass
print(total)
" 2>/dev/null || echo "0")
fi

if ls data/raw/sportybet_api_endpoints_*.json 1> /dev/null 2>&1; then
    ENDPOINT_COUNT=$(python3 -c "
import json
import glob
total = 0
for file in glob.glob('data/raw/sportybet_api_endpoints_*.json'):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            total += len(data)
    except: pass
print(total)
" 2>/dev/null || echo "0")
fi

echo "📊 Results:"
echo "  • Matches found: $MATCH_COUNT"
echo "  • Working API endpoints: $ENDPOINT_COUNT"

if [ "$MATCH_COUNT" -gt "0" ]; then
    echo "🎉 Success! Found match data"
    echo "💡 Next steps:"
    echo "  1. Review the match data structure"
    echo "  2. Refine the parsing logic if needed"
    echo "  3. Move to Stage 4 (Data Matching with SofaScore)"
elif [ "$ENDPOINT_COUNT" -gt "0" ]; then
    echo "🔄 Partial success! Found API endpoints but no matches"
    echo "💡 Next steps:"
    echo "  1. Review the API endpoints found"
    echo "  2. Manually test the endpoints to understand data structure"
    echo "  3. Update parsing logic based on actual API response format"
else
    echo "🔍 No direct API access found"
    echo "💡 Next steps:"
    echo "  1. SportyBet might use complex authentication or rate limiting"
    echo "  2. Consider browser developer tools to manually find endpoints"
    echo "  3. Look into their mobile app API (often less protected)"
    echo "  4. Consider alternative data sources or partnerships"
fi

echo ""
echo "🛠️ Development tips:"
echo "  • Check temp/source_*.html files for manual analysis"
echo "  • Use browser dev tools on sportybet.com to see network requests"
echo "  • Look for 'XHR' or 'Fetch' requests in the Network tab"
echo "  • SportyBet might use WebSocket connections for live data"

echo ""
echo "🎉 API scraper test completed!"