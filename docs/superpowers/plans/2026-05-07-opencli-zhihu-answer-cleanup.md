# OpenCLI Fallback And Zhihu Answer-Only Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `opencli browser extract` fallback and make Zhihu question pages return clean answer-only Markdown.

**Architecture:** Add a standalone `opencli` fetch strategy under `scripts/strategies/`, wire it into the orchestrator and platform definitions, then add a dedicated Zhihu question postprocessor in `scripts/content.py`.

**Tech Stack:** Python, unittest, subprocess, existing URL reader pipeline, local `opencli`

---

### Task 1: Lock the desired behavior with tests

**Files:**
- Modify: `tests/test_content.py`
- Create: `tests/test_opencli_strategy.py`
- Test: `tests/test_content.py`
- Test: `tests/test_opencli_strategy.py`

- [ ] Add a Reddit platform-identification regression test.
- [ ] Add a Zhihu question raw-fixture test that asserts only answers remain.
- [ ] Add `OpenCLIBrowserStrategy` tests using mocked subprocess output.
- [ ] Run: `python -m unittest tests.test_content tests.test_opencli_strategy -v`
- [ ] Confirm tests fail before implementation.

### Task 2: Implement the new strategy and routing

**Files:**
- Create: `scripts/strategies/opencli_browser.py`
- Modify: `scripts/main.py`
- Modify: `scripts/platforms.py`

- [ ] Implement `opencli` browser open/extract/close flow.
- [ ] Add `opencli_browser` to the strategy registry.
- [ ] Add explicit `reddit` platform support.
- [ ] Update `zhihu` preferred strategy order.

### Task 3: Implement Zhihu answer-only cleanup

**Files:**
- Modify: `scripts/content.py`
- Test: `tests/test_content.py`

- [ ] Detect `zhihu.com/question/` pages.
- [ ] Extract title and loaded answers only.
- [ ] Strip stats, hot lists, client prompts, and image-only noise.
- [ ] Re-run tests until green.

### Task 4: Verify on the real URL

**Files:**
- Modify: none

- [ ] Run: `python -m unittest tests.test_content tests.test_formatter tests.test_opencli_strategy`
- [ ] Run: `python -m scripts.main "https://www.zhihu.com/question/10434775822"`
- [ ] Confirm output is answer-only and no anti-bot JSON leaks through.
