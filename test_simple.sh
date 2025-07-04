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
