import os

# The starting point for our crawler
SEED_URL = "https://pureportal.coventry.ac.uk/en/organisations/fbl-school-of-economics-finance-and-accounting/publications/"

# Base URL to resolve relative links
BASE_URL = "https://pureportal.coventry.ac.uk"

# Maximum number of retries if first attempt fails
MAX_RETRIES = 3

# Wait for the page to be idle for not more than 90 seconds
PAGE_TIMEOUT = 90000

# Paths for storing data
CRAWLED_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'crawled_publications.json')
INDEX_FILE = os.path.join(os.path.dirname(__file__), 'data', 'index.joblib')
