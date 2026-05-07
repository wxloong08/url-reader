# LLM-Friendly Archive Format Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make saved `content.md` files cleaner and more useful as LLM research input by improving structure and filtering obvious low-information replies.

**Architecture:** Keep platform-specific extraction in `scripts/content.py`, and move save-time formatting toward a stable archive shape in `scripts/formatter.py`. Preserve YAML metadata in `scripts/saver.py`, while tests lock the new structure and filtering rules.

**Tech Stack:** Python, unittest, existing URL reader pipeline

---

### Task 1: Add failing tests for saved Markdown layout

**Files:**
- Modify: `tests/test_content.py`
- Create: `tests/test_formatter.py`
- Test: `tests/test_formatter.py`

- [ ] **Step 1: Write the failing test**

Add tests asserting:
- saved Markdown no longer contains `**来源**`, `**读取策略**`, `**原文链接**`
- X saved output uses `## Metadata`, `## Images`, `## Content`
- forum saved output uses `## Thread` and `## Replies`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_content tests.test_formatter`
Expected: FAIL on missing new section structure

- [ ] **Step 3: Write minimal implementation**

Update formatter/content shaping to emit the new archive-oriented sections.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_content tests.test_formatter`
Expected: PASS

### Task 2: Add failing tests for low-information reply filtering

**Files:**
- Modify: `tests/test_content.py`
- Test: `tests/test_content.py`

- [ ] **Step 1: Write the failing test**

Add forum reply tests asserting that obvious low-information replies like `BD`, `支持`, `前排`, pure emoji, or extremely short praise are removed, while factual short replies remain.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_content -v`
Expected: FAIL because current code keeps those replies

- [ ] **Step 3: Write minimal implementation**

Add a conservative reply filter in `scripts/content.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_content -v`
Expected: PASS

### Task 3: Re-save and verify real outputs

**Files:**
- Modify: `scripts/content.py`
- Modify: `scripts/formatter.py`
- Modify: `scripts/saver.py` if needed

- [ ] **Step 1: Run the full regression suite**

Run: `python -m unittest tests.test_content tests.test_formatter`
Expected: PASS

- [ ] **Step 2: Re-generate sample outputs**

Run:
`$env:URL_READER_OUTPUT_DIR='D:\skills\url-reader\output'; python -m scripts.main "https://x.com/plantegg/status/2044321931944497364" --save`

Run:
`$env:URL_READER_OUTPUT_DIR='D:\skills\url-reader\output'; python -m scripts.main "https://www.nodeseek.com/post-683468-1" --save`

Expected: saved `content.md` files show cleaner LLM-friendly sections and filtered replies

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-04-16-llm-friendly-archive-format-design.md docs/superpowers/plans/2026-04-16-llm-friendly-archive-format.md tests/test_content.py tests/test_formatter.py scripts/content.py scripts/formatter.py scripts/saver.py
git commit -m "feat: improve llm archive formatting"
```
