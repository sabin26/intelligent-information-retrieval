# The starting point for our crawler
SEED_URL = "https://pureportal.coventry.ac.uk/en/organisations/fbl-school-of-economics-finance-and-accounting/publications/"

# Base URL to resolve relative links
BASE_URL = "https://pureportal.coventry.ac.uk"

# Delay between requests to be a polite crawler (in seconds)
CRAWL_DELAY = 2

# Paths for storing data
DATA_DIR = "data"
CRAWLED_DATA_FILE = f"{DATA_DIR}/crawled_publications.json"
INDEX_FILE = f"{DATA_DIR}/index.joblib"
