"""domforge — 零依赖·离线优先的网页 DOM 结构快照与差异引擎。

专为 AI Agent 网页自动化设计：在 agent 执行点击/提交等动作前后，
离线对比页面 DOM 结构，精确回答「页面到底变了什么」。
"""

from .models import Element, Snapshot, SnapshotStats
from .parser import extract_snapshot, parse_html
from .diff import DiffReport, diff_snapshots, classify_change
from .fetch import fetch_url

__version__ = "1.0.0"
__all__ = [
    "Element",
    "Snapshot",
    "SnapshotStats",
    "extract_snapshot",
    "parse_html",
    "DiffReport",
    "diff_snapshots",
    "classify_change",
    "fetch_url",
    "__version__",
]
