"""HTML → DOM 结构快照解析器（基于标准库 html.parser，零依赖）。"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from .models import Element, Snapshot, SnapshotStats

# 这些标签不产生可见结构节点，仅用于元数据/资源/换行，从骨架中剔除
_SKIP_TAGS = {
    "script", "style", "noscript", "template", "head", "link",
    "meta", "base", "title", "br", "hr", "img", "source", "wbr", "col",
    "area", "track", "param",
}
# 这些标签内部文本不计入可见文本
_SUPPRESS_TEXT = {"script", "style", "noscript", "template"}
# 空元素（无子节点）：若入栈会变成错误的容器，需直接作为叶节点处理
_VOID_TAGS = {
    "input", "img", "br", "hr", "col", "source", "wbr", "area",
    "base", "embed", "link", "meta", "param", "track",
}

# 关注的属性（精简但足够用于定位与差异）
_ATTR_WHITELIST = {
    "id", "class", "name", "type", "role", "href", "src", "alt",
    "title", "placeholder", "value", "action", "method", "for", "lang",
    "name", "content",
    "aria-label", "aria-expanded", "aria-hidden", "aria-selected",
}

_IMPLICIT_ROLE = {
    "a": "link", "button": "button", "form": "form", "nav": "navigation",
    "main": "main", "header": "banner", "footer": "contentinfo",
    "section": "region", "article": "article", "ul": "list",
    "ol": "list", "li": "listitem", "table": "table", "img": "img",
    "search": "search", "dialog": "dialog",
}


def _clean_attrs(attrs: List[Tuple[str, Optional[str]]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in attrs:
        k = k.lower()
        if k in _ATTR_WHITELIST or k.startswith("aria-") or k.startswith("data-"):
            out[k] = (v or "")
    return out


def _role_of(tag: str, attrs: Dict[str, str]) -> Optional[str]:
    role = attrs.get("role") or attrs.get("aria-role")
    if role:
        return role
    if tag in _IMPLICIT_ROLE:
        if tag == "input":
            t = attrs.get("type", "").lower()
            if t in ("submit", "button", "reset"):
                return "button"
            return "textbox"
        return _IMPLICIT_ROLE[tag]
    return None


class _DomBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: List[Element] = []
        self.elements: List[Element] = []
        self.stats = SnapshotStats()
        self._sibling: Dict[Tuple[str, str], int] = {}
        self._suppress = 0
        self._in_title = False
        self._title_buf: List[str] = []

    # ---- 文本处理 ----
    def handle_data(self, data: str) -> None:
        if self._suppress > 0:
            return
        if self._in_title:
            self._title_buf.append(data)
            return
        if self.stack:
            self.stack[-1].text += data

    # ---- 标签处理 ----
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if tag in _SUPPRESS_TEXT:
            self._suppress += 1
        if tag == "title":
            self._in_title = True
            self._title_buf = []
        clean = _clean_attrs(attrs)
        if tag == "html":
            self.stats.lang = clean.get("lang", "")
        if tag == "meta":
            name = (clean.get("name") or "").lower()
            if name == "description":
                self.stats.description = clean.get("content", "")
        if tag in _SKIP_TAGS:
            return  # 不入栈、不计入结构

        parent = self.stack[-1].path if self.stack else ""
        key = (parent, tag)
        idx = self._sibling.get(key, 0)
        self._sibling[key] = idx + 1
        # 运行计数：同级同名元素总数，用于决定是否加 [index] 后缀
        total = self._sibling[key]
        suffix = f"[{idx}]" if total > 1 else ""
        path = f"{parent}/{tag}{suffix}" if parent else f"{tag}{suffix}"
        role = _role_of(tag, clean)
        el = Element(path=path, tag=tag, attrs=clean, role=role, index=idx)
        self._bump_stats(tag, clean, role)
        if tag in _VOID_TAGS:
            self.elements.append(el)  # 叶节点：不入栈，直接落库
        else:
            self.stack.append(el)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _SUPPRESS_TEXT and self._suppress > 0:
            self._suppress -= 1
        if tag == "title":
            self._in_title = False
            self.stats.title = " ".join(self._title_buf).strip()
            return
        if tag in _SKIP_TAGS:
            return
        # 弹出栈顶（容错：可能标签不匹配）
        if self.stack:
            el = self.stack.pop()
            el.text = el.text.strip()
            if el.text:
                el.text_hash = hashlib.sha1(
                    el.text.encode("utf-8", "replace")
                ).hexdigest()[:16]
            self.elements.append(el)

    def _bump_stats(self, tag: str, attrs: Dict[str, str], role: Optional[str]) -> None:
        self.stats.tag_counts[tag] = self.stats.tag_counts.get(tag, 0) + 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.stats.headings[tag] = self.stats.headings.get(tag, 0) + 1
        if tag == "a" and attrs.get("href"):
            self.stats.links += 1
        if tag == "form":
            self.stats.forms += 1
        if tag in ("input", "textarea", "select"):
            self.stats.inputs += 1
        if tag == "button" or (tag == "input" and attrs.get("type", "").lower() in ("submit", "button", "reset")):
            self.stats.buttons += 1
        if role == "dialog" or tag == "dialog":
            self.stats.dialogs += 1


def parse_html(html: str, url: str = "", source: str = "string") -> Snapshot:
    """将 HTML 文本解析为 DOM 结构快照。"""
    builder = _DomBuilder()
    builder.feed(html)
    builder.close()
    elements = builder.elements
    stats = builder.stats
    stats.total_elements = len(elements)
    stats.total_text_len = sum(len(e.text) for e in elements)
    # 稳定指纹：结构 + 可见文本
    sig = "\n".join(f"{e.path}|{e.text_hash}" for e in elements)
    fp = hashlib.sha1(sig.encode("utf-8", "replace")).hexdigest()[:24]
    return Snapshot(url=url, source=source, elements=elements, stats=stats, fingerprint=fp)


# 兼容别名
extract_snapshot = parse_html
