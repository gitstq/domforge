"""数据模型：元素记录、快照与统计信息。"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class Element:
    """DOM 中一个可定位元素的精简记录。

    path 采用稳定且可读的定位串，例如
    ``html/body/div#app/main/section[0]/h1``，用于跨快照稳定匹配。
    """

    path: str
    tag: str
    text: str = ""
    text_hash: str = ""
    attrs: Dict[str, str] = field(default_factory=dict)
    role: Optional[str] = None
    index: int = 0  # 同级同名元素中的序号

    def __post_init__(self) -> None:
        if not self.text_hash and self.text:
            self.text_hash = hashlib.sha1(
                self.text.encode("utf-8", "replace")
            ).hexdigest()[:16]


@dataclass
class SnapshotStats:
    """快照聚合统计，便于快速判断页面性质与规模。"""

    title: str = ""
    lang: str = ""
    description: str = ""
    total_elements: int = 0
    total_text_len: int = 0
    links: int = 0
    forms: int = 0
    inputs: int = 0
    buttons: int = 0
    dialogs: int = 0
    headings: Dict[str, int] = field(default_factory=dict)  # h1..h6 -> count
    tag_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class Snapshot:
    """一次页面抓取的完整快照。"""

    url: str
    source: str  # "url" | "file" | "string"
    elements: List[Element] = field(default_factory=list)
    stats: SnapshotStats = field(default_factory=SnapshotStats)
    fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "source": self.source,
            "fingerprint": self.fingerprint,
            "stats": asdict(self.stats),
            "elements": [asdict(e) for e in self.elements],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        stats = SnapshotStats(**data.get("stats", {}))
        elems = [Element(**e) for e in data.get("elements", [])]
        return cls(
            url=data.get("url", ""),
            source=data.get("source", ""),
            elements=elems,
            stats=stats,
            fingerprint=data.get("fingerprint", ""),
        )

    def to_tree(self, max_depth: int = 999, text_limit: int = 60) -> str:
        """以可读缩进树的形式渲染快照结构。"""
        lines: List[str] = []
        for el in self.elements:
            depth = el.path.count("/")
            if depth > max_depth:
                continue
            pad = "  " * depth
            label = el.tag
            if el.attrs.get("id"):
                label += f"#{el.attrs['id']}"
            if el.attrs.get("class"):
                label += f".{el.attrs['class'].split()[0]}"
            if el.role:
                label += f" [{el.role}]"
            line = f"{pad}{label}"
            if el.text:
                t = el.text if len(el.text) <= text_limit else el.text[:text_limit] + "…"
                line += f"  «{t}»"
            lines.append(line)
        return "\n".join(lines)
