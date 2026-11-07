# 📋 项目孵化执行报告 / Project Incubation Report

| 项目 | 内容 |
| --- | --- |
| **执行日期** | 2026-11-07（GMT+8） |
| **项目名称** | **domforge** |
| **GitHub 仓库** | https://github.com/gitstq/domforge |
| **Release 发布地址** | 无（工具/库类，按分类规则无需上传 Release） |
| **项目类型** | 命令行工具 + Python 库 |
| **发布状态** | 已建仓并推送 `main` 分支（3 个 Angular 提交），公开可访问 ✅ |

---

## 🎯 项目核心功能

`domforge` 是一个**零依赖 · 离线优先**的网页 DOM 结构快照与差异引擎，专为 AI Agent 网页自动化设计。它能离线回答一个关键问题：**「Agent 执行点击/提交/跳转后，页面到底变了什么？」**

- `snap`：将网页（URL / 本地文件 / stdin / 原始字符串）解析为「标签树 + 交互元素清单 + 聚合统计」三件套，支持 JSON / 树形 / 摘要输出。
- `diff` / `watch`：逐节点比对两次快照，精确列出**新增 / 移除 / 文本变更 / 属性变更**，以及链接、表单、输入框、对话框的增删计数。
- **稳定定位路径**：每个元素拥有人类可读且稳定的 `path`（如 `html/body/main/nav/a[1]`），使跨快照匹配精确到节点。
- **变化分类器**：自动归纳 `navigation` / `modal_opened` / `modal_closed` / `content_update` / `structure_change` / `interactive_change` / `link_change` / `attribute_change` / `no_change`。

## ✨ 自研差异化亮点

- 基于标准库 `html.parser` **自研** DOM 骨架提取，无需浏览器、无需网络（解析本地即可），规避所有版权与供应链风险。
- 引入稳定定位路径与变化分类器，把「页面变化」翻译成 Agent 可直接消费的结论，填补账号「Agent 网页可观测性」空白（既有工具覆盖 Agent 安全/审计，未覆盖可观测性）。
- 与 GitHub Trending 热门方向（Agent 浏览器自动化）强相关，且与该账号 1741 个现有仓库相似度远低于 60%（去重校验：`dom`/`browser`/`scrape`/`agent-trace` 关键词命中均为 0）。

## 🌐 文档覆盖语言版本

- **简体中文**（`README.md`）
- **繁体中文**（`README.zh-TW.md`）
- **English**（`README.en.md`）

三份文档顶部均提供**可点击语言切换**；统一覆盖 8 项强制章节（项目介绍 / 核心特性 / 快速开始 / 详细指南 / 设计思路 / 打包部署 / 贡献指南 / 开源协议）。

## 🛠️ 核心技术栈与环境要求

- **技术栈**：Python 3.8+ 标准库（`html.parser` / `urllib` / `argparse`），**零第三方依赖**。
- **环境要求**：Python ≥ 3.8，无需编译、无网络依赖。
- **快速启动**：
  ```bash
  pip install domforge
  domforge snap https://example.com
  domforge watch "<html><body><p>旧</p></body></html>" "<html><body><p>新</p></body></html>"
  ```

## ⚠️ 执行过程异常说明

- 首次推送被 GitHub 拒绝（`non-fast-forward`）：创建仓库时携带 `license_template` 导致远端自动生成了一个 `LICENSE` 文件，与本地历史无关联。
- **处理**：删除该空仓并以 `auto_init:false` 且无 license 模板重建，使用自带 `LICENSE` 后正常推送，未发生强制推送（force push），历史干净。

## 💡 后续迭代建议

1. 支持 CSS 选择器导出与「按选择器定位差异」。
2. 增加 `watch --serve` 轮询模式，向 Agent 长会话推送结构化变更事件。
3. 提供 `--mask` 脱敏规则，避免快照泄露敏感文本。
4. 可选：发布至 PyPI（当前按规则暂未发布 Release）。
