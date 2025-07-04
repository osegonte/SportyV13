#!/bin/bash

# Stage 3 Test Runner - Clean and Focused
echo "🧪 SportyBet Stage 3 Test Runner"
echo "================================"

# Activate virtual environment
source venv/bin/activate

# Verify environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Environment: $VIRTUAL_ENV"
echo "🐍 Python: $(python3 --version)"

# Test module imports
echo "🔍 Testing imports..."
python3 -c "import requests, bs4, pandas, selenium; print('✅ All modules available')" || {
    echo "❌ Module import failed"
    exit 1
}

echo ""
echo "🚀 Running Stage 3 analysis..."
python3 scripts/sportybet_scraper.py

echo ""
echo "📊 Results:"
if ls data/raw/sportybet_stage3_*.json 1> /dev/null 2>&1; then
    echo "✅ Analysis complete:"
    ls -la data/raw/sportybet_stage3_*
    
    # Show key findings
    echo ""
    echo "🔍 Key findings:"
    python3 -c "
import json
import glob
for file in sorted(glob.glob('data/raw/sportybet_stage3_*.json')):
    with open(file, 'r') as f:
        data = json.load(f)
    findings = data.get('findings', {})
    print(f'📄 {file}:')
    for key, value in findings.items():
        print(f'  • {key}: {value}')
    break
"
else
    echo "⚠️ No analysis files found"
fi

echo ""
echo "📋 Recent logs:"
find logs -name "scraper_*.log" -type f | sort | tail -1 | xargs tail -10 2>/dev/null

echo ""
echo "🎯 Next step: Fix authentication in authenticated_scraper.py"
