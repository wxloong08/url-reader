"""
WeChat authentication setup and status check.
Consolidated from wechat_reader.py and wechat_reader_v2.py.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from scripts import config

AUTH_FILE: Path = config.WECHAT_AUTH_FILE
DATA_DIR: Path = config.DATA_DIR


async def setup(wait_seconds: int = 120):
    """Launch browser for WeChat QR-code login; save auth state."""
    from playwright.async_api import async_playwright

    print("正在启动浏览器，请扫码登录微信...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://mp.weixin.qq.com/")

        print("\n请在浏览器中完成以下操作：")
        print("1. 点击右上角「登录」")
        print("2. 使用微信扫码登录")
        print(f"3. 登录成功后会自动保存（等待 {wait_seconds} 秒）")
        print("\n等待登录中...")

        try:
            await page.wait_for_selector(
                ".weui-desktop-account__nickname",
                timeout=wait_seconds * 1000,
            )
            print("检测到登录成功！")
        except Exception:
            print("等待超时，尝试保存当前状态...")

        storage = await context.storage_state()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(AUTH_FILE, 'w', encoding='utf-8') as f:
            json.dump(storage, f, ensure_ascii=False, indent=2)

        await browser.close()

    print(f"认证状态已保存到: {AUTH_FILE}")
    return True


async def status() -> bool:
    """Print auth file status; return True if file exists."""
    if not AUTH_FILE.exists():
        print("未找到认证状态")
        print("运行: python -m scripts.wechat_auth setup")
        return False

    mtime = datetime.fromtimestamp(AUTH_FILE.stat().st_mtime)
    age = datetime.now() - mtime

    print(f"认证文件存在")
    print(f"  路径: {AUTH_FILE}")
    print(f"  创建时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  已过去: {age.days} 天 {age.seconds // 3600} 小时")

    if age.days > 7:
        print("\n认证可能已过期，建议重新登录")

    return True


async def save_auth_from_context(context):
    """Save auth state from an existing Playwright browser context."""
    storage = await context.storage_state()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump(storage, f, ensure_ascii=False, indent=2)
    print("认证状态已保存")


# ---- CLI entry point ----

async def _main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m scripts.wechat_auth setup    # 首次登录")
        print("  python -m scripts.wechat_auth status   # 检查认证状态")
        return

    command = sys.argv[1]
    if command == "setup":
        await setup()
    elif command == "status":
        await status()
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    asyncio.run(_main())
