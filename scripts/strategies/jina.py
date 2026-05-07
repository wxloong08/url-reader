"""Jina Reader fetch strategy."""

import requests
from scripts.strategies import FetchStrategy
from scripts import config
from scripts.content import detect_verification_page


class JinaStrategy(FetchStrategy):

    name = "Jina Reader"

    def fetch(self, url: str, platform: dict) -> dict:
        try:
            jina_url = f"{config.JINA_BASE_URL}{url}"
            headers = {
                'Accept': 'text/markdown',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }

            response = requests.get(jina_url, headers=headers, timeout=config.TIMEOUT)

            if response.status_code == 200:
                content = response.text

                if detect_verification_page(content):
                    return {'success': False, 'error': '页面需要验证'}

                if len(content) < 100:
                    return {'success': False, 'error': '内容太短，可能读取失败'}

                if _is_blocked_page(content):
                    return {'success': False, 'error': '被目标网站屏蔽'}

                return {
                    'success': True,
                    'strategy': self.name,
                    'content': content,
                    'metadata': {},
                }

            return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': f'Jina 错误: {e}'}


def _is_blocked_page(content: str) -> bool:
    """Detect anti-bot / blocked pages that returned HTTP 200."""
    lowered = content.lower()[:500]
    blocked_signals = (
        "you've been blocked by network security",
        "you have been blocked",
        "access denied",
        "please prove you are not a bot",
        "are you a robot",
        "captcha",
        "verify you are human",
        "too many requests",
    )
    return any(signal in lowered for signal in blocked_signals)
