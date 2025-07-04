#!/usr/bin/env python3
"""
HTML Inspector for SportyBet pages
Use this to examine the HTML structure before implementing parsing
"""

import requests
from bs4 import BeautifulSoup
import sys
import os
from pathlib import Path
import json

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    from settings import HEADERS, SPORTYBET_UPCOMING_URL, SPORTYBET_LIVE_URL
except ImportError:
    print("Using default headers and URLs")
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    SPORTYBET_UPCOMING_URL = "https://sportybet.com/ng/sport/football/sr:category:1/today"
    SPORTYBET_LIVE_URL = "https://sportybet.com/ng/sport/football/sr:category:1/live"

def inspect_page(url, page_name):
    """Download and inspect page structure"""
    print(f"\n🔍 Inspecting {page_name}: {url}")
    print("=" * 60)
    
    try:
        # Create temp directory
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Fetch the page
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save full HTML for manual inspection
        html_file = temp_dir / f"{page_name}_source.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Page downloaded successfully")
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"📏 Page size: {len(response.text):,} characters")
        print(f"🏗️ HTML saved to: {html_file}")
        
        # Analyze page structure
        print(f"\n📊 Page Structure Analysis:")
        print(f"  • Total elements: {len(soup.find_all())}")
        print(f"  • Scripts: {len(soup.find_all('script'))}")
        print(f"  • Links: {len(soup.find_all('a'))}")
        print(f"  • Images: {len(soup.find_all('img'))}")
        print(f"  • Divs: {len(soup.find_all('div'))}")
        
        # Look for potential match-related elements
        print(f"\n🔍 Looking for match-related elements...")
        
        # Common selectors that might contain match data
        selectors_to_try = [
            # Generic match/game selectors
            '.match', '.game', '.fixture', '.event', '.competition',
            '[class*="match"]', '[class*="game"]', '[class*="fixture"]', '[class*="event"]',
            '[data-match]', '[data-game]', '[data-fixture]', '[data-event]',
            
            # SportyBet specific patterns (guessing)
            '.sport-event', '.market', '.bet-item', '.odds', '.team',
            '[class*="sport"]', '[class*="team"]', '[class*="odds"]', '[class*="bet"]',
            
            # Common sports betting patterns
            '.home-team', '.away-team', '.vs', '.versus',
            '[class*="home"]', '[class*="away"]', '[class*="vs"]'
        ]
        
        found_elements = {}
        
        for selector in selectors_to_try:
            try:
                elements = soup.select(selector)
                if elements:
                    found_elements[selector] = len(elements)
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # Show sample content from first few elements
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        text = elem.get_text(strip=True)[:100]
                        classes = elem.get('class', [])
                        print(f"    [{i+1}] Classes: {classes}")
                        print(f"        Text: {text}...")
                        if elem.get('data-match') or elem.get('data-game'):
                            print(f"        Data attrs: {[k for k in elem.attrs.keys() if k.startswith('data-')]}")
            except Exception as e:
                continue  # Skip invalid selectors
        
        if not found_elements:
            print("❌ No obvious match elements found with common selectors")
            
            # Try to find any elements that might contain team names or odds
            print("\n🔍 Searching for potential team/odds patterns...")
            
            # Look for text patterns that might indicate matches
            text_patterns = ['vs', 'v.', '-', 'against', ':', '|']
            for pattern in text_patterns:
                elements_with_pattern = []
                for elem in soup.find_all(text=True):
                    if pattern in elem.lower() and len(elem.strip()) > 5:
                        parent = elem.parent
                        if parent and parent.name != 'script':
                            elements_with_pattern.append(parent)
                
                if elements_with_pattern:
                    print(f"📍 Found {len(elements_with_pattern)} elements containing '{pattern}'")
                    for elem in elements_with_pattern[:3]:
                        print(f"    Text: {elem.get_text(strip=True)[:80]}...")
                        print(f"    Tag: {elem.name}, Classes: {elem.get('class', [])}")
        
        # Look for JavaScript data
        print(f"\n📜 Checking for JavaScript data...")
        scripts = soup.find_all('script')
        js_data_found = False
        
        for script in scripts:
            if script.string:
                script_content = script.string
                # Look for JSON-like data structures
                if any(keyword in script_content for keyword in ['matches', 'events', 'odds', 'teams', 'fixtures']):
                    print(f"📜 Found potential match data in JavaScript")
                    # Show a sample of the script content
                    sample = script_content[:200].replace('\n', ' ')
                    print(f"    Sample: {sample}...")
                    js_data_found = True
                    break
        
        if not js_data_found:
            print("❌ No obvious JavaScript match data found")
        
        # Save analysis results
        analysis_file = temp_dir / f"{page_name}_analysis.json"
        analysis_data = {
            'url': url,
            'page_name': page_name,
            'title': soup.title.string if soup.title else None,
            'page_size': len(response.text),
            'total_elements': len(soup.find_all()),
            'found_selectors': found_elements,
            'scripts_count': len(scripts),
            'has_potential_js_data': js_data_found
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"📊 Analysis saved to: {analysis_file}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return False
    except Exception as e:
        print(f"❌ Error analyzing page: {e}")
        return False

def main():
    """Main inspection function"""
    print("🔍 SportyBet HTML Structure Inspector")
    print("=====================================")
    
    # Inspect both pages
    pages_to_inspect = [
        (SPORTYBET_UPCOMING_URL, "upcoming_matches"),
        (SPORTYBET_LIVE_URL, "live_matches")
    ]
    
    success_count = 0
    for url, name in pages_to_inspect:
        if inspect_page(url, name):
            success_count += 1
    
    print(f"\n📋 Summary:")
    print(f"  • Successfully inspected {success_count}/{len(pages_to_inspect)} pages")
    print(f"  • HTML files saved to: temp/")
    print(f"  • Analysis data saved to: temp/")
    
    if success_count > 0:
        print(f"\n🎯 Next steps:")
        print(f"  1. Review the HTML files in temp/ directory")
        print(f"  2. Look for the actual selectors used by SportyBet")
        print(f"  3. Update the parse_matches() function in scripts/sportybet_scraper.py")
        print(f"  4. Test with ./test_simple.sh")
    else:
        print(f"\n❌ No pages could be inspected. Check your internet connection.")

if __name__ == "__main__":
    main()