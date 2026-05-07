"""
JD.com product specs extractor via CDP (Chrome DevTools Protocol).
Connects to an already-running Chrome instance with --remote-debugging-port=9222.
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def get_jd_specs(page, url: str, label: str):
    """Navigate to a JD product URL and extract specs."""
    print(f"\n{'='*60}")
    print(f"=== {label} ===")
    print(f"Loading: {url}")
    print(f"{'='*60}\n")

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(8000)

    title = await page.title()
    print(f"Page title: {title}")

    # Product name
    name = await page.evaluate("""() => {
        const el = document.querySelector('.sku-name');
        return el ? el.innerText.trim() : 'N/A';
    }""")
    print(f"\n【产品名称】{name}")

    # Price
    price = await page.evaluate("""() => {
        const el = document.querySelector('.p-price .price') ||
                   document.querySelector('.p-price span');
        return el ? el.innerText.trim() : 'N/A';
    }""")
    print(f"【价格】{price}")

    # Key parameter summary (left-side list)
    summary = await page.evaluate("""() => {
        const items = document.querySelectorAll('.p-parameter li, .parameter2 li');
        return Array.from(items).map(li => li.innerText.trim()).join('\\n');
    }""")
    if summary:
        print(f"\n--- 商品参数概览 ---\n{summary}")

    # Scroll down to load detail section
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
    await page.wait_for_timeout(3000)

    # Click on 规格与包装 tab
    tab_clicked = False
    try:
        tabs = await page.query_selector_all("#detail .tab-main li, .tab-main .tab-item, #detail ul li")
        for tab in tabs:
            txt = await tab.inner_text()
            if "规格" in txt:
                await tab.click()
                await page.wait_for_timeout(3000)
                tab_clicked = True
                print(f"\n[Clicked tab: '{txt}']")
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
                    const key = dt.innerText.trim();
                    const val = dd.innerText.trim();
                    if (key && val) results.push('  ' + key + ': ' + val);
                }
            });
        });
        return results.join('\\n');
    }""")

    if specs and len(specs) > 50:
        print(f"\n--- 详细规格参数 ---{specs}")
    else:
        # Fallback: raw detail section text
        detail = await page.evaluate("""() => {
            const el = document.querySelector('#detail');
            if (!el) return '';
            return el.innerText.substring(0, 6000);
        }""")
        if detail and len(detail) > 100:
            print(f"\n--- 详情区域 ---\n{detail[:5000]}")
        else:
            # Last fallback: full body text
            body = await page.evaluate("() => document.body.innerText.substring(0, 8000)")
            print(f"\n--- 页面全文 ---\n{body}")

    # Get packaging info if available
    packaging = await page.evaluate("""() => {
        const results = [];
        const items = document.querySelectorAll('.package-list li, .Ptable-item:last-child dl');
        items.forEach(item => {
            results.push(item.innerText.trim());
        });
        return results.join('\\n');
    }""")
    if packaging and len(packaging) > 20:
        print(f"\n--- 包装信息 ---\n{packaging}")


async def main():
    urls = sys.argv[1:] if len(sys.argv) > 1 else []
    if not urls:
        print("Usage: python scripts/jd_cdp.py <url1> [url2] ...")
        return

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected to Chrome via CDP!")
        except Exception as e:
            print(f"Failed to connect to Chrome: {e}")
            print("Make sure Chrome is running with --remote-debugging-port=9222")
            return

        # Use existing context or create new page
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
        else:
            context = await browser.new_context()

        page = await context.new_page()

        for i, url in enumerate(urls):
            await get_jd_specs(page, url, f"Product {i+1}")

        await page.close()
        # Don't close the browser — it's the user's Chrome!


if __name__ == "__main__":
    asyncio.run(main())
