"""
JD.com product page full dump via CDP.
Dumps the entire page text to a file for analysis.
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def dump_jd_page(page, url: str, output_file: str):
    """Navigate to JD page and dump full text."""
    print(f"Loading: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(8000)

    title = await page.title()
    print(f"Title: {title}")

    # Scroll through the page to trigger lazy loading
    for i in range(5):
        await page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {0.2 * (i+1)})")
        await page.wait_for_timeout(1000)

    # Try to click specs tab
    try:
        tabs = await page.query_selector_all("ul.tab-main li, #detail ul li, .tab-con li")
        for tab in tabs:
            txt = (await tab.inner_text()).strip()
            if "规格" in txt:
                await tab.click()
                await page.wait_for_timeout(3000)
                print(f"Clicked: {txt}")
                break
    except Exception as e:
        print(f"Tab error: {e}")

    # Dump full body text
    body = await page.evaluate("() => document.body.innerText")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n")
        f.write(f"Title: {title}\n")
        f.write("="*60 + "\n\n")
        f.write(body)
    
    print(f"Saved {len(body)} chars to {output_file}")


async def main():
    urls = sys.argv[1:]
    if not urls:
        print("Usage: python scripts/jd_dump.py <url1> [url2] ...")
        return

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        print("Connected to Chrome!")
        
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        page = await context.new_page()

        for i, url in enumerate(urls, 1):
            await dump_jd_page(page, url, f"product{i}_dump.txt")

        await page.close()
        print(f"\nDone! Saved {len(urls)} product dump(s).")


if __name__ == "__main__":
    asyncio.run(main())

