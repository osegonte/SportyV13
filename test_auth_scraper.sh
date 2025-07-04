#!/bin/bash

# Test the Authenticated SportyBet Scraper
echo "🔐 Testing Authenticated SportyBet Scraper"
echo "=========================================="

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
    echo "✅ Chrome available for authentication"
else
    echo "⚠️ Chrome not found - authentication may not work"
    echo "💡 Install Chrome: brew install --cask google-chrome"
fi

echo ""
echo "🔐 Authentication Options:"
echo "========================="
echo "The scraper can:"
echo "  1. Use saved session (if available)"
echo "  2. Login with your SportyBet credentials" 
echo "  3. Show browser window for manual intervention"
echo ""

# Ask user for preferences
read -p "📱 Do you want to show the browser window (helpful for first-time login)? (y/N): " -n 1 -r
echo
SHOW_BROWSER=""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SHOW_BROWSER="--no-headless"
    echo "✅ Will show browser window"
else
    echo "✅ Will run headless"
fi

read -p "🔄 Do you want to use a saved session (if available)? (Y/n): " -n 1 -r
echo
USE_SESSION=""
if [[ $REPLY =~ ^[Nn]$ ]]; then
    USE_SESSION="--no-session"
    echo "✅ Will always login fresh"
else
    echo "✅ Will try to use saved session first"
fi

echo ""
echo "🚀 Running Authenticated Scraper..."
echo "=================================="

# Run the authenticated scraper
python3 scripts/authenticated_scraper.py $SHOW_BROWSER $USE_SESSION

SCRAPER_EXIT_CODE=$?

echo ""
echo "📊 Checking Results..."
echo "====================="

# Check for authenticated match data
if ls data/raw/sportybet_authenticated_*.json 1> /dev/null 2>&1; then
    echo "✅ Authenticated match data found:"
    for file in data/raw/sportybet_authenticated_*.json; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes)"
        
        # Show sample content
        echo "📋 Sample authenticated matches:"
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
    echo "⚠️ No authenticated match data found"
fi

# Check for network request data
if ls data/raw/network_requests_*.json 1> /dev/null 2>&1; then
    echo ""
    echo "✅ Network request data found:"
    for file in data/raw/network_requests_*.json; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes)"
        
        # Show network requests
        echo "📡 Captured network requests:"
        python3 -c "
import json
try:
    with open('$file', 'r') as f:
        requests_data = json.load(f)
    if isinstance(requests_data, list):
        print(f'  📊 Total requests: {len(requests_data)}')
        for i, req in enumerate(requests_data[:5]):  # Show first 5
            print(f'  🌐 Request {i+1}:')
            print(f'    URL: {req.get(\"url\", \"N/A\")}')
            print(f'    Type: {req.get(\"type\", \"N/A\")}')
            if 'duration' in req:
                print(f'    Duration: {req.get(\"duration\", \"N/A\")}ms')
            print()
    else:
        print(f'  📊 Data type: {type(requests_data)}')
except Exception as e:
    print(f'  ❌ Error reading network requests: {e}')
"
    done
else
    echo "⚠️ No network request data found"
fi

# Check for saved session
echo ""
echo "🍪 Session Information:"
if [ -f "temp/sportybet_session.json" ]; then
    echo "✅ Session file found:"
    python3 -c "
import json
from datetime import datetime
try:
    with open('temp/sportybet_session.json', 'r') as f:
        session = json.load(f)
    
    print(f'  📅 Created: {session.get(\"timestamp\", \"Unknown\")}')
    print(f'  🍪 Cookies: {len(session.get(\"cookies\", []))} saved')
    
    # Check if session is still valid (less than 24 hours old)
    if 'timestamp' in session:
        session_time = datetime.fromisoformat(session['timestamp'])
        age_hours = (datetime.now() - session_time).total_seconds() / 3600
        if age_hours < 24:
            print(f'  ✅ Session is fresh ({age_hours:.1f} hours old)')
        else:
            print(f'  ⚠️ Session is old ({age_hours:.1f} hours old)')
    
except Exception as e:
    print(f'  ❌ Error reading session: {e}')
"
else
    echo "⚠️ No saved session found"
fi

# Check temp files for debugging
echo ""
echo "🔍 Debug Files Created:"
echo "====================="
if ls temp/auth_source_*.html 1> /dev/null 2>&1; then
    for file in temp/auth_source_*.html; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes) - authenticated page source"
    done
fi

if ls temp/login_page_*.html 1> /dev/null 2>&1; then
    for file in temp/login_page_*.html; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes) - login page for debugging"
    done
fi

if ls temp/source_*.html 1> /dev/null 2>&1; then
    for file in temp/source_*.html; do
        SIZE=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo "  📄 $file ($SIZE bytes) - page source analysis"
    done
fi

# Show recent logs
echo ""
echo "📋 Recent Log Entries:"
echo "====================="
LATEST_LOG=$(find logs -name "auth_scraper_*.log" -type f 2>/dev/null | sort | tail -1)
if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
    echo "📄 Latest log: $LATEST_LOG"
    echo "----------------------------------------"
    tail -25 "$LATEST_LOG"
    echo "----------------------------------------"
else
    echo "⚠️ No authentication log files found"
fi

echo ""
echo "🎯 Summary & Analysis:"
echo "====================="

# Count results
AUTH_MATCH_COUNT=0
NETWORK_COUNT=0

if ls data/raw/sportybet_authenticated_*.json 1> /dev/null 2>&1; then
    AUTH_MATCH_COUNT=$(python3 -c "
import json
import glob
total = 0
for file in glob.glob('data/raw/sportybet_authenticated_*.json'):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            total += len(data)
    except: pass
print(total)
" 2>/dev/null || echo "0")
fi

if ls data/raw/network_requests_*.json 1> /dev/null 2>&1; then
    NETWORK_COUNT=$(python3 -c "
import json
import glob
total = 0
for file in glob.glob('data/raw/network_requests_*.json'):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            total += len(data)
    except: pass
print(total)
" 2>/dev/null || echo "0")
fi

echo "📊 Authentication Results:"
echo "  • Exit code: $SCRAPER_EXIT_CODE"
echo "  • Matches found: $AUTH_MATCH_COUNT"
echo "  • Network requests captured: $NETWORK_COUNT"
echo "  • Session saved: $([ -f "temp/sportybet_session.json" ] && echo "Yes" || echo "No")"

if [ "$SCRAPER_EXIT_CODE" -eq "0" ]; then
    if [ "$AUTH_MATCH_COUNT" -gt "0" ]; then
        echo ""
        echo "🎉 SUCCESS! Authentication worked!"
        echo "✅ Found $AUTH_MATCH_COUNT matches with authenticated access"
        echo ""
        echo "🎯 Next Steps:"
        echo "  1. ✅ Review the match data structure in data/raw/"
        echo "  2. ✅ Refine parsing logic if needed"
        echo "  3. ✅ Set up automated data collection"
        echo "  4. ✅ Move to Stage 4: Data Matching with SofaScore"
        
    elif [ "$NETWORK_COUNT" -gt "0" ]; then
        echo ""
        echo "🔄 PARTIAL SUCCESS! Authentication worked but limited matches"
        echo "✅ Captured $NETWORK_COUNT network requests"
        echo "⚠️ May need to improve parsing logic"
        echo ""
        echo "🎯 Next Steps:"
        echo "  1. 🔍 Analyze captured network requests"
        echo "  2. 🔧 Test API endpoints manually"
        echo "  3. 🎯 Improve match extraction logic"
        
    else
        echo ""
        echo "🔐 AUTHENTICATION SUCCESS but no data extracted"
        echo "✅ Login process worked"
        echo "⚠️ No matches or network requests found"
        echo ""
        echo "🎯 Next Steps:"
        echo "  1. 🔍 Check authenticated page sources in temp/"
        echo "  2. 🌐 Look for different page URLs after login"
        echo "  3. 🧪 Try accessing different sections of SportyBet"
        echo "  4. 📱 Consider mobile site or app APIs"
    fi
else
    echo ""
    echo "❌ AUTHENTICATION FAILED"
    echo "❌ Scraper exited with error code: $SCRAPER_EXIT_CODE"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  1. 🔍 Check login page debug files in temp/"
    echo "  2. 📋 Review authentication logs"
    echo "  3. 🌐 Verify SportyBet login page hasn't changed"
    echo "  4. 🔑 Confirm credentials are correct"
    echo "  5. 🤖 Check if CAPTCHA or 2FA is required"
fi

echo ""
echo "💡 Additional Tips:"
echo "=================="
echo "  • 🔍 Open temp/*.html files in browser to see actual page content"
echo "  • 🌐 Use browser dev tools on sportybet.com to compare"
echo "  • 📱 Try running with --no-headless to see browser interactions"
echo "  • 🔄 Session file saves login state for future runs"
echo "  • 🎯 Look for different URLs after successful login"

echo ""
echo "🎉 Authenticated scraper test completed!"