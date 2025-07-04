#!/bin/bash

# Test Fixed Authenticated Scraper
echo "🧪 Testing Fixed Authenticated Scraper"
echo "====================================="

# Activate virtual environment
source venv/bin/activate

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Environment: $VIRTUAL_ENV"

# Check Chrome availability
if command -v google-chrome >/dev/null 2>&1 || command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome >/dev/null 2>&1; then
    echo "✅ Chrome available"
else
    echo "⚠️ Chrome not found - may cause issues"
fi

echo ""
echo "🔧 TESTING OPTIONS:"
echo "1. 🖥️  Test with VISIBLE browser (recommended for first test)"
echo "2. 👻 Test with HEADLESS browser"
echo "3. 📋 Just verify the script loads without errors"
echo ""

read -p "Choose option (1/2/3): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🖥️ Testing with VISIBLE browser..."
        echo "💡 You'll see the actual browser and can watch the login process"
        python3 scripts/authenticated_scraper_fixed.py --visible
        ;;
    2)
        echo "👻 Testing with HEADLESS browser..."
        python3 scripts/authenticated_scraper_fixed.py
        ;;
    3)
        echo "📋 Verifying script loads..."
        python3 -c "
try:
    from scripts.authenticated_scraper_fixed import FixedAuthenticatedSportyBetScraper
    print('✅ Script loads successfully')
    scraper = FixedAuthenticatedSportyBetScraper()
    print('✅ Class instantiates successfully')
except Exception as e:
    print(f'❌ Error: {e}')
"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📊 Checking results..."
if ls data/raw/authenticated_results_*.json 1> /dev/null 2>&1; then
    echo "✅ Results files created:"
    ls -la data/raw/authenticated_results_*
else
    echo "⚠️ No results files found (may be normal if login failed)"
fi

echo ""
echo "🔍 Debug files:"
if ls temp/debug_*.html 1> /dev/null 2>&1; then
    echo "📄 Debug files available:"
    ls -la temp/debug_*
    echo "💡 Open these in browser to see what happened during login"
else
    echo "✅ No debug files (good - means no errors)"
fi

echo ""
echo "📋 Recent logs:"
find logs -name "auth_scraper_fixed_*.log" -type f | sort | tail -1 | xargs tail -10 2>/dev/null || echo "No logs found"
