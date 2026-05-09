"""
URL Reader — orchestrator / entry point.

Usage:
    python -m scripts.main <url>          # read and print
    python -m scripts.main <url> --save   # read and save
"""

import re
import sys

from scripts import config
from scripts.platforms import identify_platform
from scripts.strategies.firecrawl import FirecrawlStrategy
from scripts.strategies.jina import JinaStrategy
from scripts.strategies.opencli_browser import OpenCLIBrowserStrategy
from scripts.strategies.playwright_strategy import PlaywrightStrategy
from scripts.content import extract_forum_replies_page, postprocess_content
from scripts.formatter import format_result, format_saved_result
from scripts.saver import save

# strategy registry
_STRATEGIES = {
    'firecrawl': FirecrawlStrategy(),
    'jina': JinaStrategy(),
    'opencli_browser': OpenCLIBrowserStrategy(),
    'playwright': PlaywrightStrategy(),
}


def _filter_available_strategies(strategy_keys: list[str]) -> list[str]:
    """Remove strategies that cannot work in the current environment."""
    available = []
    for key in strategy_keys:
        if key == 'firecrawl':
            if not config.FIRECRAWL_API_KEY:
                continue
            try:
                import firecrawl  # noqa: F401
            except ImportError:
                continue
        available.append(key)
    if not available:
        return strategy_keys  # fallback: try everything
    return available


def read_url(url: str, verbose: bool = True) -> dict:
    """
    Read URL content using the platform's preferred strategy chain.
    Returns a result dict with 'success', 'content', 'platform', etc.
    """
    platform = identify_platform(url)
    if verbose:
        print(f"平台识别: {platform['name']}")

    strategies = _filter_available_strategies(platform['preferred_strategies'])
    errors = []

    for strategy_key in strategies:
        strategy = _STRATEGIES.get(strategy_key)
        if strategy is None:
            continue

        if verbose:
            print(f"尝试策略: {strategy.name}...")

        result = strategy.fetch(url, platform)

        if result.get('success'):
            content_for_postprocess = _prepare_content_for_postprocess(
                result.get('content', ''),
                result.get('metadata', {}),
                url,
            )
            processed = postprocess_content(content_for_postprocess, url, platform)
            if not processed.get('success'):
                errors.append(f"{strategy.name}: {processed.get('error')}")
                if verbose:
                    print(processed.get('error'))
                continue

            if verbose:
                print(f"{strategy.name} 读取成功")
            result['content'] = processed.get('content', result.get('content', ''))
            result['metadata'] = {
                **result.get('metadata', {}),
                **processed.get('metadata', {}),
            }
            result = _extend_forum_replies(result, url, platform, strategy, verbose=verbose)
            result['platform'] = platform
            return result

        errors.append(f"{strategy.name}: {result.get('error')}")
        if verbose:
            print(f"{result.get('error')}")

    return {
        'success': False,
        'platform': platform,
        'errors': errors,
    }


def _prepare_content_for_postprocess(content: str, metadata: dict, url: str) -> str:
    """Normalize non-Jina strategy output into the metadata envelope postprocess_content expects."""
    if 'Markdown Content:' in content:
        return content

    title = str(metadata.get('title', '')).strip()
    source_url = str(metadata.get('source_url', url)).strip() or url
    published = str(metadata.get('published_time') or metadata.get('publishTime') or '').strip()

    parts = []
    if title:
        parts.append(f'Title: {title}')
    if source_url:
        parts.append(f'URL Source: {source_url}')
    if published:
        parts.append(f'Published Time: {published}')
    parts.append('Markdown Content:')
    parts.append(content)
    return '\n\n'.join(parts)


def _extend_forum_replies(result: dict, url: str, platform: dict, strategy, verbose: bool = True) -> dict:
    """Fetch a bounded number of extra forum pages for long discussion threads."""
    if platform.get('id') not in {'lowendtalk', 'lowendspirit'}:
        return result

    if re.search(r'/p\d+$', url):
        return result

    if result.get('metadata', {}).get('content_type') != 'forum_thread':
        return result

    collected: list[dict[str, str]] = []
    pages_fetched = 0
    for page_num in range(2, config.FORUM_MAX_PAGES + 1):
        page_url = f'{url.rstrip("/")}/p{page_num}'
        page_result = strategy.fetch(page_url, platform)
        if not page_result.get('success'):
            break

        replies = extract_forum_replies_page(page_result.get('content', ''), page_url, platform)
        if not replies:
            break

        collected.extend(replies)
        pages_fetched += 1
        if verbose:
            print(f'补充抓取回复页: p{page_num} ({len(replies)} 条)')

    if not collected:
        return result

    base_content = result.get('content', '')
    existing_count = _count_existing_replies(base_content)
    result['content'] = _append_replies(base_content, collected, start_index=existing_count + 1)
    result['metadata'] = {
        **result.get('metadata', {}),
        'extra_reply_pages': pages_fetched,
        'extra_reply_count': len(collected),
    }
    return result


def _count_existing_replies(content: str) -> int:
    if '\n## 回复\n' not in content:
        return 0
    reply_block = content.split('\n## 回复\n', 1)[1]
    return len(re.findall(r'(?m)^\d+\.\s', reply_block))


def _append_replies(content: str, replies: list[dict[str, str]], start_index: int) -> str:
    lines = [content.rstrip()]
    if '\n## 回复\n' not in content:
        lines.extend(['', '## 回复', ''])

    index = start_index
    for reply in replies:
        lines.append(f'{index}. {reply["header"]}')
        lines.append(reply['body'])
        index += 1
    return '\n'.join(lines).strip()


def read_and_save(url: str, output_dir: str | None = None, verbose: bool = True) -> dict:
    """Read URL and save content + images to disk."""
    result = read_url(url, verbose=verbose)

    if not result.get('success'):
        return result

    platform = result.get('platform', {})
    formatted = format_saved_result(result, url)

    save_result = save(
        content=formatted,
        url=url,
        platform_name=platform.get('name', '未知'),
        output_dir=output_dir,
        verbose=verbose,
    )
    result['save'] = save_result
    return result


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("URL Reader - 智能网页内容读取器")
        print("=" * 60)
        print("\n用法:")
        print("  python -m scripts.main <url>              # 读取并显示")
        print("  python -m scripts.main <url> --save       # 读取并保存")
        print("\n示例:")
        print("  python -m scripts.main https://mp.weixin.qq.com/s/xxxxx --save")
        print("\n策略优先级: Firecrawl → OpenCLI → Jina → Playwright")
        print("  (未配置 API Key 或未安装依赖时自动跳过)")
        return

    url = sys.argv[1]
    save_mode = '--save' in sys.argv

    print(f"\n{'=' * 60}")
    print(f"正在读取: {url}")
    print(f"{'=' * 60}\n")

    if save_mode:
        result = read_and_save(url)
        if result.get('success') and result.get('save'):
            print(f"\n{'=' * 60}")
            print("读取并保存成功")
            print(f"{'=' * 60}")
    else:
        result = read_url(url)
        output = format_result(result, url)
        print(f"\n{'=' * 60}")
        print("读取结果")
        print(f"{'=' * 60}\n")
        print(output)


if __name__ == "__main__":
    main()
