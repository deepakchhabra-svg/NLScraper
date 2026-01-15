"""
Example configuration file for NLScraper
Copy this file to config.py and adjust settings as needed
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
CHECKPOINTS_DIR = os.path.join(BASE_DIR, 'checkpoints')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
for directory in [OUTPUT_DIR, IMAGES_DIR, CHECKPOINTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Noel Leeming website configuration
BASE_URL = 'https://www.noelleeming.co.nz'
CATEGORIES_URL = f'{BASE_URL}/shop'

# Scraping settings - Adjust these based on your needs
REQUEST_DELAY = 2  # Increase this if you get rate limited (2-5 seconds recommended)
CONCURRENT_REQUESTS = 2  # Keep this low to be respectful
TIMEOUT = 30  # Request timeout in seconds
MAX_RETRIES = 3  # Maximum number of retries for failed requests
RETRY_DELAY = 5  # Delay between retries in seconds

# User agent rotation for ethical scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# Image download settings
DOWNLOAD_IMAGES = True  # Set to False to skip image downloads
IMAGE_QUALITY = 'high'  # 'high', 'medium', 'low'
IMAGE_FORMAT = 'jpg'
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB max per image

# Output settings
OUTPUT_FORMAT = 'csv'  # 'csv' or 'excel' - CSV is faster for large datasets
OUTPUT_FILENAME = 'noel_leeming_products'

# TradeMe compatibility settings
TRADEME_COMPATIBLE = True  # Creates additional TradeMe-formatted export

# Resume functionality
ENABLE_CHECKPOINTS = True  # Save progress to resume later
CHECKPOINT_INTERVAL = 50  # Save checkpoint every N products

# Error handling
CONTINUE_ON_ERROR = True  # Continue scraping even if some products fail
LOG_ERRORS = True  # Log all errors to file

# Selenium settings (only needed if website requires JavaScript)
USE_SELENIUM = False  # Set to True if you need JavaScript rendering
HEADLESS_BROWSER = True  # Run browser in background
BROWSER_TYPE = 'chrome'  # 'chrome' or 'firefox'

# Rate limiting - Be respectful to the website
RESPECT_ROBOTS_TXT = True
DOWNLOAD_DELAY = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Logging
LOG_LEVEL = 'INFO'  # DEBUG for verbose, INFO for normal, WARNING for minimal
LOG_FILE = os.path.join(LOGS_DIR, 'scraper.log')
