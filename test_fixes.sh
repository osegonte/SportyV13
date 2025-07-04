#!/bin/bash

echo "🧪 Testing All Fixes"
echo "==================="

# Activate virtual environment
source venv/bin/activate

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Virtual environment active: $VIRTUAL_ENV"

# Test imports
echo "🔍 Testing module imports..."
python3 -c "
try:
    import requests, bs4, pandas, selenium
    print('✅ All modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test main scraper syntax
echo "🔍 Testing main scraper syntax..."
python3 -m py_compile scripts/sportybet_scraper.py && echo "✅ Main scraper syntax OK" || echo "❌ Syntax error in main scraper"

# Test login analyzer syntax
echo "🔍 Testing login analyzer syntax..."
python3 -m py_compile analyze_sportybet_login.py && echo "✅ Login analyzer syntax OK" || echo "❌ Syntax error in login analyzer"

echo ""
echo "📋 Available scripts:"
ls -la *.sh | grep -E "(test_|fix_|analyze)" | while read line; do
    echo "  ✅ $line"
done

echo ""
echo "🎯 Ready to test:"
echo "  ./test_stage3.sh              # Test main scraper"
echo "  python3 analyze_sportybet_login.py  # Analyze login page"
echo "  ./fix_authentication.sh       # Get authentication help"
