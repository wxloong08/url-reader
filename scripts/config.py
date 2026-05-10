"""
Centralized configuration for URL Reader.
Precedence: env vars > .env file > config.json > defaults.
"""

import os
import json
from pathlib import Path

# ---------- .env support (optional) ----------

try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
CONFIG_FILE = PROJECT_DIR / "config.json"

# ---------- defaults ----------

_DEFAULTS = {
    "firecrawl_api_key": "",
    "jina_base_url": "https://r.jina.ai/",
    "output_dir": str(Path.home() / "url-reader-output"),
    "timeout": 30,
    "headless": True,
    "forum_max_pages": 8,
    "cloakbrowser_enabled": False,
    "cloakbrowser_binary_path": "",
    "cloakbrowser_backend": "playwright",
    "wechat_auth_file": str(DATA_DIR / "wechat_auth.json"),
}

# ---------- config.json layer ----------

def _load_config_file() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

_file_cfg = _load_config_file()

# ---------- env var mapping ----------

_ENV_MAP = {
    "firecrawl_api_key": "FIRECRAWL_API_KEY",
    "jina_base_url": "URL_READER_JINA_BASE_URL",
    "output_dir": "URL_READER_OUTPUT_DIR",
    "timeout": "URL_READER_TIMEOUT",
    "headless": "URL_READER_HEADLESS",
    "forum_max_pages": "URL_READER_FORUM_MAX_PAGES",
    "cloakbrowser_enabled": "URL_READER_CLOAKBROWSER_ENABLED",
    "cloakbrowser_binary_path": "CLOAKBROWSER_BINARY_PATH",
    "cloakbrowser_backend": "CLOAKBROWSER_BACKEND",
}


def get(key: str):
    """
    Retrieve a config value.  Precedence: env > config.json > default.
    """
    # env layer
    env_name = _ENV_MAP.get(key)
    if env_name:
        env_val = os.environ.get(env_name)
        if env_val is not None:
            default = _DEFAULTS.get(key)
            if isinstance(default, bool):
                return env_val.lower() in ("1", "true", "yes")
            if isinstance(default, int):
                try:
                    return int(env_val)
                except ValueError:
                    pass
            return env_val

    # config.json layer
    if key in _file_cfg:
        return _file_cfg[key]

    # default layer
    return _DEFAULTS.get(key)


# convenience accessors
FIRECRAWL_API_KEY: str = get("firecrawl_api_key")
JINA_BASE_URL: str = get("jina_base_url")
OUTPUT_DIR: str = get("output_dir")
TIMEOUT: int = get("timeout")
HEADLESS: bool = get("headless")
FORUM_MAX_PAGES: int = get("forum_max_pages")
CLOAKBROWSER_ENABLED: bool = get("cloakbrowser_enabled")
CLOAKBROWSER_BINARY_PATH: Path | None = Path(get("cloakbrowser_binary_path")) if get("cloakbrowser_binary_path") else None
CLOAKBROWSER_BACKEND: str = get("cloakbrowser_backend")
WECHAT_AUTH_FILE: Path = Path(get("wechat_auth_file"))
