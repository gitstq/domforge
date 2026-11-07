"""快照差异引擎：精确回答「页面到底变了什么」。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import Snapshot

_ATTR_DIFF_KEYS = ("id", "class", "name", "type", "role", "href", "src",
                   "aria-expanded", "aria-hidden", "aria-selected", "aria-label")


@dataclass
class ChangeNode:
    path: str
    tag: str
    text: str = ""

    def to_dict(self) -> dict:
        return {"path": self.path, "tag": self.tag, "text": self.text}


@dataclass
class TextChange:
    path: str
    tag: str
    old_len: int
    new_len: int
    old_text: str = ""
    new_text: str = ""

    def to_dict(self) -> dict:
        return {
            "path": self.path, "tag": self.tag,
            "old_len": self.old_len, "new_len": self.new_len,
            "old_text": self.old_text, "new_text": self.new_text,
        }


@dataclass
class AttrChange:
    path: str
    tag: str
    changed: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"path": self.path, "tag": self.tag, "changed": self.changed}


@dataclass
class DiffReport:
    classification: str = "no_change"
    added: List[ChangeNode] = field(default_factory=list)
    removed: List[ChangeNode] = field(default_factory=list)
    text_changed: List[TextChange] = field(default_factory=list)
    attrs_changed: List[AttrChange] = field(default_factory=list)
    links_added: int = 0
    links_removed: int = 0
    forms_added: int = 0
    forms_removed: int = 0
    inputs_added: int = 0
    inputs_removed: int = 0
    dialogs_added: int = 0
    dialogs_removed: int = 0

    @property
    def changed(self) -> bool:
        return bool(self.added or self.removed or self.text_changed or self.attrs_changed)

    def to_dict(self) -> dict:
        return {
            "classification": self.classification,
            "added": [c.to_dict() for c in self.added],
            "removed": [c.to_dict() for c in self.removed],
            "text_changed": [c.to_dict() for c in self.text_changed],
            "attrs_changed": [c.to_dict() for c in self.attrs_changed],
            "links_added": self.links_added,
            "links_removed": self.links_removed,
            "forms_added": self.forms_added,
            "forms_removed": self.forms_removed,
            "inputs_added": self.inputs_added,
            "inputs_removed": self.inputs_removed,
            "dialogs_added": self.dialogs_added,
            "dialogs_removed": self.dialogs_removed,
        }


def _index(snap: Snapshot) -> Dict[str, object]:
    return {e.path: e for e in snap.elements}


def diff_snapshots(old: Snapshot, new: Snapshot) -> DiffReport:
    rep = DiffReport()
    a = _index(old)
    b = _index(new)

    for path in a:
        if path not in b:
            el = a[path]
            rep.removed.append(ChangeNode(path=path, tag=el.tag, text=el.text[:80]))
            if el.tag == "a" and el.attrs.get("href"):
                rep.links_removed += 1
            if el.tag == "form":
                rep.forms_removed += 1
            if el.tag in ("input", "textarea", "select"):
                rep.inputs_removed += 1
            if el.role == "dialog" or el.tag == "dialog":
                rep.dialogs_removed += 1

    for path in b:
        el = b[path]
        if path not in a:
            rep.added.append(ChangeNode(path=path, tag=el.tag, text=el.text[:80]))
            if el.tag == "a" and el.attrs.get("href"):
                rep.links_added += 1
            if el.tag == "form":
                rep.forms_added += 1
            if el.tag in ("input", "textarea", "select"):
                rep.inputs_added += 1
            if el.role == "dialog" or el.tag == "dialog":
                rep.dialogs_added += 1
            continue
        # 同时存在：比较文本与属性
        oe = a[path]
        if oe.text_hash != el.text_hash and (oe.text or el.text):
            rep.text_changed.append(TextChange(
                path=path, tag=el.tag,
                old_len=len(oe.text), new_len=len(el.text),
                old_text=oe.text[:120], new_text=el.text[:120],
            ))
        changed = {}
        keys = set(_ATTR_DIFF_KEYS) | set(oe.attrs) | set(el.attrs)
        for k in keys:
            ov, nv = oe.attrs.get(k, ""), el.attrs.get(k, "")
            if ov != nv:
                changed[k] = {"old": ov, "new": nv}
        if changed:
            rep.attrs_changed.append(AttrChange(path=path, tag=el.tag, changed=changed))

    rep.classification = classify_change(rep, old, new)
    return rep


def classify_change(rep: DiffReport, old: Snapshot, new: Snapshot) -> str:
    """将差异归纳为一个最贴切的变化类型。"""
    if old.source == "url" and new.source == "url" and old.url != new.url:
        return "navigation"
    if rep.dialogs_added > 0:
        return "modal_opened"
    if rep.dialogs_removed > 0:
        return "modal_closed"
    struct = len(rep.added) + len(rep.removed)
    if struct >= 3 and len(rep.text_changed) <= struct:
        return "structure_change"
    if rep.forms_added or rep.forms_removed or rep.inputs_added or rep.inputs_removed:
        return "interactive_change"
    if rep.links_added or rep.links_removed:
        return "link_change"
    if rep.text_changed:
        return "content_update"
    if rep.attrs_changed:
        return "attribute_change"
    if struct > 0:
        return "structure_change"
    return "no_change"
