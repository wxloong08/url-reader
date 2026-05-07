---
layout: post
title: "AI 编程助手的搜索+抓取链路优化：用 SearXNG + url-reader 替代 web_url_read"
date: 2026-05-07
categories: [engineering, ai-toolchain]
---

## 问题的提出

在 Claude Code 中做技术调研时，典型流程是：搜索 → 点开结果 → 阅读内容。Anthropic 的 MCP 生态里，`mcp__searxng__web_url_read` 是默认的"点开阅读"工具。但它有致命缺陷。

### web_url_read 的三个痛点

**1. 中文站成功率低。** 底层只走 Jina Reader——微信公众号、知乎、小红书等中国主流平台普遍返回 HTTP 451 (Unavailable For Legal Reasons)。

**2. 无降级机制。** Jina 挂了就挂了，不会自动换其他方式重试。

**3. 无内容清洗。** 即使抓取成功，返回的是原始页面全文（导航栏、侧栏、广告、页脚、相关推荐），token 利用率极低。

### 真实对比：抓取同一个 Reddit 帖子

{% raw %}
`web_url_read` 返回：
```
<!DOCTYPE html>
```
——空白。Reddit 把 Jina 屏蔽了。

`url-reader` 返回：
```
标题 + 正文 + 20+ 条评论（经过清洗）
```
——策略链自动从 Jina 降级到 OpenCLI Browser，抓取成功。
{% endraw %}

## 解决方案：SearXNG → url-reader

架构很简单：

```
用户问题
    ↓
SearXNG MCP (多引擎搜索)
    ↓
搜索结果显示 → 用户选择感兴趣的链接
    ↓
url-reader (多策略降级 + 平台感知清洗)
    ↓
干净的 Markdown 进入 Claude 上下文
```

### 策略降级链

url-reader 为每个平台配置了专属的抓取策略链，从左到右逐级降级：

```
Firecrawl API → OpenCLI Browser → Jina Reader → Playwright
```

- **Firecrawl**：AI 驱动，Markdown 直出，但需要 API Key（未配置自动跳过）
- **OpenCLI Browser**：复用终端浏览器渲染，中文站兼容性最好——对 Jina 返回 451 的平台特别有效
- **Jina Reader**：免费 HTTP API，对海外站效果好
- **Playwright**：完整浏览器自动化，兜底

### 为什么 OpenCLI 是关键

Jina 对中国站的 451 率极高。在 20 个平台的实测中，OpenCLI 是**中文内容最可靠的策略**。它在知乎、Reddit、微博等 Jina 频繁失败的平台上提供了关键的保底能力。

## 平台感知的内容清洗

抓起内容只是第一步。Claude Code 的 token 是按量计费的，原始网页里 40-70% 是噪音。

url-reader 内置了针对 20+ 平台的内容清洗规则：

| 平台 | 清洗策略 | 主要去噪项 |
|------|----------|-----------|
| NodeSeek | forum_thread | "BD"、"支持"、"谢谢老板"、emoji-only 回复 |
| 知乎 | qa_answers | 关注统计、客户端下载提示、侧栏推荐 |
| 微信公众号 | wechat_article | "继续滑动看下一个"、"喜欢此内容的人还喜欢" |
| 京东/淘宝 | ecommerce | 售后保障、购物指南、版权声明 |
| V2EX/HostLoc | forum_thread | 导航、积分规则、Discuz 页脚 |

核心去噪逻辑：

```python
# 低价值回复检测 — 基于信息论信号
def _should_keep_reply(text):
    # 扔掉纯表情、纯数字
    # 扔掉 "BD" / "支持" / "前排"
    # 扔掉 "ID + 谢谢老板" 模式
    # 保留有问号、URL、技术关键词的回复
```

## 效果

### Token 节省

在 Claude Code 的工作流中，每次搜索后跟进阅读 3-5 个页面是常态。假设每次阅读消耗 5K-10K token：

| 方式 | 单页 token | 5 页 token | 成功率 |
|------|-----------|-----------|--------|
| web_url_read (裸 Jina) | ~8K（含噪音） | ~40K | 中文站 ~40% |
| url-reader | ~3K（清洗后） | ~15K | ~90%+ |

每次调研节省约 25K token，按 Sonnet 4.6 API 价格（$3/MTok input），约 $0.075/次。日积月累下来可观。

### 可用性

最关键的不是 token 省钱——是**不用反复尝试不同抓取方式**。以前 Jina 挂了要手动换个工具重试，现在自动降级，一次搞定。

## 部署

在 Claude Code 中配置：

```bash
# CLAUDE.md
## Web Search & Scraping
- 网页搜索优先使用 SearXNG MCP 工具
- 搜索后跟进阅读必须使用 url-reader，禁止使用 web_url_read
- url-reader 路径：D:\skills\url-reader
```

CLI 使用：

```bash
# 读取 URL
python -m scripts.main <url>

# 读取并保存到本地
python -m scripts.main <url> --save
```

## 总结

这套工具链用三个开源组件（SearXNG + url-reader + OpenCLI）构建了一个可靠、节省 token 的网页阅读管道。核心思路是：

1. **搜索和阅读解耦**——SearXNG 负责搜索，url-reader 负责阅读
2. **策略降级而非单一依赖**——不信任任何单一抓取方式
3. **平台感知清洗**——不是一刀切的去噪，而是针对每个平台的结构做优化

代码开源在 [github.com/wxloong08/url-reader](https://github.com/wxloong08/url-reader)。
