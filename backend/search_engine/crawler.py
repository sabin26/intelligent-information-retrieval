import asyncio
import json
import os
from collections import deque
from urllib.parse import urljoin
from tqdm import tqdm

from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright, Error

from config import SEED_URL, BASE_URL, CRAWL_DELAY, CRAWLED_DATA_FILE, DATA_DIR

async def crawl():
    """
    Crawls the Coventry University publications portal starting from a seed URL.
    It follows a BFS approach for pagination and extracts publication details.
    """
    print("Starting crawler with Playwright...")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Error as e:
            print(f"Error launching browser: {e}")
            print("Please ensure you have run 'playwright install'")
            return
            
        page = await browser.new_page()
        # Use a deque for an efficient queue (BFS) and a set to track visited URLs
        queue = deque([SEED_URL])
        visited_urls = {SEED_URL}
        publications = []

        # Ensure the data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        while queue:
            current_url = queue.popleft()
            print(f"Crawling: {current_url}")

            try:
                await page.goto(current_url, wait_until='domcontentloaded', timeout=30000)
                page_source = await page.content()
                soup = BeautifulSoup(page_source, 'html.parser')
            except Error as e:
                print(f"Error fetching {current_url} with Playwright: {e}")
                continue
            # Find all publication items on the page
            pub_list = soup.find_all('div', class_='result-container')
            
            # Using tqdm for a progress bar on the publication list
            for pub_item in tqdm(pub_list, desc=f"Parsing {len(pub_list)} publications"):
                title_tag = pub_item.find('h3', class_='title')
                if not title_tag or not title_tag.a:
                    continue

                title = title_tag.get_text(strip=True)
                pub_url = urljoin(BASE_URL, title_tag.a['href'])
                
                # Find all author tags and extract name and URL
                authors_data = []
                author_tags = pub_item.find_all('a', class_='link person')
                for author_tag in author_tags:
                    name = author_tag.get_text(strip=True)
                    # Ensure the href attribute exists before creating the full URL
                    if 'href' in author_tag.attrs:
                        profile_url = urljoin(BASE_URL, author_tag['href'])
                        authors_data.append({'name': name, 'url': profile_url})
                    else:
                        # Fallback for an author link without a URL
                        authors_data.append({'name': name, 'url': None})

                year_tag = pub_item.find('span', class_='date')
                year = year_tag.get_text(strip=True) if year_tag else "N/A"

                publications.append({
                    'title': title,
                    'url': pub_url,
                    'authors': authors_data,
                    'year': year
                })

            # Find the 'next' page link for pagination
            next_page_tag = soup.find('a', class_='next')
            next_page_url = None
            
            if isinstance(next_page_tag, Tag) and 'href' in next_page_tag.attrs:
                href_value = next_page_tag['href']
                # Handle case where href might be a list
                if isinstance(href_value, list):
                    href_value = href_value[0] if href_value else None
                if href_value:
                    next_page_url = urljoin(BASE_URL, href_value)
                    
            if next_page_url and next_page_url not in visited_urls:
                visited_urls.add(next_page_url)
                queue.append(next_page_url)
            
            # Polite crawling: wait before the next request
            await asyncio.sleep(CRAWL_DELAY)

        print("Closing Playwright browser.")
        await browser.close()

    # Save the extracted data to a file
    with open(CRAWLED_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(publications, f, indent=4, ensure_ascii=False)
        
    print(f"\nCrawling complete. Found {len(publications)} publications.")
    print(f"Data saved to {CRAWLED_DATA_FILE}")

if __name__ == '__main__':
    asyncio.run(crawl())