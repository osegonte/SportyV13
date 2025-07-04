# SportyBet Scraper Configuration

# SportyBet URLs
SPORTYBET_BASE_URL = "https://sportybet.com/ng"
SPORTYBET_LIVE_URL = "https://sportybet.com/ng/sport/football/sr:category:1/live"
SPORTYBET_UPCOMING_URL = "https://sportybet.com/ng/sport/football/sr:category:1/today"

# Request headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Data storage paths
DATA_DIR = "data"
LOGS_DIR = "logs"

# Betting settings (for testing)
TEST_BET_AMOUNT = 10  # Minimum bet amount in Naira
MAX_RETRIES = 3
TIMEOUT = 30

# SofaScore API settings
SOFASCORE_API_BASE = "https://api.sofascore.com/api/v1"
