"""
Playwright fetch strategy — handles generic pages and WeChat articles.
Consolidates logic from url_reader.py, wechat_reader.py, and wechat_reader_v2.py.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from scripts.strategies import FetchStrategy
from scripts import config
from scripts.content import detect_verification_page

MOBILE_UA = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
    'MicroMessenger/8.0.38(0x18002629) NetType/WIFI Language/zh_CN'
)

DESKTOP_UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
)


class PlaywrightStrategy(FetchStrategy):

    name = "Playwright"

    # ---- public interface ----

    def fetch(self, url: str, platform: dict) -> dict:
        """Sync wrapper that safely runs the async implementation."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Already inside an event loop — offload to a thread.
            with ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self._fetch_async(url, platform)).result()
        return asyncio.run(self._fetch_async(url, platform))

    # ---- async implementation ----

    async def _fetch_async(self, url: str, platform: dict) -> dict:
        try:
            from playwright.async_api import async_playwright

            auth_file = None
            if platform.get('id') == 'wechat' and config.WECHAT_AUTH_FILE.exists():
                auth_file = str(config.WECHAT_AUTH_FILE)

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=config.HEADLESS)

                ctx_kwargs = {'user_agent': self._get_user_agent(platform)}
                if auth_file:
                    ctx_kwargs['storage_state'] = auth_file

                context = await browser.new_context(**ctx_kwargs)
                page = await context.new_page()

                await page.goto(
                    url,
                    wait_until=self._get_wait_until(platform),
                    timeout=self._get_navigation_timeout(platform),
                )
                await self._wait_for_page_ready(page, platform)

                # --- verification check ---
                page_html = await page.content()
                if detect_verification_page(page_html) or self._is_finance_stock_block(page_html):
                    verify_btn = await page.query_selector("text=去验证")
                    if verify_btn:
                        await verify_btn.click()
                        await page.wait_for_timeout(3000)
                        await page.wait_for_load_state("networkidle", timeout=15000)
                        page_html = await page.content()

                    if detect_verification_page(page_html):
                        await browser.close()
                        return {
                            'success': False,
                            'error': '需要手动验证，请运行 wechat_auth setup 登录',
                        }

                # --- content extraction ---
                if platform.get('id') == 'wechat':
                    result = await self._extract_wechat(page)
                elif self._is_finance_stock_page(platform):
                    result = await self._extract_finance_stock(page)
                else:
                    result = await self._extract_generic(page)

                await browser.close()

                if result.get('content') and len(result['content']) > 100:
                    markdown = f"# {result.get('title', '无标题')}\n\n"
                    if result.get('author'):
                        markdown += f"**作者**: {result['author']}\n"
                    if result.get('publishTime'):
                        markdown += f"**发布时间**: {result['publishTime']}\n"
                    markdown += f"\n---\n\n{result['content']}"

                    return {
                        'success': True,
                        'strategy': self.name,
                        'content': markdown,
                        'metadata': {
                            'title': result.get('title', ''),
                            'author': result.get('author', ''),
                            'publishTime': result.get('publishTime', ''),
                        },
                    }

                return {'success': False, 'error': '页面内容提取失败'}

        except Exception as e:
            return {'success': False, 'error': f'Playwright 错误: {e}'}

    def _get_navigation_timeout(self, platform: dict) -> int:
        if self._is_finance_stock_page(platform):
            return 15000
        return config.TIMEOUT * 1000

    def _get_wait_until(self, platform: dict) -> str:
        if self._is_finance_stock_page(platform):
            return "domcontentloaded"
        return "networkidle"

    def _get_user_agent(self, platform: dict) -> str:
        if self._is_finance_stock_page(platform):
            return DESKTOP_UA
        return MOBILE_UA

    async def _wait_for_page_ready(self, page, platform: dict) -> None:
        if self._is_finance_stock_page(platform):
            try:
                await page.wait_for_selector('table', timeout=15000)
            except Exception:
                await page.wait_for_function(
                    "() => /\\d/.test(document.body?.innerText || '') && (document.body?.innerText || '').length > 200",
                    timeout=15000,
                )
            await page.wait_for_timeout(1000)
            return

        await page.wait_for_timeout(2000)

    @staticmethod
    def _is_finance_stock_page(platform: dict) -> bool:
        return platform.get('cleanup_profile') == 'finance_stock'

    @staticmethod
    def _is_finance_stock_block(page_html: str) -> bool:
        snippet = page_html[:3000]
        blocked_signals = (
            '请完成验证',
            '安全验证',
            '验证码',
            '访问受限',
            '请先登录后查看',
            '登录后查看',
        )
        return any(signal in snippet for signal in blocked_signals)

    # ---- platform-specific extractors ----

    @staticmethod
    async def _extract_wechat(page) -> dict:
        try:
            await page.wait_for_selector('#js_content', timeout=10000)
        except Exception:
            pass

        return await page.evaluate("""
            () => {
                const title = document.querySelector('#activity-name')?.innerText?.trim() || '';
                const author = document.querySelector('#js_name')?.innerText?.trim() || '';
                const content = document.querySelector('#js_content')?.innerText?.trim() || '';
                const publishTime = document.querySelector('#publish_time')?.innerText?.trim() || '';
                return { title, author, content, publishTime };
            }
        """)

    @staticmethod
    async def _extract_generic(page) -> dict:
        return await page.evaluate("""
            () => {
                const title = document.querySelector('h1')?.innerText?.trim()
                             || document.querySelector('title')?.innerText?.trim() || '';
                const content = document.body.innerText || '';
                return { title, author: '', content, publishTime: '' };
            }
        """)

    @staticmethod
    async def _extract_finance_stock(page) -> dict:
        return await page.evaluate("""
            () => {
                const title = document.querySelector('h1')?.innerText?.trim()
                             || document.querySelector('title')?.innerText?.trim() || '';
                const text = document.body?.innerText?.trim() || '';
                const tables = Array.from(document.querySelectorAll('table'))
                  .map((table) => table.outerHTML)
                  .join('\\n\\n');
                const content = tables ? `${text}\\n\\n${tables}` : text;
                return { title, author: '', content, publishTime: '' };
            }
        """)
