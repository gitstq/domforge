"""获取模块：从 URL 抓取或从本地文件/字符串读取 HTML（零依赖）。"""

from __future__ import annotations

import os
import sys
import urllib.request
from typing import Tuple

_DEFAULT_UA = (
    "Mozilla/5.0 (compatible; domforge/1.0; +https://github.com/gitstq/domforge)"
)


def _decode(body: bytes, content_type: str = "") -> str:
    charset = "utf-8"
    for part in content_type.split(";"):
        part = part.strip().lower()
        if part.startswith("charset="):
            charset = part.split("=", 1)[1].strip() or "utf-8"
    try:
        return body.decode(charset, errors="replace")
    except (LookupError, ValueError):
        return body.decode("utf-8", errors="replace")


def fetch_url(url: str, timeout: float = 15.0,
              user_agent: str = _DEFAULT_UA) -> str:
    """抓取 URL 并返回解码后的 HTML 文本。"""
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    return _decode(body, ctype)


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def resolve_source(spec: str) -> Tuple[str, str, str]:
    """将输入规格解析为 (html, url, source)。

    - 以 http:// / https:// 开头 → 视为 URL
    - 等于 "-" → 从 stdin 读取
    - 本地文件存在 → 读取文件
    - 其他 → 直接作为 HTML 字符串
    """
    if spec.startswith(("http://", "https://")):
        html = fetch_url(spec)
        return html, spec, "url"
    if spec == "-":
        html = sys.stdin.read()
        return html, "<stdin>", "string"
    if os.path.isfile(spec):
        return read_file(spec), os.path.abspath(spec), "file"
    # 兜底：当作原始 HTML
    return spec, "<string>", "string"
