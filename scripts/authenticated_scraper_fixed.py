#!/usr/bin/env python3
"""
Fixed Authenticated SportyBet Scraper
Uses navigation approach instead of direct login URLs
Based on analysis findings: login buttons exist on home page
"""

import requests
import json
import time
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from settings import HEADERS, SPORTYBET_BASE_URL
except ImportError:
    print("Using default settings...")
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    SPORTYBET_BASE_URL = "https://sportybet.com/ng"

class FixedAuthenticatedSportyBetScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setup_logging()
        self.is_logged_in = False
        
    def setup_logging(self):
        """Setup logging configuration"""
        Path("logs").mkdir(exist_ok=True)
        log_file = f"logs/auth_scraper_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={HEADERS['User-Agent']}")
            
            # Additional options for better compatibility
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Chrome WebDriver initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Chrome: {e}")
            return False

    def login_to_sportybet(self, username=None, password=None):
        """Fixed login using navigation approach - based on analysis findings"""
        if not self.setup_selenium():
            return False
            
        try:
            self.logger.info("🔐 Starting FIXED SportyBet login...")
            
            # Step 1: Load home page (we know this works)
            home_url = f"{SPORTYBET_BASE_URL}"
            self.logger.info(f"📱 Loading home page: {home_url}")
            self.driver.get(home_url)
            
            # Step 2: Wait for SPA to fully load (critical!)
            self.logger.info("⏳ Waiting 15 seconds for SPA to fully load...")
            time.sleep(15)  # Based on analysis - this is required
            
            # Step 3: Look for login button (we found these work)
            self.logger.info("🔍 Looking for login button...")
            wait = WebDriverWait(self.driver, 30)
            
            # Based on analysis findings - these selectors work
            login_selectors = [
                "button[class*='login']",  # ✅ Found in analysis
                "//button[contains(text(), 'Login')]",  # ✅ Found in analysis
                "//a[contains(text(), 'Login')]",
                "//a[contains(text(), 'Sign')]",
                ".login-btn",
                "#login-btn"
            ]
            
            login_element = None
            for selector in login_selectors:
                try:
                    if selector.startswith('//'):
                        login_element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        login_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    self.logger.info(f"✅ Found login element: {selector}")
                    break
                except TimeoutException:
                    self.logger.debug(f"⏳ Selector not found: {selector}")
                    continue
            
            if not login_element:
                self.logger.error("❌ No login button found after 30 seconds")
                self.save_debug_page("no_login_button_found")
                return False
            
            # Step 4: Click login button
            self.logger.info("🖱️ Clicking login button...")
            self.driver.execute_script("arguments[0].scrollIntoView();", login_element)
            time.sleep(1)
            login_element.click()
            
            # Step 5: Wait for login form to appear
            self.logger.info("⏳ Waiting for login form to appear...")
            time.sleep(5)  # Wait for modal/form to load
            
            # Step 6: Find login form fields
            self.logger.info("📝 Looking for login form fields...")
            
            # Try multiple selectors for username field
            username_selectors = [
                "input[type='email']",
                "input[type='text']",
                "input[placeholder*='email' i]",
                "input[placeholder*='phone' i]",
                "input[name='username']",
                "input[name='email']",
                "input[name='phone']"
            ]
            
            password_selectors = [
                "input[type='password']",
                "input[name='password']"
            ]
            
            username_field = None
            password_field = None
            
            # Find username field with explicit wait
            for selector in username_selectors:
                try:
                    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    self.logger.info(f"✅ Found username field: {selector}")
                    break
                except TimeoutException:
                    continue
            
            # Find password field
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"✅ Found password field: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field or not password_field:
                self.logger.error("❌ Login form fields not found")
                self.save_debug_page("login_form_not_found")
                return False
            
            # Step 7: Get credentials if not provided
            if not username:
                print("\n🔐 SportyBet Login Required")
                username = input("📧 Enter your email/phone: ").strip()
                
            if not password:
                import getpass
                password = getpass.getpass("🔒 Enter your password: ").strip()
            
            if not username or not password:
                self.logger.error("❌ Username or password not provided")
                return False
            
            # Step 8: Fill in credentials
            self.logger.info("📝 Filling in credentials...")
            
            # Clear and fill username
            username_field.clear()
            time.sleep(0.5)
            username_field.send_keys(username)
            time.sleep(1)
            
            # Clear and fill password
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(password)
            time.sleep(1)
            
            # Step 9: Submit the form
            self.logger.info("🚀 Submitting login form...")
            
            # Try to find submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                ".login-submit",
                ".submit-btn",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Sign')]"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if selector.startswith('//'):
                        submit_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        submit_button.click()
                        self.logger.info(f"✅ Clicked submit button: {selector}")
                        break
                except:
                    continue
            
            if not submit_button:
                # Fallback: try Enter key
                self.logger.info("🔄 Trying Enter key as fallback...")
                password_field.send_keys(Keys.RETURN)
            
            # Step 10: Wait for login to complete
            self.logger.info("⏳ Waiting for login to complete...")
            time.sleep(10)
            
            # Step 11: Check if login was successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check various indicators of successful login
            success_indicators = [
                'dashboard' in current_url.lower(),
                'account' in page_source,
                'logout' in page_source,
                'balance' in page_source,
                'profile' in page_source
            ]
            
            failure_indicators = [
                'login' in current_url.lower(),
                'error' in page_source,
                'invalid' in page_source,
                'incorrect' in page_source
            ]
            
            if any(success_indicators) and not any(failure_indicators):
                self.logger.info("✅ Login appears successful!")
                self.is_logged_in = True
                
                # Save session cookies
                cookies = self.driver.get_cookies()
                for cookie in cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                return True
            else:
                self.logger.error("❌ Login may have failed")
                self.save_debug_page("login_failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            self.save_debug_page("login_exception")
            return False

    def save_debug_page(self, reason):
        """Save current page for debugging"""
        try:
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            debug_file = temp_dir / f"debug_{reason}_{datetime.now().strftime('%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            self.logger.info(f"🔍 Debug page saved: {debug_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save debug page: {e}")

    def scrape_authenticated_content(self):
        """Scrape content after authentication"""
        if not self.is_logged_in:
            self.logger.error("❌ Not logged in - cannot scrape authenticated content")
            return []
        
        self.logger.info("📊 Scraping authenticated content...")
        
        # Navigate to different sections after login
        pages_to_scrape = [
            f"{SPORTYBET_BASE_URL}/sport/football/sr:category:1/today",
            f"{SPORTYBET_BASE_URL}/sport/football/sr:category:1/live"
        ]
        
        matches_data = []
        
        for url in pages_to_scrape:
            try:
                self.logger.info(f"📖 Scraping: {url}")
                self.driver.get(url)
                time.sleep(10)  # Wait for content to load
                
                # Save authenticated page
                page_name = url.split('/')[-1]
                auth_file = Path("temp") / f"auth_{page_name}_{datetime.now().strftime('%H%M%S')}.html"
                with open(auth_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                
                self.logger.info(f"💾 Authenticated page saved: {auth_file}")
                
                # TODO: Parse matches from authenticated content
                # For now, just record that we accessed the page
                matches_data.append({
                    'url': url,
                    'status': 'authenticated_access',
                    'timestamp': datetime.now().isoformat(),
                    'page_size': len(self.driver.page_source)
                })
                
            except Exception as e:
                self.logger.error(f"❌ Error scraping {url}: {e}")
        
        return matches_data

    def save_results(self, matches_data):
        """Save scraping results"""
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = output_dir / f"authenticated_results_{timestamp}.json"
        
        results = {
            'timestamp': timestamp,
            'authentication_status': 'success' if self.is_logged_in else 'failed',
            'matches_found': len(matches_data),
            'matches_data': matches_data
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Results saved: {results_file}")

    def run(self, username=None, password=None):
        """Main execution method"""
        self.logger.info("🚀 Starting FIXED Authenticated SportyBet Scraper...")
        
        try:
            # Step 1: Login
            if not self.login_to_sportybet(username, password):
                self.logger.error("❌ Login failed - cannot proceed")
                return False
            
            # Step 2: Scrape authenticated content
            matches_data = self.scrape_authenticated_content()
            
            # Step 3: Save results
            self.save_results(matches_data)
            
            self.logger.info("✅ Scraping completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error during scraping: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔧 WebDriver closed")

def main():
    """Main function for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fixed Authenticated SportyBet Scraper')
    parser.add_argument('--username', help='SportyBet username/email')
    parser.add_argument('--password', help='SportyBet password')
    parser.add_argument('--visible', action='store_true', help='Show browser window (not headless)')
    
    args = parser.parse_args()
    
    scraper = FixedAuthenticatedSportyBetScraper(headless=not args.visible)
    success = scraper.run(username=args.username, password=args.password)
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
