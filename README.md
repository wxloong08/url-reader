# URL Reader - 智能网页内容读取器

> Forked from [yhslgg-arch/url-reader](https://github.com/yhslgg-arch/url-reader)，在此基础上做了大量扩展。

读取任意 URL 内容，自动识别平台类型，智能选择最佳读取策略，自动保存内容和图片到本地。

## 功能特点

- **智能平台识别**：微信公众号、小红书、今日头条、抖音、淘宝、天猫、京东、百度、知乎、微博、X、B站、Reddit、MeowVPS、HostLoc、NodeSeek、LINUX DO、V2EX、LowEndTalk、LowEndSpirit
- **多策略读取**：Firecrawl → OpenCLI → Jina → Playwright，按平台自动选择优先级。未配置 API Key 或未安装依赖时自动跳过不可用策略
- **Markdown 输出**：干净的 Markdown 格式，含 YAML front matter
- **自动保存**：内容 + 图片下载到本地，图片 URL 自动替换为本地路径
- **平台感知**：图片下载自动匹配正确的 Referer

## 快速开始

```bash
# 安装依赖
pip install firecrawl-py requests

# 可选：Playwright（用于需要登录的平台）
pip install playwright && playwright install chromium

# 读取 URL
python -m scripts.main https://example.com

# 读取并保存
python -m scripts.main https://example.com --save
```

## 配置

优先在项目根目录创建 `.env` 文件（已 gitignored）：

```bash
FIRECRAWL_API_KEY=fc-YOUR_KEY
```

也支持通过环境变量或 `config.json` 配置：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `FIRECRAWL_API_KEY` | Firecrawl API 密钥 | (空) |
| `URL_READER_OUTPUT_DIR` | 保存目录 | `~/url-reader-output` |
| `URL_READER_TIMEOUT` | HTTP 超时秒数 | 30 |
| `URL_READER_HEADLESS` | Playwright 无头模式 | true |

## 架构

```
URL 输入 → 平台识别 → 策略链（按平台优先级）→ 格式化 → 保存
```

### 目录结构

```
url-reader/
├── skill.md                        # Claude 执行指南
├── README.md
├── metadata.json
└── scripts/
    ├── config.py                   # 配置（env > .env > config.json > defaults）
    ├── platforms.py                # 平台识别 + 策略优先级
    ├── content.py                  # 标题/图片提取
    ├── formatter.py                # Markdown 格式化
    ├── saver.py                    # 磁盘保存 + 图片下载
    ├── wechat_auth.py              # WeChat 认证管理
    ├── url_converter.py            # WeChat URL 转换
    ├── main.py                     # 入口 / 编排器
    └── strategies/
        ├── __init__.py             # FetchStrategy ABC
        ├── firecrawl.py
        ├── jina.py
        └── playwright_strategy.py
```

## License

MIT — 原始版本 © ys (yhslgg-arch)，修改和扩展 © wxloong08。详见 [LICENSE](LICENSE)。
