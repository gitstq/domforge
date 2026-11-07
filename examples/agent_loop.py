"""示例：AI Agent 如何利用 domforge 验证「点击」是否生效。

场景：Agent 在登录页点击「提交」按钮，需要离线确认页面已经跳转到「登录成功」。
不依赖截图，只需在动作前后各抓一次快照并 diff 即可。
"""

from domforge import parse_html, diff_snapshots, classify_change

PAGE_BEFORE = """
<html lang="zh-CN"><head><title>登录页</title></head><body>
  <main><form action="/login">
    <input type="text" name="user">
    <input type="password" name="pwd">
    <button type="submit">登入</button>
  </form></main>
</body></html>
"""

PAGE_AFTER = """
<html lang="zh-CN"><head><title>登录成功</title></head><body>
  <main><p role="alert">登录成功，欢迎回来！</p></main>
  <div role="dialog"><p>新消息：1 条</p></div>
</body></html>
"""


def main() -> None:
    before = parse_html(PAGE_BEFORE, url="https://app.example.com/login", source="string")
    after = parse_html(PAGE_AFTER, url="https://app.example.com/home", source="string")

    report = diff_snapshots(before, after)
    kind = classify_change(report, before, after)

    print(f"变化类型      : {kind}")
    print(f"移除的表单数  : {report.forms_removed}")
    print(f"新增的对话框  : {report.dialogs_added}")
    print(f"标题          : {before.stats.title} → {after.stats.title}")

    if kind in ("navigation", "modal_opened", "content_update"):
        print("✅ 判定：点击已生效，可继续下一步。")
    else:
        print("⚠️ 判定：页面未如预期变化，建议重试或报错。")


if __name__ == "__main__":
    main()
