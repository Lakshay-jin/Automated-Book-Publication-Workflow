import os
import re
import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from playwright.sync_api import sync_playwright
from chroma_manager import add_version
from status_tracker import update_status

BASE_URL = "https://en.wikisource.org/wiki/The_Gates_of_Morning"
OUTPUT_DIR = "book_output"

def get_chapter_links(page, base_url=BASE_URL):
    chapter_links = []
    links = page.query_selector_all("div#mw-content-text a")
    for link in links:
        href = link.get_attribute("href")
        if href and "/wiki/The_Gates_of_Morning/Book_1/Chapter_" in href:
            full_url = f"https://en.wikisource.org{href}"
            chapter_links.append(full_url)
    return sorted(set(chapter_links))  # Remove duplicates and sort

def process_chapter(url, chapter_num):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=60000)

            try:
                page.wait_for_selector("div#mw-content-text", timeout=15000)
            except:
                print(f"⚠️ Skipping Chapter {chapter_num}: No content found at {url}")
                browser.close()
                return

            content = page.inner_text("div#mw-content-text")

            # Save raw text
            raw_path = os.path.join(OUTPUT_DIR, f"chapter_{chapter_num:02d}_raw.txt")
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Screenshot
            screenshot_path = os.path.join(OUTPUT_DIR, f"chapter_{chapter_num:02d}.png")
            page.screenshot(path=screenshot_path, full_page=True)

            browser.close()
            print(f"✅ Chapter {chapter_num} scraped.")

            update_status(f"chapter_{chapter_num:02d}", "scraped", metadata={"title": chapter_num})


            add_version(
                chapter_id=f"chapter_{chapter_num:02d}",
                stage="raw",
                text=content,
                metadata={"source": "scraper"}
            )
            
    except Exception as e:
        return "error"
    

def scrape_entire_book(URL):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        chapter_urls = get_chapter_links(page,URL)
        browser.close()

    print(f"🔍 Found {len(chapter_urls)} chapters")
    for i, url in enumerate(chapter_urls, start=1):
        if(process_chapter(url, i)=="error"):
            return "error"
    return "success"
