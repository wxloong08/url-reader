"""
JD.com product specs extractor — uses user's Chrome profile for login state.
Usage: python scripts/jd_specs.py <url1> [url2] ...
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright


async def get_jd_specs(page, url: str, label: str):
    """Extract specs from a single JD.com product page."""
    print(f"\n{'='*60}")
    print(f"=== {label} ===")
    print(f"Loading: {url}")
    print(f"{'='*60}\n")

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(5000)

    title = await page.title()
    print(f"Page title: {title}")

    # Get product name
    name = await page.evaluate("""() => {
        const el = document.querySelector('.sku-name');
        return el ? el.innerText.trim() : 'N/A';
    }""")
    print(f"\nProduct name: {name}")

    # Get price
    price = await page.evaluate("""() => {
        const el = document.querySelector('.p-price .price') ||
                   document.querySelector('.price-box .price') ||
                   document.querySelector('.summary-price-wrap .price') ||
                   document.querySelector('.p-price');
        return el ? el.innerText.trim() : 'N/A (need login)';
    }""")
    print(f"Price: {price}")

    # Get key parameter summary
    summary = await page.evaluate("""() => {
        const items = document.querySelectorAll('.p-parameter li, .parameter2 li');
        return Array.from(items).map(li => li.innerText.trim()).join('\\n');
    }""")
    if summary:
        print(f"\n--- Key Parameters ---\n{summary}")

    # Scroll to detail section
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.4)")
    await page.wait_for_timeout(2000)

    # Find and click specs tab
    try:
        tabs = await page.query_selector_all("#detail .tab-main li, .tab-main .tab-item")
        for tab in tabs:
            txt = await tab.inner_text()
            if "规格" in txt:
                await tab.click()
                await page.wait_for_timeout(2000)
                print(f"\nClicked tab: '{txt}'")
                break
    except Exception as e:
        print(f"Tab click error: {e}")

    # Extract Ptable specs
    specs = await page.evaluate("""() => {
        const results = [];
        const items = document.querySelectorAll('.Ptable-item');
        items.forEach(item => {
            const h3 = item.querySelector('h3');
            if (h3) results.push('\\n## ' + h3.innerText.trim());
            const rows = item.querySelectorAll('dl');
            rows.forEach(row => {
                const dt = row.querySelector('dt');
                const dd = row.querySelector('dd');
                if (dt && dd) {
                    results.push('  ' + dt.innerText.trim() + ': ' + dd.innerText.trim());
                }
            });
        });
        return results.join('\\n');
    }""")

    if specs and len(specs) > 50:
        print(f"\n--- Detailed Specifications ---{specs}")
    else:
        # Fallback: get the entire detail area text
        detail = await page.evaluate("""() => {
            const el = document.querySelector('#detail') || document.querySelector('.product-detail');
            return el ? el.innerText.substring(0, 5000) : '';
        }""")
        if detail:
            print(f"\n--- Detail Section ---\n{detail}")
        else:
            # Last resort: get body text
            body = await page.evaluate("() => document.body.innerText.substring(0, 5000)")
            print(f"\n--- Page Body ---\n{body}")


async def main():
    urls = sys.argv[1:] if len(sys.argv) > 1 else []
    if not urls:
        print("Usage: python scripts/jd_specs.py <url1> [url2] ...")
        return

    # Use user's Chrome profile for login cookies
    chrome_data = os.path.expanduser("~") + "/AppData/Local/Google/Chrome/User Data"
    
    async with async_playwright() as p:
        # Launch with persistent context (uses Chrome cookies/login state)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=chrome_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--profile-directory=Default",
            ],
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        
        page = context.pages[0] if context.pages else await context.new_page()

        for i, url in enumerate(urls):
            await get_jd_specs(page, url, f"Product {i+1}")

        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
