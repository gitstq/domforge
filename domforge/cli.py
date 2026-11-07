"""命令行入口：snap / diff / watch。"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .fetch import resolve_source
from .models import Snapshot
from .parser import parse_html
from .diff import diff_snapshots


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="domforge",
        description="零依赖·离线优先的网页 DOM 结构快照与差异引擎（AI Agent 网页自动化可观测性工具）",
    )
    p.add_argument("--version", action="version", version="domforge 1.0.0")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("snap", help="抓取/解析页面并生成 DOM 结构快照")
    ps.add_argument("source", help="URL、本地 HTML 文件路径、-（stdin）或原始 HTML 字符串")
    ps.add_argument("--format", choices=["json", "tree", "summary"], default="summary")
    ps.add_argument("--max-depth", type=int, default=999, help="树形渲染最大深度")
    ps.add_argument("--text-limit", type=int, default=60, help="树形文本截断长度")
    ps.add_argument("--out", help="将快照 JSON 写入该文件")

    pd = sub.add_parser("diff", help="对比两次快照，回答「页面变了什么」")
    pd.add_argument("old", help="旧状态：URL / 文件 / - / 原始 HTML")
    pd.add_argument("new", help="新状态：URL / 文件 / - / 原始 HTML")
    pd.add_argument("--format", choices=["human", "json"], default="human")

    pw = sub.add_parser("watch", help="等价于 diff --format human（观察变化）")
    pw.add_argument("old")
    pw.add_argument("new")
    return p


def _load(spec: str) -> Snapshot:
    html, url, source = resolve_source(spec)
    return parse_html(html, url=url, source=source)


def _cmd_snap(args: argparse.Namespace) -> int:
    snap = _load(args.source)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(snap.to_json())
        print(f"已写入快照 JSON：{args.out}", file=sys.stderr)
    if args.format == "json":
        print(snap.to_json())
    elif args.format == "tree":
        print(snap.to_tree(max_depth=args.max_depth, text_limit=args.text_limit))
    else:
        _print_summary(snap)
    return 0


def _print_summary(snap: Snapshot) -> None:
    s = snap.stats
    print(f"来源   : {snap.source}  {snap.url}")
    print(f"指纹   : {snap.fingerprint}")
    print(f"标题   : {s.title}")
    print(f"语言   : {s.lang}")
    print(f"元素数 : {s.total_elements}    文本总长: {s.total_text_len}")
    print(f"链接   : {s.links}   表单: {s.forms}   输入: {s.inputs}   "
          f"按钮: {s.buttons}   对话框: {s.dialogs}")
    if s.headings:
        hs = " ".join(f"{k}×{v}" for k, v in sorted(s.headings.items()))
        print(f"标题层级: {hs}")
    top = sorted(s.tag_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    print("标签Top: " + ", ".join(f"{t}:{c}" for t, c in top))


def _cmd_diff(args: argparse.Namespace) -> int:
    old = _load(args.old)
    new = _load(args.new)
    rep = diff_snapshots(old, new)
    if args.format == "json":
        print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2))
    else:
        _print_diff(rep, old, new)
    return 0


def _print_diff(rep, old: Snapshot, new: Snapshot) -> None:
    print(f"变化类型: {rep.classification}")
    print(f"  旧指纹 {old.fingerprint}  →  新指纹 {new.fingerprint}")
    print(f"  新增结构节点: {len(rep.added)}   移除: {len(rep.removed)}   "
          f"文本变更: {len(rep.text_changed)}   属性变更: {len(rep.attrs_changed)}")
    if rep.links_added or rep.links_removed:
        print(f"  链接: +{rep.links_added} / -{rep.links_removed}")
    if rep.forms_added or rep.forms_removed:
        print(f"  表单: +{rep.forms_added} / -{rep.forms_removed}")
    if rep.inputs_added or rep.inputs_removed:
        print(f"  输入: +{rep.inputs_added} / -{rep.inputs_removed}")
    if rep.added:
        print("  ➕ 新增:")
        for n in rep.added[:20]:
            t = f" «{n.text}»" if n.text else ""
            print(f"     {n.path}  [{n.tag}]{t}")
    if rep.removed:
        print("  ➖ 移除:")
        for n in rep.removed[:20]:
            t = f" «{n.text}»" if n.text else ""
            print(f"     {n.path}  [{n.tag}]{t}")
    if rep.text_changed:
        print("  ✏️  文本变更:")
        for c in rep.text_changed[:20]:
            print(f"     {c.path} [{c.tag}] {c.old_len}→{c.new_len}  "
                  f"\"{c.old_text}\" → \"{c.new_text}\"")


def main(argv: List[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "snap":
        return _cmd_snap(args)
    if args.cmd in ("diff", "watch"):
        return _cmd_diff(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
