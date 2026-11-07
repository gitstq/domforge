<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen.svg" alt="Zero deps">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
</p>

# 🕸️ domforge

> **零依賴 · 離線優先的網頁 DOM 結構快照與差異引擎**，專為 AI Agent 網頁自動化設計。
> 當 Agent 執行「點擊 / 提交 / 跳轉」等動作後，domforge 能離線回答：**「頁面到底變了什麼？」**

---

## 🎉 專案介紹

`domforge` 是一個**純標準函式庫**（零第三方依賴）實作的輕量級工具，用於把任意網頁（或本地 HTML / 原始 HTML 字串）解析為一份**可比對的 DOM 結構快照**，並在兩次快照之間計算**精確的差異化報告**。

- **核心價值**：在 Agent 瀏覽器自動化場景中，傳統方案依賴截圖或整頁 HTML 字串比對，體積大、雜訊高、難以判斷「動作是否生效」。domforge 以結構化骨架 + 穩定定位路徑，讓「頁面變化」變成可量化、可斷言的資料。
- **解決的痛點**：Agent 點擊按鈕後無法確認結果；多步操作難以回溯；整頁 diff 雜訊巨大；線上服務有隱私與網路依賴。
- **自研差異化亮點**：
  - 基於 `html.parser` 自研 DOM 骨架提取，無需瀏覽器、無需網路連線（解析本地即可）。
  - 引入**穩定定位路徑**（如 `html/body/main/nav/a[1]`），使跨快照匹配精確到節點。
  - 內建**變化分類器**（navigation / modal_opened / content_update / structure_change / interactive_change …），把「差異」直接翻譯成 Agent 可消費的結論。
- **靈感來源**：Agent 瀏覽器自動化趨勢（GitHub Trending 熱門方向）與帳號既有的「零依賴·離線優先」開發者工具矩陣。

---

## ✨ 核心特性

- 🧩 **零依賴**：僅用 Python 標準函式庫（`html.parser` / `urllib` / `argparse`），`pip install` 後即可離線執行。
- 📸 **結構快照（snap）**：把頁面提煉為「標籤樹 + 互動元素清單 + 聚合統計」三件套，輸出 JSON / 樹形 / 摘要三種格式。
- 🔍 **差異引擎（diff）**：逐節點比對，精確列出**新增 / 移除 / 文字變更 / 屬性變更**，以及連結、表單、輸入框、對話框的增刪計數。
- 🏷️ **穩定定位路徑**：每個元素擁有人類可讀且穩定的 `path`，讓兩次快照的同一節點可被精確對齊。
- 🤖 **變化分類器**：自動歸納出 `navigation` / `modal_opened` / `modal_closed` / `content_update` / `structure_change` / `interactive_change` / `link_change` / `attribute_change` / `no_change`。
- 🌐 **多源輸入**：支援 URL 抓取、本地 HTML 檔案、stdin 管道、原始 HTML 字串四種來源。
- 🧪 **自帶測試**：標準函式庫 `unittest` 全覆蓋核心邏輯，零額外測試依賴。

---

## 🚀 快速開始

### 環境要求
- Python **3.8+**（無任何第三方依賴）

### 安裝
```bash
pip install domforge
# 或從原始碼安裝
git clone https://github.com/gitstq/domforge.git && cd domforge && pip install .
```

### 本地啟動 / 一鍵執行
```bash
# 1) 抓取網頁並產生結構摘要
domforge snap https://example.com

# 2) 抓取為 JSON 快照（供後續 diff 使用）
domforge snap https://example.com --format json --out before.json

# 3) 執行動作後再次抓取，比對變化
domforge snap https://example.com/after --format json --out after.json
domforge diff before.json after.json

# 4) 直接比對兩段 HTML 字串（無需網路）
domforge watch "<html><body><p>舊</p></body></html>" "<html><body><p>新</p></body></html>"
```

---

## 📖 詳細使用指南

### `snap` —— 產生快照
```bash
domforge snap <SOURCE> [--format json|tree|summary] [--out FILE]
```
- `<SOURCE>` 自動識別：以 `http(s)://` 開頭抓取 URL；等於 `-` 從 stdin 讀取；本地檔案存在則讀取；其他視為 HTML 字串。
- `--format`：`json` / `tree` / `summary`（預設）。
- `--max-depth` / `--text-limit`：控制樹形渲染深度與文字截斷長度。

### `diff` / `watch` —— 比對變化
```bash
domforge diff <OLD> <NEW> [--format human|json]
domforge watch <OLD> <NEW>          # 等同於 diff --format human
```

### 程式介面
```python
from domforge import parse_html, diff_snapshots

before = parse_html(html_before, url="https://x", source="url")
after  = parse_html(html_after,  url="https://x", source="url")
report = diff_snapshots(before, after)
print(report.classification)   # 例如 "modal_opened"
```

---

## 💡 設計思路與迭代規劃

**設計理念**：以「最小可比對資訊」為原則——只保留對「頁面是否變化、變化在哪」有意義的結構。

**技術選型原因**：選用標準函式庫 `html.parser` 而非 `lxml` / `beautifulsoup`，是為了貫徹「零依賴·離線優先」基調。

**後續迭代計畫**：
- 支援 CSS 選擇器匯出與「依選擇器定位差異」
- 增加 `watch --serve` 模式，輪詢 URL 並推送結構化變更事件
- 提供 `--mask` 脫敏規則，避免快照洩露敏感文字

---

## 📦 打包與部署指南

- **類型**：命令列工具 + Python 函式庫。
- **打包**：零依賴純 Python 套件，無需編譯。
  ```bash
  pip install build && python -m build
  pip install twine && twine upload dist/*
  ```
- **相容環境**：Python 3.8+，Windows / macOS / Linux 全平台。

---

## 🤝 貢獻指南

1. Fork 本倉庫並建立特性分支：`git checkout -b feat/your-feature`
2. 保持**零依賴**原則，新增邏輯請配套 `tests/` 下的 `unittest` 用例
3. 提交資訊遵循 Angular 規範：`feat:` / `fix:` / `docs:` / `refactor:`
4. 提交 PR 並於描述中說明動機與自測結果

---

## 📄 開源協議

本專案基於 **MIT License** 開源，詳見 [LICENSE](LICENSE)。可自由用於商業與非商業場景。
