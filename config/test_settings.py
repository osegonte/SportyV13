# Test configuration for SportyBet scraper
import os
from datetime import datetime

# Test mode settings
TEST_MODE = True
MAX_PAGES_TO_SCRAPE = 2  # Limit for testing
DELAY_BETWEEN_REQUESTS = 2  # seconds
VERBOSE_LOGGING = True

# Test URLs (start with these)
TEST_URLS = [
    "https://sportybet.com/ng/sport/football/sr:category:1/today",
    "https://sportybet.com/ng/sport/football/sr:category:1/live"
]

# Output file for test run
TEST_OUTPUT_FILE = f"data/raw/test_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Log file for this session
LOG_FILE = f"logs/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
