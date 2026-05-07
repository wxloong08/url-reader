---
name: url-reader
description: 智能读取任意URL内容，支持微信公众号、小红书等中国主流平台，自动保存Markdown和图片。
---

# URL Reader - 智能网页内容读取器

读取任意 URL 内容，自动识别平台，智能选择读取策略，保存内容和图片到本地。

## Claude 执行指南

当用户请求读取 URL 时，按以下步骤执行：

### 1. 读取并显示

```bash
cd D:\skills\url-reader
python -m scripts.main <url>
```

### 2. 读取并保存到默认目录

```bash
python -m scripts.main <url> --save
```

### 3. 读取并保存到指定目录

```bash
URL_READER_OUTPUT_DIR="D:\custom\path" python -m scripts.main <url> --save
```

### 4. WeChat 认证管理

```bash
# 首次登录（打开浏览器扫码）
python -m scripts.wechat_auth setup

# 检查认证状态
python -m scripts.wechat_auth status
```

### 5. WeChat 长链接转短链接

```bash
python -m scripts.url_converter "https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&sn=xxx"
```

## 多层读取策略（自动降级）

```
用户输入 URL
     ↓
┌─────────────┐
│ 平台识别器   │ → 识别 URL 所属平台
└─────────────┘
     ↓
┌─────────────────────────────────────┐
│           策略链                     │
│  Firecrawl → OpenCLI → Jina → Playwright │
│  自动跳过不可用策略，按平台优先级尝试    │
└─────────────────────────────────────┘
     ↓
┌─────────────┐
│ 格式化 + 保存│ → Markdown + 图片下载
└─────────────┘
```

### 策略 1：Firecrawl API

- AI 驱动的网页抓取，直接返回 Markdown
- 需要在 `.env` 或环境变量中设置 `FIRECRAWL_API_KEY`
- 免费额度：500 页/月
- 未配置 API Key 或未安装 `firecrawl-py` 时自动跳过

### 策略 2：OpenCLI Browser Extract

- 复用本机 `opencli browser extract` 的渲染与正文提取
- 中文站兼容性最好（Jina 常返回 451/503 的平台都能用）
- **2026-05-07 升级为全平台通用中层策略**，不再仅限知乎/Reddit

### 策略 3：Jina Reader API

- 完全免费，无需 API Key
- URL 前缀 `https://r.jina.ai/` 即可使用
- 适合不需要登录的平台
- 部分中文平台会返回 HTTP 451/503

### 策略 4：Playwright 浏览器自动化

- 支持登录态保持（WeChat 等）
- 移动端 User-Agent 模拟
- 需要首次手动登录

## 支持的平台

| 平台 | 域名 | 策略优先级 |
|------|------|-----------|
| 微信公众号 | mp.weixin.qq.com | Firecrawl → OpenCLI → Playwright → Jina |
| 小红书 | xiaohongshu.com | Firecrawl → OpenCLI → Jina → Playwright |
| 今日头条 | toutiao.com | Firecrawl → OpenCLI → Jina → Playwright |
| 抖音 | douyin.com | Firecrawl → OpenCLI → Jina → Playwright |
| 淘宝 | taobao.com | Firecrawl → OpenCLI → Playwright → Jina |
| 天猫 | tmall.com | Firecrawl → OpenCLI → Playwright → Jina |
| 京东 | jd.com | Firecrawl → OpenCLI → Jina → Playwright |
| 百度 | baidu.com | Firecrawl → OpenCLI → Jina → Playwright |
| 知乎 | zhihu.com | Firecrawl → OpenCLI → Jina → Playwright |
| 微博 | weibo.com | Firecrawl → OpenCLI → Playwright → Jina |
| X | x.com / twitter.com | Jina → OpenCLI → Playwright → Firecrawl |
| B站 | bilibili.com | Firecrawl → OpenCLI → Jina → Playwright |
| Reddit | reddit.com | Jina → OpenCLI → Playwright |
| V2EX | v2ex.com | Jina → OpenCLI → Playwright |
| MeowVPS | meowvps.com | Jina → OpenCLI → Playwright |
| HostLoc | hostloc.com | Jina → OpenCLI → Playwright |
| NodeSeek | nodeseek.com | Jina → OpenCLI → Playwright |
| LINUX DO | linux.do | Jina → OpenCLI → Playwright |
| LowEndTalk/Spirit | lowendtalk.com | Jina → OpenCLI → Playwright |
| 通用网站 | * | Firecrawl → OpenCLI → Jina → Playwright |

## 论坛帖子页支持

针对 `HostLoc`、`NodeSeek`、`LINUX DO`、`V2EX`、`LowEndTalk`、`LowEndSpirit` 的帖子详情页，系统会自动进入论坛帖子清洗模式：

- 优先保留主楼正文和回复内容
- 自动清理导航、版块列表、广告、登录提示、贴纸图片等噪音
- 自动过滤 `BD`、`支持`、`前排`、`ID + 谢谢老板` 这类低信息回复
- 对 `LowEndTalk` 这类可能返回 `Sign In` 页的场景，若未拿到公开帖子正文则直接判定失败，不把登录页误当内容返回

## 问答页支持

针对 `知乎 question` 页，系统会自动进入答案清洗模式：

- 只保留问题标题和当前已加载的公开回答
- 自动移除关注/浏览统计、热榜、客户端下载提示、侧栏推荐等噪音
- 优先使用 `OpenCLI Browser Extract` 作为 `Jina` 之后的兜底路径

## 配置

### .env 文件（推荐）

在项目根目录创建 `.env` 文件（已 gitignored）：

```bash
FIRECRAWL_API_KEY=fc-YOUR_KEY
```

### 环境变量（最高优先级）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FIRECRAWL_API_KEY` | Firecrawl API 密钥 | (空) |
| `URL_READER_OUTPUT_DIR` | 保存目录 | `~/url-reader-output` |
| `URL_READER_TIMEOUT` | HTTP 超时秒数 | 30 |
| `URL_READER_HEADLESS` | Playwright 无头模式 | true |
| `URL_READER_FORUM_MAX_PAGES` | 论坛帖子最多抓取页数 | 8 |

### config.json（次优先级）

在项目根目录创建 `config.json`（已 gitignored）：

```json
{
  "firecrawl_api_key": "fc-YOUR_KEY",
  "output_dir": "D:/custom/path",
  "timeout": 60,
  "forum_max_pages": 8
}
```

## 保存格式

```
output-dir/
└── 2026-01-30_文章标题/
    ├── content.md      # Markdown 内容（含 YAML front matter）
    ├── img_01.webp
    ├── img_02.jpg
    └── ...
```

## 目录结构

```
url-reader/
├── SKILL.md                    # 本文档
├── README.md                   # 人类可读概述
├── metadata.json               # 版本 2.0.0
├── config.json                 # 用户配置（gitignored）
├── .gitignore
├── scripts/
│   ├── __init__.py
│   ├── config.py               # 配置系统
│   ├── platforms.py            # 平台识别
│   ├── content.py              # 标题/图片提取，平台清洗
│   ├── formatter.py            # Markdown 输出格式化
│   ├── saver.py                # 保存到磁盘，下载图片
│   ├── wechat_auth.py          # WeChat 认证管理
│   ├── url_converter.py        # WeChat URL 转换
│   ├── benchmark.py            # 性能基准测试
│   ├── main.py                 # 入口/编排器
│   └── strategies/
│       ├── __init__.py         # FetchStrategy 基类
│       ├── firecrawl.py        # Firecrawl 策略
│       ├── jina.py             # Jina Reader 策略
│       ├── opencli_browser.py  # OpenCLI Browser 策略
│       └── playwright_strategy.py  # Playwright 策略
└── tests/
    ├── __init__.py
    ├── test_content.py         # 平台识别 + 清洗测试
    ├── test_formatter.py       # 格式化输出测试
    └── test_opencli_strategy.py # OpenCLI 策略测试
```

## 依赖安装

```bash
cd D:\skills\url-reader
python -m venv .venv
.venv\Scripts\activate

# 核心依赖
pip install firecrawl-py requests

# Playwright（可选，用于需要登录的平台）
pip install playwright
playwright install chromium
```

## 常见问题

**Q: 微信公众号读取失败？**
A: 微信反爬最严格。运行 `python -m scripts.wechat_auth setup` 设置登录态，或切换到 Firecrawl。

**Q: Firecrawl 额度用完？**
A: 自动降级到 Jina Reader（免费），无需操作。

**Q: 图片下载失败？**
A: 部分平台有 Referer 验证。系统已内置平台感知的 Referer 映射，覆盖小红书、微信、飞书、微博、B站。
