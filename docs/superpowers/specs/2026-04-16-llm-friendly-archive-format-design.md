# LLM-Friendly Archive Format Design

**Goal**

Improve saved `content.md` files so they are easier for LLMs to ingest for research and synthesis: low noise, stable structure, and minimal information loss.

**Scope**

- Reformat saved Markdown for social posts and forum threads.
- Filter obvious low-information forum replies.
- Preserve source metadata in YAML front matter.
- Preserve semantically useful content such as authors, timestamps, quotes, links, code, and images.

**Non-Goals**

- Visual styling for human reading beyond cleaner Markdown structure.
- Semantic ranking or summarization of replies.
- Cross-platform AI scoring or deduplication.

## Current Problems

1. Saved files repeat display-oriented metadata (`来源`, `读取策略`, `原文链接`) that is useful for humans but noisy for LLM ingestion.
2. Forum replies are structurally inconsistent and often flatten mentions, quotes, and reply metadata into hard-to-parse blobs.
3. Low-information replies such as `BD`, `支持`, `前排`, or pure emoji reactions pollute the corpus.
4. Paragraphs are preserved too literally from scraped line breaks, producing dump-like rather than archive-like Markdown.

## Desired Output Shape

All saved files should keep YAML front matter:

```md
---
title: ...
platform: ...
url: ...
saved_at: ...
images: ...
---
```

After front matter, body layout should be LLM-oriented:

- No repeated display header like `**来源**` / `**读取策略**`.
- One top-level title only.
- Stable section names by content type.

### X / Social Post Layout

```md
# Title

## Metadata
- Author: ...
- Published: ...

## Images
![...](img_01.jpg)

## Content
Paragraph...
```

Rules:

- Keep images if present.
- Normalize body into paragraphs.
- Remove wrapper markers like `Article`, `Conversation`.

### Forum Thread Layout

```md
# Title

## Thread
Paragraph...

## Replies
### Reply 1 | author | time | #floor
> quoted text

reply body
```

Rules:

- Rename `主楼` to a neutral research-friendly section like `Thread`.
- Keep all structurally useful replies after filtering.
- Use predictable per-reply subheadings.
- Split quotes into Markdown blockquotes when recoverable.

## Low-Information Reply Filtering

Use a conservative filter. Remove only obviously low-value replies:

- very short praise/noise like `BD`, `支持`, `前排`, `路过`, `好鸡`
- pure emoji or sticker-equivalent replies
- extremely short cheerleading without facts, questions, or context

Keep replies that contain any of the following:

- numbers, dates, timings, measurements, versions, configs
- concrete problem statements or questions
- first-hand experience / test outcomes
- references to screenshots, logs, links, platforms, products, commands
- multi-sentence reasoning

## File Responsibilities

- `scripts/content.py`
  - normalize cleaned content into LLM-friendly structures
  - forum reply filtering and formatting
  - social post formatting improvements
- `scripts/formatter.py`
  - reduce save-time presentation noise
  - emit stable archive-friendly Markdown envelope
- `scripts/saver.py`
  - keep YAML front matter only, save already-clean formatted body
- `tests/test_content.py`
  - filtering and structure regression tests
- `tests/test_formatter.py`
  - saved Markdown layout regression tests

## Error Handling

- If reply filtering removes every reply, omit the `Replies` section entirely.
- If a post has no images, omit `Images`.
- If metadata such as author or published time is missing, omit only that field, not the whole section.

## Testing

- Add regression tests for X saved layout.
- Add regression tests for NodeSeek reply filtering.
- Add regression tests that noisy human-display headers are absent from saved Markdown.
