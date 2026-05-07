# OpenCLI Fallback And Zhihu Answer-Only Cleanup Design

**Goal**

Add an `opencli browser extract` fallback to `url-reader`, and make Zhihu question pages return only the public answers instead of full page noise.

**Scope**

- Add a new fetch strategy that shells out to `opencli browser`.
- Use that strategy as a platform-specific fallback for `zhihu` and `reddit`.
- Add a Zhihu question-page cleaner that keeps only the title and extracted answers.
- Keep existing `Firecrawl -> Jina -> Playwright` behavior unchanged for other platforms.

**Non-Goals**

- Full `opencli zhihu question` adapter integration.
- Dedicated Reddit post/comment cleanup in this round.
- Logged-in/private page support.

## Current Problems

1. `Firecrawl` and `Jina` fail on some Zhihu question pages.
2. Existing `Playwright` extraction returns anti-bot error JSON on the same question page.
3. `opencli zhihu question` requires cookies, even when the public page itself is readable without login.
4. `opencli browser extract` can read the public page, but its raw output still contains large amounts of Zhihu page noise.

## Chosen Approach

### Strategy Layer

Introduce `OpenCLIBrowserStrategy`:

- Run `opencli browser open <url>`
- Parse returned page/tab ID
- Run `opencli browser extract --tab <id> --selector main`
- If that fails with selector issues, retry without `--selector`
- Close the temporary tab if possible
- Return the extracted Markdown body into the existing `postprocess_content()` pipeline

### Platform Routing

- `zhihu` preferred strategies become:
  - `firecrawl -> jina -> opencli_browser -> playwright`
- Add explicit `reddit` platform support:
  - `jina -> opencli_browser -> playwright`

### Zhihu Question Cleanup

Detect `zhihu.com/question/...` URLs and route them to a dedicated answer-only extractor.

Output shape:

```md
# 问题标题

## 回答

1. 作者
回答正文

2. 作者
回答正文
```

Cleanup rules:

- Keep only loaded answers, not all “remaining answers”.
- Remove question stats, hot search, app download, footer, topic chips, promoted cards, and sidebars.
- Remove answer-author signature lines where they look like profile bios rather than answer content.
- Remove image-only lines and SVG placeholder lines.

## Testing

- Add failing tests for:
  - `reddit.com` platform identification
  - `OpenCLIBrowserStrategy` JSON parsing / fallback behavior
  - Zhihu question answer-only extraction
- Verify on the real Zhihu question URL after implementation.
