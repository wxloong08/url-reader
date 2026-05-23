# URL Reader

> Forked from [yhslgg-arch/url-reader](https://github.com/yhslgg-arch/url-reader)，在原项目基础上扩展了平台识别、论坛清洗、`OpenCLI` 回退和更适合 LLM 调研的保存格式。

`url-reader` 用来读取公开网页内容，并把结果整理成尽量干净的 Markdown。  
它不是“万能爬虫”，而是一个带平台识别、策略回退和内容清洗的读取流水线。

## 现在到底能做什么

- 识别常见内容站、论坛站、社交站点，以及一批财经披露源和新闻源
- 按平台优先级尝试多种读取策略
- 对部分平台做专门清洗，而不是只返回原始网页 dump
- 保存 Markdown 和图片到本地
- 对论坛和问答页尽量保留“正文 / 回复 / 回答”结构，方便后续给 LLM 做摘要、调研、对比

## 读取流程

实际流程是：

```text
URL
  -> 平台识别
  -> 按该平台自己的策略顺序依次尝试
  -> 内容后处理 / 清洗
  -> 格式化
  -> 可选保存
```

注意：

- 没有“全局固定策略顺序”。
- 每个平台的策略顺序都定义在 [scripts/platforms.py](scripts/platforms.py)。
- 某些策略在本机不可用时会失败回退；当前 `firecrawl` 和 `cloakbrowser` 会在进入主循环前被预过滤。
- 如果任一非 OpenCLI 策略返回登录页、验证页或“需要登录/验证”类错误，调度器会把 `OpenCLI Browser` 提到下一位再抓一次，并继续走同一套平台清洗逻辑。

## 当前策略

### 1. Firecrawl

- 适合 JS 较重、Jina 不稳定的站点
- 需要同时满足：
  - 已安装 `firecrawl-py`
  - 已设置 `FIRECRAWL_API_KEY`
- 如果缺包或缺 Key，会被直接跳过

### 2. Jina Reader

- 对公开网页最省事
- 不需要 API Key
- 对部分站点可能返回 `451`、摘要页或带较多噪音的正文

### 3. OpenCLI Browser

- 复用本机 `opencli browser extract`
- 适合“网页公开可见，但 Jina / Playwright 不稳定”的场景
- 也会作为登录页 / 验证页回退：当其他策略检测到需要登录或验证时，本轮尚未试过 OpenCLI 就会立即尝试它
- 当前对 `知乎 question` 页特别有用
- 需要本机安装 `opencli`

### 4. CloakBrowser（可选）

- 更强的无头浏览器 fallback，用于降低公开页面触发验证的概率
- 当前只建议给高风控公开页启用，例如 `知乎 / 脉脉 / 牛客`
- 需要你自己提供固定版本本地二进制
- 默认关闭，不会自动下载、不依赖自动更新

### 5. Playwright

- 本地浏览器渲染兜底
- 适合需要真实浏览器环境的站点
- 微信可配合登录态使用
- 需要安装 `playwright` 和 `chromium`

## 平台支持

下面分两层看，避免 README 把“显式识别”和“专门清洗”混成一回事。

### 显式识别的平台

- 微信公众号
- 小红书
- 今日头条
- 抖音
- 淘宝
- 天猫
- 京东
- 百度 / 百家号
- 知乎
- 脉脉
- 牛客
- 同花顺
- 微博
- X / Twitter
- B站
- Reddit
- 亿牛网
- 雪球
- MeowVPS
- HostLoc
- NodeSeek
- LINUX DO
- V2EX
- LowEndTalk
- LowEndSpirit

其余站点走 `generic` 兜底。

### 有专门清洗 / 提取逻辑的平台

#### 社交 / 问答

- `X / Twitter`
  - 去掉 `Article / Conversation / Replies / Related Posts` 包装
  - 保留标题、作者、发布时间、图片、正文

- `知乎 question`
  - 只保留问题标题和当前已加载的公开回答
  - 尽量移除关注数、浏览数、热榜、客户端下载、侧栏推荐、答主签名等噪音

#### 求职 / 面经

- `脉脉`
  - 支持 `article/detail` 公开文章页
  - 保留标题、作者、发布时间/身份、正文
  - 去掉登录提示、加好友控件、声明、推荐和评论区

- `牛客 discuss`
  - 支持公开讨论帖 / 面经帖
  - 保留标题和主帖正文，并把帖内小节整理成二级标题
  - 去掉精华标记、标签、分享控件、热门话题和评论区

#### 财经 / 新闻

- `巨潮资讯`
  - 支持公告 PDF 和最新公告列表
  - 保留证券代码、证券简称、公告编号、时间、正文

- `上交所`
  - 支持公告 PDF 和科创板公告列表
  - 保留代码、简称、公告编号、时间、正文

- `HKEXnews`
  - 支持标题搜索结果页和港股披露 PDF
  - 保留发布时间、代码、简称、文档类别、公告标题、正文

- `SEC EDGAR`
  - 支持公司 filings 列表页和 filing index 页
  - 保留 form、description、filing date、period of report、document list

- `Reuters`
  - 支持 `Markets` 列表页和文章页
  - 去掉数据部件、cookie/legal 壳、相关阅读和广告占位

- `财联社`
  - 支持首页资讯流和 `detail` 文章页
  - 保留标题、时间、来源、摘要、正文

- `东方财富`
  - 支持财经首页资讯流、`/a/<id>.html` 文章页、`data.eastmoney.com` 个股数据页
  - 个股页会优先保留核心题材、主营业务、融资融券和财务数据表

- `新浪财经`
  - 支持首页资讯流、`doc-*.shtml` 新闻页、`vip.stock.finance.sina.com.cn` 个股资料页
  - 个股页会优先保留公司资料、主营业务、上市信息等结构化信息

- `华尔街见闻`
  - 支持首页资讯流和 `/articles/<id>` 文章页
  - 去掉行情壳、登录/收藏/评论区和风险提示尾部

- `同花顺 / 亿牛网 / 雪球`
  - 面向个股财务 / 估值 / 资料页
  - 优先保留财务指标、关键估值数字、公司资料和结构化表格

#### 论坛 / 社区

- `NodeSeek`
  - 主楼 / 回复分离
  - 页脚、登录提示、导航噪音清理
  - 低信息回复过滤

- `HostLoc`
  - Discuz 结构清理
  - 主楼 / 回复分离
  - 页尾和楼层噪音清理

- `LINUX DO`
  - 主题页主楼 / 回复分离
  - Related topics 和论坛导航噪音清理

- `V2EX`
  - 主题页主楼 / 回复分离
  - 推广块、推荐块、页脚噪音清理

- `LowEndTalk / LowEndSpirit`
  - Vanilla 风格论坛提取
  - 支持额外分页回复补抓

### 只做规则清洗的平台

这些站点当前主要是“按规则删噪”，不是深度结构化提取：

- 微信公众号
- 小红书
- 今日头条
- 抖音
- 淘宝 / 天猫 / 京东
- 百度 / 知乎专栏类页面
- 微博
- B站
- MeowVPS
- Reddit

其中 `Reddit` 目前是“显式识别 + 策略回退 + 通用清洗”，还没有专门的评论提取器。

## 依赖安装

最小依赖：

```bash
pip install requests
```

如果你要用 `.env`：

```bash
pip install python-dotenv
```

如果你要用 Firecrawl：

```bash
pip install firecrawl-py
```

如果你要用 Playwright：

```bash
pip install playwright
playwright install chromium
```

如果你要用 OpenCLI Browser：

```bash
npm install -g @jackwener/opencli
```

如果你要用 CloakBrowser：

```bash
pip install cloakbrowser
```

然后显式启用并指定本地固定二进制：

```bash
URL_READER_CLOAKBROWSER_ENABLED=true
CLOAKBROWSER_BINARY_PATH=D:/tools/cloakbrowser/chrome.exe
CLOAKBROWSER_AUTO_UPDATE=false
CLOAKBROWSER_SKIP_CHECKSUM=false
```

## 配置

配置优先级：

```text
环境变量 > .env > config.json > 默认值
```

### `.env`

只有安装了 `python-dotenv` 才会自动加载项目根目录的 `.env`。

示例：

```bash
FIRECRAWL_API_KEY=fc-YOUR_KEY
URL_READER_OUTPUT_DIR=D:/url-reader-output
URL_READER_TIMEOUT=30
URL_READER_HEADLESS=true
URL_READER_FORUM_MAX_PAGES=8
URL_READER_CLOAKBROWSER_ENABLED=false
CLOAKBROWSER_BINARY_PATH=
CLOAKBROWSER_BACKEND=playwright
```

### 支持的环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `FIRECRAWL_API_KEY` | Firecrawl API Key | 空 |
| `URL_READER_JINA_BASE_URL` | Jina Reader 基础地址 | `https://r.jina.ai/` |
| `URL_READER_OUTPUT_DIR` | 输出目录 | `~/url-reader-output` |
| `URL_READER_TIMEOUT` | 超时秒数 | `30` |
| `URL_READER_HEADLESS` | Playwright 是否无头 | `true` |
| `URL_READER_FORUM_MAX_PAGES` | 论坛分页补抓上限 | `8` |
| `URL_READER_CLOAKBROWSER_ENABLED` | 是否启用 CloakBrowser | `false` |
| `CLOAKBROWSER_BINARY_PATH` | CloakBrowser 本地固定二进制路径 | 空 |
| `CLOAKBROWSER_BACKEND` | CloakBrowser backend | `playwright` |

### `config.json`

也可以在项目根目录放一个 `config.json`：

```json
{
  "firecrawl_api_key": "fc-YOUR_KEY",
  "output_dir": "D:/url-reader-output",
  "timeout": 30,
  "headless": true,
  "forum_max_pages": 8
}
```

## 用法

读取并打印：

```bash
python -m scripts.main "https://example.com"
```

读取并保存：

```bash
python -m scripts.main "https://example.com" --save
```

指定输出目录保存：

```bash
URL_READER_OUTPUT_DIR="D:/custom/output" python -m scripts.main "https://example.com" --save
```

微信登录态管理：

```bash
python -m scripts.wechat_auth setup
python -m scripts.wechat_auth status
```

微信公众号长链接转短链接：

```bash
python -m scripts.url_converter "https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&sn=xxx"
```

## 输出格式

默认保存目录结构：

```text
output-dir/
└── 2026-01-30_文章标题/
    ├── content.md
    ├── img_01.jpg
    ├── img_02.webp
    └── ...
```

保存的 `content.md` 带 YAML front matter：

```md
---
title: ...
platform: ...
url: ...
saved_at: ...
images: 2
---
```

然后根据内容类型采用不同结构：

- 社交帖：`Metadata / Images / Content`
- 论坛帖：`Metadata / Thread / Replies`
- 普通文章：保留清洗后的正文

## 项目结构

```text
url-reader/
├── README.md
├── SKILL.md
├── metadata.json
├── config.json                  # 可选，用户自建
├── data/
│   └── wechat_auth.json         # 微信登录态
├── docs/
├── tests/
└── scripts/
    ├── __init__.py
    ├── config.py
    ├── content.py
    ├── formatter.py
    ├── main.py
    ├── platforms.py
    ├── saver.py
    ├── url_converter.py
    ├── wechat_auth.py
    └── strategies/
        ├── __init__.py
        ├── cloakbrowser_strategy.py
        ├── firecrawl.py
        ├── jina.py
        ├── opencli_browser.py
        └── playwright_strategy.py
```

## 已知限制

- 公开网页可访问，不代表所有策略都能读到；不同策略的能力边界不同
- `知乎 question` 只保留“当前已加载的公开回答”，不会自动拿到全部回答
- `Reddit` 当前还没有专门的评论结构化提取器
- `雪球` 当前公开入口反爬较重，尚未纳入稳定支持范围
- `Playwright` 和 `OpenCLI Browser` 都依赖本机浏览器环境，CI 或纯服务器环境下未必稳定
- 强反爬站点不保证稳定成功
- OpenCLI 回退只在检测到登录/验证类失败时插入；如果站点完全不向本机浏览器开放内容，仍会失败

## 测试

```bash
python -m unittest tests.test_main tests.test_opencli_strategy tests.test_cloakbrowser_strategy tests.test_content tests.test_formatter tests.test_playwright_strategy
```

## License

MIT。原始版本 © ys (`yhslgg-arch`)，后续修改与扩展 © 本仓库维护者。详见 [LICENSE](LICENSE)。
