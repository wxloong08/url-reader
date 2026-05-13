---
name: url-reader
description: 智能读取任意URL内容，支持内容站、论坛站、求职社区与财经个股数据页，自动保存Markdown和图片。
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
│ Firecrawl → CloakBrowser → OpenCLI → Jina │
│                  ↓                        │
│              Playwright 兜底              │
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

### 策略 4：CloakBrowser（可选增强）

- 更强的无头浏览器 fallback
- 目标是降低公开页面触发验证的概率
- 默认关闭，只有显式启用并提供固定本地二进制时才参与策略链
- 当前建议只给 `知乎 / 脉脉 / 牛客` 这类高风控公开页启用

### 策略 5：Playwright 浏览器自动化

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
| 知乎 | zhihu.com | Firecrawl → CloakBrowser → OpenCLI → Jina → Playwright |
| 脉脉 | maimai.cn | Firecrawl → CloakBrowser → OpenCLI → Jina → Playwright |
| 牛客 | nowcoder.com | Firecrawl → CloakBrowser → OpenCLI → Jina → Playwright |
| 同花顺 | 10jqka.com.cn | Playwright → OpenCLI → Jina |
| 微博 | weibo.com | Firecrawl → OpenCLI → Playwright → Jina |
| X | x.com / twitter.com | Jina → OpenCLI → Playwright → Firecrawl |
| B站 | bilibili.com | Firecrawl → OpenCLI → Jina → Playwright |
| Reddit | reddit.com | Jina → OpenCLI → Playwright |
| 巨潮资讯 | cninfo.com.cn | Jina → OpenCLI → Playwright |
| 上交所 | sse.com.cn / star.sse.com.cn | Jina → OpenCLI → Playwright |
| HKEXnews | hkexnews.hk | Jina → OpenCLI → Playwright |
| SEC EDGAR | sec.gov | Jina → OpenCLI → Playwright |
| Reuters | reuters.com | OpenCLI → Jina → Playwright → Firecrawl |
| 财联社 | cls.cn | Jina → OpenCLI → Playwright |
| 东方财富 | eastmoney.com / data.eastmoney.com | Playwright → Jina → OpenCLI |
| 新浪财经 | finance.sina.com.cn / vip.stock.finance.sina.com.cn | Jina → OpenCLI → Playwright |
| 华尔街见闻 | wallstreetcn.com | Jina → OpenCLI → Playwright |
| 亿牛网 | eniu.com | Playwright → OpenCLI → Jina |
| 雪球 | xueqiu.com | Playwright → Jina → OpenCLI |
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

## 求职 / 面经支持

针对求职调研场景，系统已支持专门清洗：

- `脉脉 article/detail`：保留标题、作者、发布时间/身份、正文
- `牛客 discuss`：保留标题和主帖正文，帖内小节整理为二级标题

这类清洗会尽量去掉登录提示、加好友控件、标签、分享控件、热门话题、评论区和 APP 打开引导，只留下适合 LLM 调研的主体内容。

## 财经 / 新闻支持

针对财经披露源和新闻源，系统已支持专门清洗：

- `巨潮资讯`：公告 PDF、最新公告列表
- `上交所`：公告 PDF、科创板公告列表
- `HKEXnews`：标题搜索结果页、披露 PDF
- `SEC EDGAR`：公司 filings 列表页、filing index 页
- `Reuters`：Markets 列表页、文章页
- `财联社`：首页资讯流、detail 文章页
- `东方财富`：财经首页资讯流、文章页、个股数据页
- `新浪财经`：首页资讯流、文章页、个股资料页
- `华尔街见闻`：首页资讯流、文章页
- `同花顺`：F10 财务页、财务指标/资产负债构成/报告区块
- `亿牛网`：个股估值页、关键估值/财务快讯
- `雪球`：已显式识别，优先走浏览器策略

这些清洗会尽量保留投资调研所需的元信息，如标题、时间、来源、证券代码、公告编号、文档类型和正文，并去掉导航、行情挂件、评论区、推荐阅读、下载/登录引导等噪音。

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
| `URL_READER_CLOAKBROWSER_ENABLED` | 是否启用 CloakBrowser | false |
| `URL_READER_FORUM_MAX_PAGES` | 论坛帖子最多抓取页数 | 8 |
| `CLOAKBROWSER_BINARY_PATH` | CloakBrowser 本地固定二进制路径 | (空) |
| `CLOAKBROWSER_BACKEND` | CloakBrowser backend | playwright |

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
│       ├── cloakbrowser_strategy.py # CloakBrowser 策略
│       ├── firecrawl.py        # Firecrawl 策略
│       ├── jina.py             # Jina Reader 策略
│       ├── opencli_browser.py  # OpenCLI Browser 策略
│       └── playwright_strategy.py  # Playwright 策略
└── tests/
    ├── __init__.py
    ├── test_content.py         # 平台识别 + 清洗测试
    ├── test_formatter.py       # 格式化输出测试
    ├── test_opencli_strategy.py # OpenCLI 策略测试
    ├── test_cloakbrowser_strategy.py # CloakBrowser 策略测试
    ├── test_playwright_strategy.py # Playwright 财经页测试
    └── test_main.py            # 主流程准备/策略过滤测试
```

## 依赖安装

```bash
cd D:\skills\url-reader
python -m venv .venv
.venv\Scripts\activate

# 核心依赖
pip install requests python-dotenv

# Firecrawl（可选）
pip install firecrawl-py

# Playwright（可选，用于需要登录的平台）
pip install playwright
playwright install chromium

# CloakBrowser（可选，用于高风控公开页）
pip install cloakbrowser
```

## 测试

```bash
python -m unittest tests.test_main tests.test_opencli_strategy tests.test_cloakbrowser_strategy tests.test_content tests.test_formatter tests.test_playwright_strategy
```

## 常见问题

**Q: 微信公众号读取失败？**
A: 微信反爬最严格。运行 `python -m scripts.wechat_auth setup` 设置登录态，或切换到 Firecrawl。

**Q: Firecrawl 额度用完？**
A: 自动降级到 Jina Reader（免费），无需操作。

**Q: 图片下载失败？**
A: 部分平台有 Referer 验证。系统已内置平台感知的 Referer 映射，覆盖小红书、微信、飞书、微博、B站。
