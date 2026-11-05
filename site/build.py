"""Build both seven-lesson routes from the course Markdown."""
from html import escape, unescape
import json
from pathlib import Path
import re
from shutil import copyfile

from markdown import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ART = ROOT / "assets/lessons/01/illustrations/ai-two-layers.svg"
SITE_NAME = "爸妈的 Mac 与 AI 课"
ROUTES = {"dad": "爸爸", "mom": "妈妈"}
HEADINGS = {
    "dad": ("认识 AI，跑通 DeepSeek", "分清工具与模型，用自己的 DeepSeek 账户在 Codex 收到第一条回复。"),
    "mom": ("把新 Mac 用起来", "装好豆包，试一次屏幕共享，再确认腾讯会议可以入会。"),
}
def write(relative, title, body):
    path = DOCS / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = "../" if path.parent != DOCS else ""
    path.write_text(f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · {SITE_NAME}</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="bar"><div class="wrap">
<a class="brand" href="{prefix}index.html">{SITE_NAME}</a>
<span class="quiet">家庭课程</span>
</div></header>
<main class="wrap">{body}</main>
<footer class="wrap footer"><a href="{prefix}index.html">返回首页</a><span lang="en-GB">© 2026 Hao Li · <a href="mailto:hli@sdu.dk">hli@sdu.dk</a> · All rights reserved.</span></footer>
</body>
</html>
''', encoding="utf-8")


def home():
    cards = []
    for route, name in ROUTES.items():
        _, description = HEADINGS[route]
        cards.append(f'''<a class="route {route}" href="{route}/index.html">
<div class="portrait"><img src="assets/{route}.svg" alt="" width="300" height="220"></div>
<div class="route-info"><h2>{name}的课程</h2><p>{description}</p><span class="enter">打开课表 →</span></div></a>''')
    write("index.html", "首页", f'''<section class="intro">
<p class="kicker">家庭练习 · 持续更新</p><h1>爸妈的 Mac 与 AI 课</h1>
<p class="lead">按学习路线浏览，或搜索课里的操作和概念。</p>
<section class="course-search" aria-labelledby="search-title">
<h2 id="search-title">搜索课程</h2>
<form role="search"><label for="course-query">关键词</label>
<input id="course-query" type="search" placeholder="例如：屏幕共享、API Key" autocomplete="off"></form>
<p class="quiet">搜索已上线课程的标题和正文。</p>
<p id="search-status" role="status"></p><ul id="search-results"></ul>
</section>
<script defer src="assets/search-index.js"></script><script defer src="assets/search.js"></script>
</section><div class="routes">{''.join(cards)}</div>''')


def schedule(route, name, rows):
    items = [
        f'<li><span lang="en-GB">Lesson {number}</span>'
        f'<span><a href="lesson-{number:02}.html">{escape(title)}</a></span>'
        f'<small>{escape(mode)}</small></li>'
        for number, (mode, title) in enumerate(rows, 1)
    ]
    write(f"{route}/index.html", f"{name}的课表", f'''<section class="intro">
<p class="kicker">学习路线</p><h1>{name}的课程</h1>
<p class="lead">选择一节课开始，也可以从首页搜索课程里的操作和概念。</p>
</section><ol class="schedule">{''.join(items)}</ol>''')


def course_links(body, route, source_path):
    def convert(match):
        url = unescape(match[1])
        lesson = re.fullmatch(r"(0[1-7])\.md(?:#(dad|mom))?", url)
        if lesson:
            number, target = lesson.groups()
            path = f"lesson-{number}.html"
            if target and target != route:
                path = f"../{target}/{path}"
            return f'href="{path}"'
        if url.startswith("../../assets/"):
            asset = (source_path.parent / url).resolve()
            relative = asset.relative_to(ROOT / "assets")
            destination = DOCS / "assets" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            copyfile(asset, destination)
            return f'href="../assets/{escape(relative.as_posix())}" download'
        return match[0]

    return re.sub(r'href="([^"]+)"', convert, body)


def lesson(route, name, source, source_path, number, mode, heading, count):
    title, description = HEADINGS[route] if number == 1 else (heading, "")
    sections = re.split(r"(?m)^### (.+)\n", source.strip())
    jump = [
        f'<li><a href="#step-{step}">{escape(label)}</a></li>'
        for step, label in enumerate(sections[1::2], 1)
    ]
    diagram = '''<figure>
<img class="diagram" src="../assets/ai-two-layers.svg" alt="上层是用来交代任务的电脑界面，下层是处理输入并生成回答的模型。" width="840" height="330">
<figcaption>上层负责交互，下层生成回答。爸爸这台 Mac 的连接方式如下。</figcaption>
<div class="model-line"><span>上层 · Codex 界面</span><b aria-label="接入">→</b><span>下层 · DeepSeek 模型</span></div>
</figure>'''
    if not ART.is_file():
        diagram = diagram.replace(diagram.splitlines()[1] + "\n", "")
    source = re.sub(r"```mermaid\n.*?```", lambda _: diagram, source, flags=re.S)
    body = markdown(source, extensions=["tables", "fenced_code"])
    body = course_links(body, route, source_path)
    ids = iter(range(1, len(jump) + 1))
    body = re.sub(r"<h3>(.*?)</h3>", lambda m: f'<h2 id="step-{next(ids)}">{m[1]}</h2>', body)
    prep = result = ""
    if number == 1:
        need = "自己的 Mac、DeepSeek 开放平台账户（可现场注册）、一段可独立操作的时间。" if route == "dad" else "已联网的 Mac、Apple 账户、家人发来的腾讯会议测试邀请。"
        done = "Codex 收到测试回复。若用量尚未显示，记下时间，下次再核对。" if route == "dad" else "能在 Mac 上从邀请链接入会，请家人确认声音，并试一次共享练习窗口。"
        prep = f'<div class="callout"><p><strong>课前准备</strong>　{need}</p></div>'
        result = f'<aside class="callout"><p><strong>做到这里就可以</strong>　{done}</p></aside>'
    toc = f'<nav class="jump" aria-label="本节步骤"><strong>本节步骤</strong><ul>{"".join(jump)}</ul></nav>' if jump else ""
    neighbours = []
    if number > 1:
        neighbours.append(f'<a href="lesson-{number - 1:02}.html">← 第 {number - 1} 节</a>')
    neighbours.append(f'<a href="index.html">返回{name}的课表</a>')
    if number < count:
        neighbours.append(f'<a href="lesson-{number + 1:02}.html">第 {number + 1} 节 →</a>')
    if route == "dad" and number <= 3:
        neighbours.append(f'<a href="../mom/lesson-{number + 4:02}.html">返回妈妈第 {number + 4} 节</a>')
    summary = f'<p class="lead">{escape(description)}</p>' if description else ""
    write(f"{route}/lesson-{number:02}.html", f"第 {number} 节 · {name}", f'''<article class="lesson">
<section class="intro"><p><a href="index.html">← 返回{name}的课表</a></p>
<p class="kicker"><span lang="en-GB">Lesson {number}</span> · {name} · {escape(mode)}</p>
<h1>{escape(title)}</h1>{summary}</section>
{prep}{toc}
<div class="content" id="{route}">{body}</div>
{result}
<nav class="lesson-nav" aria-label="课次导航">{"".join(neighbours)}</nav>
</article>''')

    index = []
    for step, (label, section) in enumerate(zip([title] + sections[1::2], sections[::2])):
        section = re.sub(r"```mermaid\n.*?```", "", section, flags=re.S)
        plain = unescape(re.sub(r"<[^>]+>", " ", markdown(section, extensions=["tables", "fenced_code"])))
        if not plain.strip():
            continue
        anchor = f"step-{step}" if step else route
        index.append({
            "title": f"{name} · 第 {number} 节 · {title}",
            "heading": label if step else "",
            "text": " ".join(plain.split()),
            "url": f"{route}/lesson-{number:02}.html#{anchor}",
        })
    return index


def main():
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    copyfile(ROOT / "site/style.css", DOCS / "assets/style.css")
    if ART.is_file():
        copyfile(ART, DOCS / "assets/ai-two-layers.svg")
    home()
    table = [line.split("|")[1:-1] for line in (ROOT / "README.md").read_text().splitlines()
             if line.startswith("| [第 ")]
    search_entries = []
    copyfile(ROOT / "site/search.js", DOCS / "assets/search.js")
    for index, (route, name) in enumerate(ROUTES.items()):
        copyfile(ROOT / f"assets/site/{route}.svg", DOCS / f"assets/{route}.svg")
        schedule(route, name, [(row[1].strip(), row[index + 2].strip()) for row in table])
        for number, row in enumerate(table, 1):
            path = ROOT / f"course/lessons/{number:02}.md"
            source = path.read_text(encoding="utf-8")
            match = re.search(rf"(?ms)^## {name}｜([^\n]+)\n(.*?)(?=^## |\Z)", source)
            heading, body = match.groups()
            search_entries.extend(lesson(route, name, body, path, number, row[1].strip(), heading, len(table)))
    index_js = "window.courseSearchIndex = " + json.dumps(search_entries, ensure_ascii=False) + ";\n"
    (DOCS / "assets/search-index.js").write_text(index_js, encoding="utf-8")


if __name__ == "__main__":
    main()
