"""
Save content to disk and download images.
"""

import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from scripts import config
from scripts.content import sanitize_filename, extract_title, extract_images


# ---- platform-aware referer ----

_REFERER_MAP = [
    ('sns-webpic', 'https://www.xiaohongshu.com/'),
    ('xiaohongshu', 'https://www.xiaohongshu.com/'),
    ('mmbiz.qpic.cn', 'https://mp.weixin.qq.com/'),
    ('feishu', 'https://www.feishu.cn/'),
    ('sinaimg', 'https://weibo.com/'),
    ('bilibili', 'https://www.bilibili.com/'),
]


def _determine_referer(image_url: str) -> str:
    """Pick a Referer header based on the image URL pattern."""
    for pattern, referer in _REFERER_MAP:
        if pattern in image_url:
            return referer
    return ''


def download_image(url: str, save_dir: Path, index: int) -> str | None:
    """Download a single image; return local filename or None."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        referer = _determine_referer(url)
        if referer:
            headers['Referer'] = referer

        response = requests.get(url, headers=headers, timeout=config.TIMEOUT)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'webp' in content_type or 'webp' in url:
            ext = '.webp'
        elif 'png' in content_type or 'png' in url:
            ext = '.png'
        elif 'gif' in content_type or 'gif' in url:
            ext = '.gif'
        else:
            ext = '.jpg'

        filename = f"img_{index:02d}{ext}"
        filepath = save_dir / filename

        with open(filepath, 'wb') as f:
            f.write(response.content)

        return filename

    except Exception:
        return None


def save(
    content: str,
    url: str,
    platform_name: str = "",
    output_dir: str | None = None,
    title: str | None = None,
    verbose: bool = True,
) -> dict:
    """
    Save Markdown content and its images to disk.

    Returns dict with: success, dir, md_file, images, title.
    """
    out = Path(output_dir or config.OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    if not title:
        title = extract_title(content)

    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{date_str}_{sanitize_filename(title)}"
    content_dir = out / folder_name
    content_dir.mkdir(parents=True, exist_ok=True)

    images = extract_images(content)
    image_mapping: dict[str, str] = {}

    if images and verbose:
        print(f"发现 {len(images)} 张图片，正在下载...")

    for i, img_url in enumerate(images, 1):
        local = download_image(img_url, content_dir, i)
        if local:
            image_mapping[img_url] = local
            if verbose:
                print(f"  {local}")

    updated_content = content
    for orig, local in image_mapping.items():
        updated_content = updated_content.replace(orig, local)

    meta = (
        f"---\n"
        f"title: {title}\n"
        f"platform: {platform_name}\n"
        f"url: {url}\n"
        f"saved_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"images: {len(image_mapping)}\n"
        f"---\n\n"
    )

    md_path = content_dir / "content.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(meta + updated_content)

    if verbose:
        print(f"\n已保存到: {content_dir}")
        print(f"   - content.md")
        print(f"   - 图片: {len(image_mapping)} 张")

    return {
        'success': True,
        'dir': str(content_dir),
        'md_file': str(md_path),
        'images': len(image_mapping),
        'title': title,
    }
