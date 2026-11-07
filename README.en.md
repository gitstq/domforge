<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen.svg" alt="Zero deps">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
</p>

# 🕸️ domforge

> A **zero-dependency, offline-first DOM structure snapshot & diff engine**, purpose-built for AI Agent web automation.
> After an agent performs a *click / submit / navigate* action, domforge answers offline: **"What exactly changed on the page?"**

---

## 🎉 Introduction

`domforge` is a lightweight tool implemented with the **pure Python standard library** (zero third-party dependencies). It parses any web page (or a local HTML file / raw HTML string) into a **comparable DOM-structure snapshot**, and computes a **precise differential report** between two snapshots.

- **Core value**: In agent browser-automation scenarios, traditional approaches rely on screenshots or whole-page HTML diffing—bulky, noisy, and poor at telling "did the action work?". domforge turns "page change" into quantifiable, assertable data via a structural skeleton + stable locator paths.
- **Problems solved**: Agents can't confirm the result after a click; multi-step flows are hard to trace; whole-page diffs are noisy; online services add privacy and network dependencies.
- **Original differentiators**:
  - A self-built DOM skeleton extractor on `html.parser`—no browser, no network (parses locally).
  - **Stable locator paths** (e.g. `html/body/main/nav/a[1]`) so the same node is aligned precisely across snapshots.
  - A built-in **change classifier** (`navigation` / `modal_opened` / `content_update` / `structure_change` / `interactive_change` …) translating diffs into agent-consumable conclusions.
- **Inspiration**: The agent-browser-automation trend (a top GitHub Trending theme) and the account's existing "zero-dependency, offline-first" developer-tool lineup.

---

## ✨ Core Features

- 🧩 **Zero dependencies**: Only the Python stdlib (`html.parser` / `urllib` / `argparse`). Runs offline after `pip install`.
- 📸 **Structural snapshot (`snap`)**: Distills a page into a tag tree + interactive-element list + aggregate stats, in JSON / tree / summary formats.
- 🔍 **Diff engine (`diff`)**: Node-by-node comparison listing **added / removed / text-changed / attr-changed**, plus link/form/input/dialog add-remove counts.
- 🏷️ **Stable locator paths**: Every element gets a human-readable, stable `path` so identical nodes align across snapshots.
- 🤖 **Change classifier**: Auto-labels `navigation` / `modal_opened` / `modal_closed` / `content_update` / `structure_change` / `interactive_change` / `link_change` / `attribute_change` / `no_change`.
- 🌐 **Multi-source input**: URL fetch, local HTML file, stdin pipe, or raw HTML string.
- 🧪 **Self-tested**: Full `unittest` coverage of core logic, no extra test deps.

---

## 🚀 Quick Start

### Requirements
- Python **3.8+** (no third-party dependencies)

### Install
```bash
pip install domforge
# or from source
git clone https://github.com/gitstq/domforge.git && cd domforge && pip install .
```

### Run
```bash
# 1) Fetch a page and print a structural summary
domforge snap https://example.com

# 2) Capture a JSON snapshot for later diffing
domforge snap https://example.com --format json --out before.json

# 3) Capture again after an action, then diff
domforge snap https://example.com/after --format json --out after.json
domforge diff before.json after.json

# 4) Diff two HTML strings directly (no network)
domforge watch "<html><body><p>old</p></body></html>" "<html><body><p>new</p></body></html>"
```

---

## 📖 Usage Guide

### `snap` — capture a snapshot
```bash
domforge snap <SOURCE> [--format json|tree|summary] [--out FILE]
```
- `<SOURCE>` auto-detected: `http(s)://` → fetch URL; `-` → stdin; existing file → read; else treated as HTML.
- `--format`: `json` / `tree` / `summary` (default).
- `--max-depth` / `--text-limit`: tree depth and text truncation.

### `diff` / `watch` — compare changes
```bash
domforge diff <OLD> <NEW> [--format human|json]
domforge watch <OLD> <NEW>          # alias for diff --format human
```

### Library API
```python
from domforge import parse_html, diff_snapshots

before = parse_html(html_before, url="https://x", source="url")
after  = parse_html(html_after,  url="https://x", source="url")
report = diff_snapshots(before, after)
print(report.classification)   # e.g. "modal_opened"
```

---

## 💡 Design & Roadmap

**Design philosophy**: Minimal comparable information—keep only what matters for "did it change, and where".

**Tech choice**: Standard-library `html.parser` over `lxml`/`beautifulsoup` to stay zero-dependency and offline-first, single-file portable, no supply-chain risk.

**Roadmap**:
- CSS-selector export & "diff by selector"
- `watch --serve` polling mode emitting structured change events (for long agent sessions)
- `--mask` redaction rules to avoid leaking sensitive text into snapshots

---

## 📦 Packaging & Deployment

- **Type**: CLI tool + Python library.
- **Build**: pure-Python, no compilation.
  ```bash
  pip install build && python -m build
  pip install twine && twine upload dist/*
  ```
- **Compatibility**: Python 3.8+, Windows / macOS / Linux.

---

## 🤝 Contributing

1. Fork and create a feature branch: `git checkout -b feat/your-feature`
2. Keep the **zero-dependency** rule; add `unittest` cases under `tests/`
3. Use Angular commit conventions: `feat:` / `fix:` / `docs:` / `refactor:`
4. Open a PR describing motivation and self-test results

---

## 📄 License

Released under the **MIT License**—see [LICENSE](LICENSE). Free for commercial and non-commercial use.
