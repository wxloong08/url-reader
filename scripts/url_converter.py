"""
WeChat URL converter — long-form URL to short-form.
Standalone utility; no internal imports.
"""

import asyncio
import re
import sys
from urllib.parse import urlparse, parse_qs


async def convert_long_to_short(long_url: str) -> str:
    """
    Convert a WeChat long URL to its short form via Playwright.
    Returns the original URL if conversion fails.
    """
    from playwright.async_api import async_playwright

    print(f"正在转换: {long_url[:80]}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_extra_http_headers({
            'User-Agent': (
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
                'MicroMessenger/8.0.38'
            ),
        })

        try:
            await page.goto(long_url, wait_until="domcontentloaded", timeout=15000)
            final_url = page.url

            # Already a short URL?
            if '/s/' in final_url and '?' not in final_url.split('/s/')[1].split('#')[0]:
                await browser.close()
                return final_url

            # Try meta / canonical tags
            short_url = await page.evaluate("""
                () => {
                    const ogUrl = document.querySelector('meta[property="og:url"]');
                    if (ogUrl) return ogUrl.content;
                    const canonical = document.querySelector('link[rel="canonical"]');
                    if (canonical) return canonical.href;
                    return null;
                }
            """)

            if short_url and '/s/' in short_url:
                await browser.close()
                return short_url

            # Try page source patterns
            content = await page.content()
            patterns = [
                r'var\s+msg_link\s*=\s*["\']([^"\']+)["\']',
                r'href="(https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+)"',
                r'"url":"(https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    found = match.group(1).replace('\\/', '/')
                    if '/s/' in found and len(found.split('/s/')[1]) > 10:
                        await browser.close()
                        return found

            await browser.close()
            return final_url

        except Exception as e:
            await browser.close()
            print(f"转换失败: {e}")
            return long_url


def is_long_url(url: str) -> bool:
    """Check whether *url* is a WeChat long-form link."""
    parsed = urlparse(url)
    if 'mp.weixin.qq.com' not in parsed.netloc:
        return False
    query = parse_qs(parsed.query)
    return '__biz' in query or 'mid' in query


def extract_short_id(url: str) -> str | None:
    """Extract the short ID from a WeChat short URL."""
    match = re.search(r'/s/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None


# ---- CLI ----

async def _main():
    if len(sys.argv) < 2:
        print("用法: python -m scripts.url_converter <长链接>")
        return

    long_url = sys.argv[1]

    if not is_long_url(long_url):
        short_id = extract_short_id(long_url)
        if short_id:
            print(f"已经是短链接格式: https://mp.weixin.qq.com/s/{short_id}")
            return
        print("错误: 不是有效的微信公众号链接")
        return

    short_url = await convert_long_to_short(long_url)
    print(f"\n短链接: {short_url}")
    short_id = extract_short_id(short_url)
    if short_id:
        print(f"文章ID: {short_id}")


if __name__ == "__main__":
    asyncio.run(_main())
