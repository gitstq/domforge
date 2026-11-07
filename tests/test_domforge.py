"""domforge 单元测试（标准库 unittest，零依赖）。"""

import os
import subprocess
import sys
import tempfile
import unittest

from domforge import parse_html, diff_snapshots, classify_change, Snapshot
from domforge.fetch import read_file, resolve_source

HTML_A = """
<!doctype html>
<html lang="zh-CN">
<head><title>登录页</title><meta name="description" content="示例"></head>
<body>
  <header><h1>欢迎</h1></header>
  <main>
    <form action="/login">
      <input type="text" name="user" placeholder="用户名">
      <input type="password" name="pwd">
      <button type="submit">登入</button>
    </form>
    <nav><a href="/home">首页</a><a href="/about">关于</a></nav>
    <p>这是一段可见文本</p>
  </main>
</body>
</html>
"""

HTML_B = """
<!doctype html>
<html lang="zh-CN">
<head><title>登录成功</title><meta name="description" content="示例"></head>
<body>
  <header><h1>欢迎</h1></header>
  <main>
    <p role="alert">登录成功，欢迎回来！</p>
    <nav><a href="/home">首页</a><a href="/about">关于</a><a href="/logout">退出</a></nav>
  </main>
  <div role="dialog"><p>新消息：1 条</p></div>
</body>
</html>
"""


class TestParse(unittest.TestCase):
    def setUp(self):
        self.s = parse_html(HTML_A, url="http://example.com", source="url")

    def test_stats(self):
        self.assertEqual(self.s.stats.title, "登录页")
        self.assertEqual(self.s.stats.lang, "zh-CN")
        self.assertEqual(self.s.stats.description, "示例")
        self.assertEqual(self.s.stats.forms, 1)
        self.assertEqual(self.s.stats.inputs, 2)
        self.assertEqual(self.s.stats.buttons, 1)
        self.assertEqual(self.s.stats.links, 2)
        self.assertEqual(self.s.stats.headings.get("h1"), 1)
        # script/style 等被剔除，不应进入元素列表
        tags = {e.tag for e in self.s.elements}
        self.assertNotIn("script", tags)
        self.assertNotIn("head", tags)

    def test_paths_stable(self):
        paths = [e.path for e in self.s.elements]
        self.assertTrue(any(p.startswith("html/body/main/form/input") for p in paths))
        self.assertIn("html/body/main/nav/a[1]", paths)

    def test_fingerprint_deterministic(self):
        s2 = parse_html(HTML_A)
        self.assertEqual(self.s.fingerprint, s2.fingerprint)

    def test_serialize_roundtrip(self):
        d = self.s.to_dict()
        s2 = Snapshot.from_dict(d)
        self.assertEqual(s2.fingerprint, self.s.fingerprint)
        self.assertEqual(len(s2.elements), len(self.s.elements))


class TestDiff(unittest.TestCase):
    def setUp(self):
        self.a = parse_html(HTML_A)
        self.b = parse_html(HTML_B)

    def test_added_removed(self):
        rep = diff_snapshots(self.a, self.b)
        added_paths = {n.path for n in rep.added}
        removed_paths = {n.path for n in rep.removed}
        self.assertIn("html/body/div", added_paths)  # role=dialog
        self.assertIn("html/body/main/form", removed_paths)
        self.assertEqual(rep.dialogs_added, 1)
        self.assertEqual(rep.forms_removed, 1)
        self.assertEqual(rep.links_added, 1)   # /logout
        self.assertEqual(rep.links_removed, 0)

    def test_text_changed(self):
        rep = diff_snapshots(self.a, self.b)
        changed = {c.path for c in rep.text_changed}
        self.assertTrue(any("p" in p for p in changed))

    def test_classification(self):
        rep = diff_snapshots(self.a, self.b)
        self.assertEqual(rep.classification, "modal_opened")
        # 纯文本变化
        s1 = parse_html("<html><body><p>旧</p></body></html>")
        s2 = parse_html("<html><body><p>新内容</p></body></html>")
        self.assertEqual(classify_change(diff_snapshots(s1, s2), s1, s2),
                         "content_update")
        # 无变化
        self.assertEqual(classify_change(diff_snapshots(s1, s1), s1, s1),
                         "no_change")


class TestFetch(unittest.TestCase):
    def test_read_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(HTML_A)
            path = f.name
        try:
            self.assertIn("登录页", read_file(path))
        finally:
            os.unlink(path)

    def test_resolve_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write("<html><body><p>x</p></body></html>")
            path = f.name
        try:
            html, url, source = resolve_source(path)
            self.assertEqual(source, "file")
            self.assertIn("x", html)
        finally:
            os.unlink(path)

    def test_resolve_url(self):
        html, url, source = resolve_source("https://example.com")
        self.assertEqual(source, "url")
        self.assertIn("example", html.lower())


class TestCLI(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "domforge", *args],
            capture_output=True, text=True,
        )

    def test_version(self):
        r = self._run("--version")
        self.assertEqual(r.returncode, 0)
        self.assertIn("domforge", r.stdout)

    def test_snap_summary(self):
        r = self._run("snap", "<html><body><h1>标题</h1><a href='/x'>链接</a></body></html>")
        self.assertEqual(r.returncode, 0)
        self.assertIn("元素数", r.stdout)
        self.assertIn("链接", r.stdout)

    def test_diff_human(self):
        r = self._run("diff",
                      "<html><body><p>旧</p></body></html>",
                      "<html><body><p>新</p></body></html>")
        self.assertEqual(r.returncode, 0)
        self.assertIn("content_update", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
