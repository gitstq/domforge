<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen.svg" alt="Zero deps">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/offline--first-✔-orange.svg" alt="Offline first">
</p>

# 🕸️ domforge

> **零依赖 · 离线优先的网页 DOM 结构快照与差异引擎**，专为 AI Agent 网页自动化设计。
> 当 Agent 执行「点击 / 提交 / 跳转」等动作后，domforge 能离线回答：**「页面到底变了什么？」**

---

## 🎉 项目介绍

`domforge` 是一个**纯标准库**（零第三方依赖）实现的轻量级工具，用于把任意网页（或本地 HTML / 原始 HTML 字符串）解析为一份**可比较的 DOM 结构快照**，并在两次快照之间计算**精确的差异化报告**。

- **核心价值**：在 Agent 浏览器自动化（如 `vercel-labs/agent-browser` 类场景）中，传统方案依赖截图或整页 HTML 字符串比对，体积大、噪声高、难以判断「动作是否生效」。domforge 用结构化骨架 + 稳定定位路径，让「页面变化」变成可量化、可断言的数据。
- **解决的痛点**：Agent 点击按钮后无法确认结果；多步操作难以回溯；整页 diff 噪声巨大；在线服务有隐私与网络依赖。
- **自研差异化亮点**：
  - 基于 `html.parser` 自研 DOM 骨架提取，无需浏览器、无需网络连接（解析本地即可）。
  - 引入**稳定定位路径**（如 `html/body/main/nav/a[1]`），使跨快照匹配精确到节点。
  - 内置**变化分类器**（navigation / modal_opened / content_update / structure_change / interactive_change …），把「差异」直接翻译成 Agent 可消费的结论。
- **灵感来源**：Agent 浏览器自动化趋势（GitHub Trending 热门方向）与账号既有的「零依赖·离线优先」开发者工具矩阵。

---

## ✨ 核心特性

- 🧩 **零依赖**：仅用 Python 标准库（`html.parser` / `urllib` / `argparse`），`pip install` 后即可离线运行。
- 📸 **结构快照（snap）**：把页面提炼为「标签树 + 交互元素清单 + 聚合统计」三件套，输出 JSON / 树形 / 摘要三种格式。
- 🔍 **差异引擎（diff）**：逐节点比对，精确列出**新增 / 移除 / 文本变更 / 属性变更**，以及链接、表单、输入框、对话框的增删计数。
- 🏷️ **稳定定位路径**：每个元素拥有人类可读且稳定的 `path`，让两次快照的同一节点可被精确对齐。
- 🤖 **变化分类器**：自动归纳出 `navigation` / `modal_opened` / `modal_closed` / `content_update` / `structure_change` / `interactive_change` / `link_change` / `attribute_change` / `no_change`。
- 🌐 **多源输入**：支持 URL 抓取、本地 HTML 文件、stdin 管道、原始 HTML 字符串四种来源。
- 🧪 **自带测试**：标准库 `unittest` 全覆盖核心逻辑，零额外测试依赖。

---

## 🚀 快速开始

### 环境要求
- Python **3.8+**（无任何第三方依赖）

### 安装
```bash
pip install domforge
# 或从源码安装
git clone https://github.com/gitstq/domforge.git && cd domforge && pip install .
```

### 本地启动 / 一键运行
```bash
# 1) 抓取网页并生成结构摘要
domforge snap https://example.com

# 2) 抓取为 JSON 快照（供后续 diff 使用）
domforge snap https://example.com --format json --out before.json

# 3) 执行动作后再次抓取，比对变化
domforge snap https://example.com/after --format json --out after.json
domforge diff before.json after.json

# 4) 直接对比两段 HTML 字符串（无需网络）
domforge watch "<html><body><p>旧</p></body></html>" "<html><body><p>新</p></body></html>"
```

---

## 📖 详细使用指南

### `snap` —— 生成快照
```bash
domforge snap <SOURCE> [--format json|tree|summary] [--out FILE]
```
- `<SOURCE>` 自动识别：
  - 以 `http://` / `https://` 开头 → 抓取 URL
  - 等于 `-` → 从 stdin 读取
  - 本地文件存在 → 读取文件
  - 其他 → 直接作为 HTML 字符串
- `--format`：`json`（机器可读）、`tree`（缩进树形）、`summary`（统计摘要，默认）
- `--max-depth` / `--text-limit`：控制树形渲染深度与文本截断长度
- `--out`：将 JSON 快照写入文件

### `diff` / `watch` —— 比对变化
```bash
domforge diff <OLD> <NEW> [--format human|json]
domforge watch <OLD> <NEW>          # 等价于 diff --format human
```
两个参数同样支持 URL / 文件 / 字符串。`human` 输出人类友好的中文报告，`json` 输出结构化结果，便于 Agent 程序消费。

### 编程接口
```python
from domforge import parse_html, diff_snapshots

before = parse_html(html_before, url="https://x", source="url")
after  = parse_html(html_after,  url="https://x", source="url")

report = diff_snapshots(before, after)
print(report.classification)   # 例如 "modal_opened"
for c in report.added:
    print("新增：", c.path, c.tag)
```

---

## 💡 设计思路与迭代规划

**设计理念**：以「最小可比较信息」为原则——只保留对「页面是否变化、变化在哪」有意义的结构（标签、定位路径、可见文本、关键属性、交互元素），剔除脚本、样式、元数据等噪声。

**技术选型原因**：选用标准库 `html.parser` 而非 `lxml`/`beautifulsoup`，是为了贯彻账号「零依赖·离线优先」的基调，保证单文件可移植、无供应链风险。

**后续迭代计划**：
- 支持 CSS 选择器导出与「按选择器定位差异」
- 增加 `watch --serve` 模式，轮询 URL 并推送结构化变更事件（适配 Agent 长会话）
- 提供 `--mask` 脱敏规则，避免快照泄露敏感文本

**社区贡献方向**：欢迎补充更多「变化分类」启发式规则、增加多语言错误文案、提供浏览器插件桥接。

---

## 📦 打包与部署指南

- **类型**：命令行工具 + Python 库（插件 / 脚本 / 工具库类）。
- **打包**：本工具为零依赖纯 Python 包，无需编译。
  ```bash
  pip install build && python -m build     # 生成 wheel / sdist
  pip install twine && twine upload dist/*  # 发布到 PyPI
  ```
- **兼容环境**：Python 3.8+，Windows / macOS / Linux 全平台。
- **部署**：无需部署服务端；可作为 CLI 直接调用，或以库形式集成进 Agent 运行时。

---

## 🤝 贡献指南

1. Fork 本仓库并创建特性分支：`git checkout -b feat/your-feature`
2. 保持**零依赖**原则，新增逻辑请配套 `tests/` 下的 `unittest` 用例
3. 提交信息遵循 Angular 规范：`feat:` / `fix:` / `docs:` / `refactor:`
4. 提交 PR 并在描述中说明动机与自测结果

---

## 📄 开源协议

本项目基于 **MIT License** 开源，详见 [LICENSE](LICENSE)。可自由用于商业与非商业场景。
