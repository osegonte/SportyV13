#!/usr/bin/env python3
"""
Fixed SportyBet Login Page Analyzer
No more infinite recursion - runs directly in current environment
"""

import sys
import os

# Check if we're already in virtual environment
if not os.environ.get('VIRTUAL_ENV'):
    print("❌ Please activate virtual environment first:")
    print("source venv/bin/activate")
    print("Then run: python3 analyze_sportybet_login_fixed.py")
    exit(1)

# Now we're in the virtual environment, import normally
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import json

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available for dynamic analysis")

def analyze_sportybet_comprehensive():
    """Complete analysis of SportyBet login and authentication"""
    print("🔍 COMPREHENSIVE SPORTYBET LOGIN ANALYSIS")
    print("=" * 50)
    
    # Headers for requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # URLs to analyze
    urls_to_analyze = [
        ("Home Page", "https://sportybet.com/ng"),
        ("Sports Page", "https://sportybet.com/ng/sport/football"),
        ("Mobile Home", "https://sportybet.com/ng/m"),
    ]
    
    analysis_results = []
    
    print("\n📊 STATIC ANALYSIS WITH REQUESTS")
    print("-" * 40)
    
    for name, url in urls_to_analyze:
        try:
            print(f"\n🌐 Testing {name}: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Success: {response.status_code}")
                
                # Save page
                safe_name = name.lower().replace(' ', '_')
                html_file = temp_dir / f"{safe_name}_{datetime.now().strftime('%H%M%S')}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Analyze
                soup = BeautifulSoup(response.text, 'html.parser')
                
                page_analysis = {
                    'name': name,
                    'url': url,
                    'status': response.status_code,
                    'title': soup.title.string if soup.title else 'No title',
                    'has_app_div': bool(soup.find('div', {'id': 'app'})),
                    'is_spa': 'logoLoading' in response.text or 'react' in response.text.lower(),
                    'scripts': len(soup.find_all('script')),
                    'forms': len(soup.find_all('form')),
                    'inputs': len(soup.find_all('input')),
                    'html_file': str(html_file)
                }
                
                analysis_results.append(page_analysis)
                
                print(f"📄 Saved: {html_file}")
                print(f"📊 Title: {page_analysis['title']}")
                print(f"🎯 SPA: {page_analysis['is_spa']}")
                print(f"📋 Forms: {page_analysis['forms']}, Inputs: {page_analysis['inputs']}")
                    
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Dynamic analysis with Selenium
    if SELENIUM_AVAILABLE and analysis_results:
        print(f"\n📊 DYNAMIC ANALYSIS WITH SELENIUM")
        print("-" * 40)
        
        # Use the working URL (should be home page)
        working_page = next((r for r in analysis_results if r['status'] == 200), None)
        if working_page:
            selenium_analysis = analyze_with_selenium(working_page['url'])
            if selenium_analysis:
                analysis_results.append(selenium_analysis)
    
    # Save complete analysis
    analysis_file = temp_dir / f"complete_analysis_{datetime.now().strftime('%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n📊 Complete analysis saved: {analysis_file}")
    
    # Generate recommendations
    generate_authentication_solution(analysis_results)
    
    return analysis_results

def analyze_with_selenium(url):
    """Analyze page with Selenium for dynamic content"""
    if not SELENIUM_AVAILABLE:
        return None
        
    print(f"\n🤖 Selenium analysis of: {url}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        print("⏳ Waiting for JavaScript to load...")
        import time
        time.sleep(15)  # Wait for SPA to fully load
        
        # Look for login-related elements after JavaScript loads
        login_selectors = [
            "button[class*='login']",
            "a[href*='login']",
            "a[href*='auth']",
            "[data-testid*='login']",
            "[data-testid*='auth']",
            "//a[contains(text(), 'Login')]",
            "//a[contains(text(), 'Sign')]",
            "//button[contains(text(), 'Login')]"
        ]
        
        found_elements = []
        for selector in login_selectors:
            try:
                if selector.startswith('//'):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                if elements:
                    visible_count = sum(1 for e in elements if e.is_displayed())
                    found_elements.append({
                        'selector': selector,
                        'total': len(elements),
                        'visible': visible_count
                    })
                    print(f"✅ {selector}: {len(elements)} total, {visible_count} visible")
            except:
                continue
        
        # Save rendered page
        selenium_file = temp_dir / f"selenium_rendered_{datetime.now().strftime('%H%M%S')}.html"
        with open(selenium_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print(f"📄 Selenium page saved: {selenium_file}")
        
        return {
            'name': 'Selenium Dynamic Analysis',
            'url': url,
            'method': 'selenium',
            'found_elements': found_elements,
            'current_url': driver.current_url,
            'html_file': str(selenium_file)
        }
        
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def generate_authentication_solution(analysis_results):
    """Generate specific authentication solution based on analysis"""
    print(f"\n🎯 AUTHENTICATION SOLUTION")
    print("=" * 50)
    
    # Analyze results
    working_pages = [r for r in analysis_results if r.get('status') == 200]
    spa_confirmed = any(r.get('is_spa') for r in working_pages)
    selenium_data = next((r for r in analysis_results if r.get('method') == 'selenium'), None)
    
    print("🔍 KEY FINDINGS:")
    print(f"   • SportyBet uses SPA: {spa_confirmed}")
    print(f"   • Working pages found: {len(working_pages)}")
    print(f"   • Dynamic analysis available: {selenium_data is not None}")
    
    if selenium_data and selenium_data.get('found_elements'):
        login_elements = selenium_data['found_elements']
        print(f"   • Login elements found: {len(login_elements)}")
        for elem in login_elements:
            if elem['visible'] > 0:
                print(f"     - {elem['selector']}: {elem['visible']} visible")
    
    print(f"\n💡 RECOMMENDED APPROACH:")
    
    if spa_confirmed:
        print("1. 🎯 SELENIUM WITH NAVIGATION APPROACH")
        print("   • Load home page: https://sportybet.com/ng")
        print("   • Wait 15+ seconds for SPA to fully load")
        print("   • Find and click login button/link")
        print("   • Wait for login form to appear")
        print("   • Use proper selectors for form fields")
        
        print(f"\n2. 🔧 KEY IMPLEMENTATION POINTS:")
        print("   • Use longer waits (15+ seconds)")
        print("   • Use WebDriverWait with explicit conditions")
        print("   • Navigate via button clicks, not direct URLs")
        print("   • Test with headless=False first")
    
    print(f"\n🧪 NEXT STEPS:")
    print("1. Update authenticated_scraper.py with navigation approach")
    print("2. Test with visible browser first (headless=False)")
    print("3. Use the working selectors found in analysis")
    print("4. Implement proper waits and error handling")

if __name__ == "__main__":
    analyze_sportybet_comprehensive()
