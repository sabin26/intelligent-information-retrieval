import asyncio
import json
import os
import random
from collections import deque
from urllib.parse import urljoin
from urllib import robotparser

from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright, Error
from tqdm import tqdm

from config import SEED_URL, BASE_URL, MAX_RETRIES, PAGE_TIMEOUT, CRAWLED_DATA_FILE

# Define a single User-Agent constant to be used by both Playwright and the robotparser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# --- Extract author name and profile url from publication url ---
def extract_authors_from_detail_page(soup, base_url):
    authors_data = []
    persons_p = soup.select_one('p.relations.persons')
    if not persons_p:
        return []
    for element in persons_p.contents:
        if isinstance(element, Tag) and element.name == 'a':
            name = element.get_text(strip=True)
            url = urljoin(base_url, str(element.get('href', '')))
            if name:
                authors_data.append({'name': name, 'url': url})
        elif isinstance(element, str):
            potential_names = element.split(',')
            for name_part in potential_names:
                clean_name = name_part.strip(' ,')
                if clean_name:
                    authors_data.append({'name': clean_name, 'url': None})
    return authors_data

# --- Extract abstract content from publication url ---
def extract_abstract_from_detail_page(soup):
    # Find the specific div containing the abstract
    abstract_div = soup.find('div', class_='rendering_researchoutput_abstractportal')
    if abstract_div:
        # The text is within a nested 'textblock' div
        text_block = abstract_div.find('div', class_='textblock')
        if text_block:
            return text_block.get_text(strip=True)
    return '' # Return empty string if abstract is not found

# --- Main Crawler Function ---
async def crawl():
    """
    Crawls the Coventry University publications portal, respecting robots.txt.
    It follows a BFS approach for pagination and extracts publication details.
    """
    print("Starting crawler with Playwright...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)

        # robots.txt parsing
        rp = robotparser.RobotFileParser()
        robots_url = urljoin(BASE_URL, 'robots.txt')
        print(f"Fetching robots.txt from: {robots_url}")
        
        page_robots = await context.new_page()
        try:
            await page_robots.goto(robots_url, timeout=PAGE_TIMEOUT)
            robots_content = await page_robots.content()
            soup_robots = BeautifulSoup(robots_content, 'html.parser')
            robots_text = soup_robots.get_text()

            print("\n--- Actual robots.txt content being parsed ---")
            print(robots_text)
            print("----------------------------------------------\n")
            
            rp.parse(robots_text.splitlines())
            print("robots.txt parsed successfully.")
        except Error as e:
            print(f"Warning: Could not fetch or parse robots.txt with Playwright. Proceeding with default settings. Error: {e}")
        finally:
            await page_robots.close()
        
        crawl_delay = rp.crawl_delay(USER_AGENT)
        robots_delay = int(crawl_delay) if crawl_delay else None
        user_min_delay = 2
        
        if robots_delay and robots_delay > user_min_delay:
            effective_delay_min = robots_delay
            print(f"Using Crawl-Delay from robots.txt: {effective_delay_min} seconds.")
        else:
            effective_delay_min = user_min_delay
            print(f"Using configured minimum delay: {effective_delay_min} seconds.")

        # Ensure the data directory exists
        data_dir = os.path.dirname(CRAWLED_DATA_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # PHASE 1: DISCOVER ALL PUBLICATION URLS
        print("\n--- Phase 1: Discovering all publication URLs ---")
        publications_to_scrape = []
        queue = deque([SEED_URL])
        visited_urls = {SEED_URL}
        
        pbar_pages = tqdm(total=16, desc="Scanning Pages")

        while queue:
            current_url = queue.popleft()

            # Check if URL is allowed by robots.txt before fetching
            if not rp.can_fetch(USER_AGENT, current_url):
                print(f"\nSkipping disallowed URL (from robots.txt): {current_url}")
                pbar_pages.update(1)
                continue

            page = await context.new_page()
            
            success = False
            for attempt in range(MAX_RETRIES):
                try:
                    await page.goto(current_url, wait_until='domcontentloaded', timeout=PAGE_TIMEOUT)
                    if len(visited_urls) == 1:
                        await page.click("#onetrust-accept-btn-handler", timeout=5000)
                except Error:
                    pass

                try:
                    await page.wait_for_selector('li.list-result-item', state='visible', timeout=30000)
                    success = True
                    break
                except Error as e:
                    print(f"\nAttempt {attempt + 1}/{MAX_RETRIES} failed for {current_url}: {e}")
                    if attempt < MAX_RETRIES - 1:
                        print('Retrying...')
                        # Wait before retrying, respecting the effective delay
                        delay = random.uniform(effective_delay_min, effective_delay_min + 2.0)
                        await asyncio.sleep(delay)

            if not success:
                print(f"All retries failed for {current_url}. Skipping page.")
                await page.close()
                pbar_pages.update(1)
                continue

            soup = BeautifulSoup(await page.content(), 'html.parser')
            # Find all publication items on the page
            pub_list = soup.find_all('li', class_='list-result-item')
            for pub_item in pub_list:
                if isinstance(pub_item, Tag):
                    title_tag = pub_item.find('h3', class_='title')
                    if isinstance(title_tag, Tag) and title_tag.a:
                        title = title_tag.get_text(strip=True)
                        pub_url = urljoin(BASE_URL, str(title_tag.a['href']))
                        date_tag = pub_item.find('span', class_='date')
                        date = date_tag.get_text(strip=True) if date_tag else "N/A"
                        publications_to_scrape.append({'title': title, 'url': pub_url, 'date': date})

            next_page_tag = soup.find('a', class_='nextLink')
            if isinstance(next_page_tag, Tag) and 'href' in next_page_tag.attrs:
                next_page_url = urljoin(BASE_URL, str(next_page_tag['href']))
                if next_page_url not in visited_urls:
                    visited_urls.add(next_page_url)
                    queue.append(next_page_url)
            
            pbar_pages.update(1)
            await page.close()

            # Polite crawling: wait before the next request using the effective delay
            delay = random.uniform(effective_delay_min, effective_delay_min + 2.0)
            await asyncio.sleep(delay)
        
        pbar_pages.close()
        print(f"--- Discovery complete. Found {len(publications_to_scrape)} publications to scrape. ---")

        # PHASE 2: SCRAPE AUTHOR DETAILS AND ABSTRACT FOR EACH PUBLICATION
        print("\n--- Phase 2: Scraping author details and abstract for each publication ---")
        final_publications = []
        for pub_data in tqdm(publications_to_scrape, desc="Scraping Author Details and Abstract"):
            # Check if URL is allowed by robots.txt before fetching
            if not rp.can_fetch(USER_AGENT, pub_data['url']):
                print(f"\nSkipping disallowed URL (from robots.txt): {pub_data['url']}")
                continue

            page = await context.new_page()
            try:
                success = False
                # --- RETRY LOGIC FOR DETAIL PAGES ---
                for attempt in range(MAX_RETRIES):
                    try:
                        await page.goto(pub_data['url'], wait_until='domcontentloaded', timeout=PAGE_TIMEOUT)
                        await page.wait_for_selector('p.relations.persons', state='visible', timeout=30000)
                        
                        detail_soup = BeautifulSoup(await page.content(), 'html.parser')
                        pub_data['authors'] = extract_authors_from_detail_page(detail_soup, BASE_URL)
                        pub_data['abstract'] = extract_abstract_from_detail_page(detail_soup)
                        success = True
                        break # Success, so exit retry loop
                    except Error as e:
                        print(f"\nAttempt {attempt + 1}/{MAX_RETRIES} failed for {pub_data['url']}: {e}")
                        if attempt < MAX_RETRIES - 1:
                            print('Retrying...')
                            # Wait before retrying, respecting the effective delay
                            delay = random.uniform(effective_delay_min, effective_delay_min + 2.0)
                            await asyncio.sleep(delay)
                
                if not success:
                    print(f"All retries failed for {pub_data['url']}. Saving without author details and abstract.")
                    pub_data['authors'] = [] # Ensure authors key exists even on failure
                    pub_data['abstract'] = '' # Ensure abstract key exists even on failure
                
                final_publications.append(pub_data)
            
            finally:
                await page.close()
                # --- RANDOMIZED DELAY BETWEEN EACH DETAIL PAGE SCRAPE ---
                delay = random.uniform(effective_delay_min, effective_delay_min + 2.0)
                await asyncio.sleep(delay)
        
        print("\nClosing Playwright browser.")
        await browser.close()

    # Save the extracted data to a file
    with open(CRAWLED_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_publications, f, indent=4, ensure_ascii=False)

    print(f"\nCrawling complete. Found {len(final_publications)} publications.")
    print(f"Data saved to {CRAWLED_DATA_FILE}")

if __name__ == '__main__':
    asyncio.run(crawl())