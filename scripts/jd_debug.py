"""
JD.com product specs extractor.
Non-headless Playwright, desktop UA, long waits.
"""

import asyncio
import sys
from playwright.async_api import async_playwright

INIT_SCRIPT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"


async def get_jd_specs(url: str, label: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        await context.add_init_script(INIT_SCRIPT)

        page = await context.new_page()
        print(f"\n{'='*60}")
        print(f"=== {label} ===")
        print(f"{'='*60}\n")

        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(8000)

        title = await page.title()
        print(f"Page title: {title}")

        # Dump the body inner text to see what we get
        body = await page.evaluate("() => document.body.innerText")
        print(f"\n--- FULL PAGE TEXT (first 10000 chars) ---")
        print(body[:10000])

        # Also try to get the HTML structure of the detail area
        detail_html = await page.evaluate("""() => {
            const el = document.querySelector('#detail') || 
                       document.querySelector('.product-detail') ||
                       document.querySelector('.Ptable');
            return el ? el.outerHTML.substring(0, 5000) : 'NO DETAIL ELEMENT';
        }""")
        print(f"\n--- DETAIL HTML ---")
        print(detail_html[:3000])

        await browser.close()


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://item.jd.com/100155070908.html"
    await get_jd_specs(url, url.split("/")[-1].split(".")[0])


if __name__ == "__main__":
    asyncio.run(main())
