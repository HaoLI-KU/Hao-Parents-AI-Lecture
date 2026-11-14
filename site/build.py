"""Build the family course site from the course Markdown."""
from html import escape, unescape
import json
from pathlib import Path
from shutil import copyfile, rmtree
import re
from urllib.parse import quote

from markdown import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE_NAME = "爸妈的 AI 课"
SITE_FULL = "爸妈的 Mac 与 AI 课"
SITE_TAGLINE = "家庭课程 · 持续更新"
ROUTES = ("dad", "mom")
ROUTE_META = {
    "dad": {
        "name": "爸爸",
        "title": "爸爸的课程",
        "blurb": "从自己的 DeepSeek 账户开始，把一份真实的 Word 技术文档逐步变成可维护、可复用的中文 LaTeX 项目。",
        "focus": "DeepSeek · Harness · Word → LaTeX",
    },
    "mom": {
        "name": "妈妈",
        "title": "妈妈的课程",
        "blurb": "先把新 Mac、会议、邮件和家庭共享用顺，再用豆包和 DeepSeek Harness 做出自己的养花小站。",
        "focus": "Mac 基础 · 豆包 · 养花小站",
    },
}
PRACTICE = {
    "slug": "github",
    "file": "github.md",
    "title": "爸妈第一次用 GitHub",
    "blurb": "各自注册账号、建立私有仓库，用 Harness 完成第一次提交和推送。",
}
LESSON_LINK = re.compile(r"(\d{2})\.md(?:#(dad|mom))?")
NAV_ITEMS = (
    ("home", "首页", "index.html"),
    ("dad", "爸爸的课程", "dad/index.html"),
    ("mom", "妈妈的课程", "mom/index.html"),
    ("practice", "共同练习", "practice/github.html"),
)


def rel_prefix(path):
    return "../" * (len(path.relative_to(DOCS).parts) - 1)


def brand(prefix):
    return (
        f'<a class="brand" href="{prefix}index.html">'
        '<span class="brand-mark" aria-hidden="true">AI</span>'
        f'<span class="brand-text"><span class="brand-name">{SITE_NAME}</span>'
        '<span class="brand-role">家庭课程</span></span></a>'
    )


def write_page(path, title, description, body, active, route=None,
               page_type="page", scripts=()):
    path = DOCS / path
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = rel_prefix(path)
    nav = []
    for key, label, href in NAV_ITEMS:
        attributes = f' href="{prefix}{href}"'
        if active == key:
            attributes += ' class="is-active"'
            attributes += ' aria-current="page"' if page_type in ("home", "schedule", "practice") else ' aria-current="true"'
        nav.append(f"<a{attributes}>{label}</a>")
    footer_nav = "".join(
        f'<a href="{prefix}{href}">{label}</a>'
        for _, label, href in NAV_ITEMS + (("search", "搜索", "search.html"),)
    )
    body_class = f"page-{page_type}"
    if route:
        body_class += f" route-{route}"
    document_title = title if title == SITE_FULL else f"{title} · {SITE_FULL}"
    script_tags = "".join(
        f'<script defer src="{prefix}assets/{name}"></script>' for name in ("ui.js",) + tuple(scripts)
    )
    path.write_text(
        f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(document_title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="theme-color" content="#f7f6f2">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body class="{body_class}">
<a class="skip-link" href="#main">跳到正文</a>
<header class="site-header" data-site-header>
<div class="wrap header-inner">
{brand(prefix)}
<nav class="site-nav" id="siteNav" aria-label="主导航">{''.join(nav)}</nav>
<form class="header-search" action="{prefix}search.html" method="get" role="search">
<label class="sr-only" for="header-q">搜索课程</label>
<input id="header-q" name="q" type="search" placeholder="搜索课程" autocomplete="off">
<button type="submit">搜索</button>
</form>
<button class="menu-toggle" type="button" aria-label="打开导航菜单" aria-expanded="false" aria-controls="siteNav"><span class="menu-icon" aria-hidden="true"></span></button>
</div>
</header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="wrap footer-inner">
<div class="footer-brand"><span class="brand-mark" aria-hidden="true">AI</span><span><strong>{SITE_FULL}</strong><small>{SITE_TAGLINE}</small></span></div>
<nav class="footer-nav" aria-label="页脚导航">{footer_nav}</nav>
<p class="footer-copy" lang="en-GB">© 2026 Hao Li · <a href="mailto:hli@sdu.dk">hli@sdu.dk</a> · All rights reserved.</p>
</div></footer>
{script_tags}
</body>
</html>
''',
        encoding="utf-8",
    )


def route_content(source, name):
    match = re.search(rf"(?ms)^## {re.escape(name)}｜([^\n]+)\n(.*?)(?=^## |\Z)", source)
    return match.groups() if match else None


def markdown_html(text):
    return markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


def plain(text):
    html = markdown_html(text)
    html = re.sub(r"<[^>]+>", " ", html)
    return " ".join(unescape(html).split())


def excerpt(text, limit=140):
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


def clean_mode(mode):
    return re.sub(r"\s*·\s*(?:草稿|后续课)\s*$", "", mode).strip()


def status_label(status):
    return {"draft": "草稿", "followup": "后续课"}.get(status, "")


def parse_schedule():
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    try:
        header_index = next(i for i, line in enumerate(lines) if line.startswith("| 课稿 |"))
    except StopIteration:
        raise SystemExit("README 里找不到课表表头：| 课稿 |")
    columns = [cell.strip() for cell in lines[header_index].strip().strip("|").split("|")]
    index = {cell: position for position, cell in enumerate(columns)}
    required = {"课稿", "爸爸方式", "爸爸", "妈妈方式", "妈妈"}
    missing = required - set(index)
    if missing:
        raise SystemExit("README 课表缺少列：" + "、".join(sorted(missing)))
    rows = {route: [] for route in ROUTES}
    for line in lines[header_index + 1:]:
        if not line.startswith("| ["):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(columns):
            raise SystemExit(f"README 课表列数不一致：{line}")
        number_match = re.search(r"(\d{2})\.md", cells[0])
        if not number_match:
            continue
        number = int(number_match.group(1))
        for route in ROUTES:
            name = ROUTE_META[route]["name"]
            mode = cells[index[f"{name}方式"]]
            title = cells[index[name]]
            if title in ("", "—"):
                continue
            status = "draft" if "草稿" in mode else "followup" if "后续课" in mode else "active"
            rows[route].append({
                "route": route,
                "number": number,
                "mode": mode,
                "title": title,
                "status": status,
                "file": f"{number:02}.md",
            })
    for route, items in rows.items():
        numbers = [item["number"] for item in items]
        if len(numbers) != len(set(numbers)):
            raise SystemExit(f"{ROUTE_META[route]['name']}路线有重复课号：{numbers}")
        items.sort(key=lambda item: item["number"])
        for item in items:
            path = ROOT / "course/lessons" / item["file"]
            if not path.is_file():
                raise SystemExit(f"课表指向的课稿不存在：{path}")
            if not route_content(path.read_text(encoding="utf-8"), ROUTE_META[route]["name"]):
                raise SystemExit(
                    f"{path} 里没有“## {ROUTE_META[route]['name']}｜…”小节，但 README 课表有这一行")
    return rows


def split_sections(body, level):
    pattern = r"(?m)^%s (.+)$" % ("#" * level)
    parts = re.split(pattern, body.strip())
    intro = parts[0].strip()
    headings = parts[1::2]
    bodies = parts[2::2]
    return intro, list(zip(headings, bodies))


def copy_asset(url, source_path):
    asset = (source_path.parent / url).resolve()
    try:
        relative = asset.relative_to(ROOT / "assets")
    except ValueError:
        raise SystemExit(f"练习素材不在 assets/ 下：{url}")
    if not asset.is_file():
        raise SystemExit(f"课稿引用的练习素材不存在：{asset}")
    destination = DOCS / "assets" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    copyfile(asset, destination)
    return relative.as_posix()


def resolve_links(html, route, prefix, source_path):
    def repl(match):
        attribute, url = match.group(1), unescape(match.group(2))
        if url == PRACTICE["file"] or url.startswith(PRACTICE["file"] + "#"):
            suffix = url[len(PRACTICE["file"]):]
            return f'{attribute}="{prefix}practice/{PRACTICE["slug"]}.html{suffix}"'
        lesson = LESSON_LINK.fullmatch(url)
        if lesson and attribute == "href":
            number, target = lesson.groups()
            target_route = target or route
            if target_route == route:
                new = f"lesson-{number}.html"
            else:
                new = f"{prefix}{target_route}/lesson-{number}.html"
            if target:
                new += f"#{target}"
            return f'href="{new}"'
        if url.startswith("../../assets/"):
            relative = copy_asset(url, source_path)
            if attribute == "src":
                return f'src="{prefix}assets/{relative}"'
            return f'href="{prefix}assets/{relative}" download'
        return match.group(0)

    return re.sub(r'(href|src)="([^"]+)"', repl, html)


def prompt_block(match):
    return (
        '<div class="prompt"><div class="prompt-head">'
        '<span class="prompt-label">提示词</span>'
        '<button class="prompt-copy" type="button" aria-label="复制提示词">复制</button>'
        f'</div><pre><code class="language-text">{match.group(1)}</code></pre></div>'
    )


def render_body(source, level, route, prefix, source_path):
    diagram = (
        f'\n\n<figure>'
        f'<img src="{prefix}assets/ai-two-layers.svg" alt="上层是用来交代任务的电脑界面，下层是处理输入并生成回答的模型。" width="840" height="330">'
        '<figcaption>上层负责交互，下层生成回答。爸爸这台 Mac 的连接方式如下。</figcaption>'
        '<div class="model-line"><span>上层 · Codex 界面</span><b aria-hidden="true">→</b><span>下层 · DeepSeek 模型</span></div>'
        '</figure>\n\n'
    )
    source = re.sub(r"```mermaid\n.*?```", lambda _: diagram, source, flags=re.S)
    html = markdown_html(source)
    html = resolve_links(html, route, prefix, source_path)
    counter = iter(range(1, 1000))
    if level == 3:
        html = re.sub(
            r"<h3>(.*?)</h3>",
            lambda match: f'<h2 id="step-{next(counter)}">{match.group(1)}</h2>',
            html,
            flags=re.S,
        )
    else:
        html = re.sub(
            r"<h2>(.*?)</h2>",
            lambda match: f'<h2 id="step-{next(counter)}">{match.group(1)}</h2>',
            html,
            flags=re.S,
        )
    html = re.sub(r"(<table>.*?</table>)", r'<div class="table-wrap">\1</div>', html, flags=re.S)
    html = re.sub(
        r"<li>\[ \]\s*(.*?)</li>",
        r'<li class="task"><span class="task-box" aria-hidden="true"></span><span class="task-text">\1</span></li>',
        html,
        flags=re.S,
    )
    html = re.sub(
        r"<li>\[[xX]\]\s*(.*?)</li>",
        r'<li class="task is-done"><span class="task-box" aria-hidden="true"></span><span class="task-text">\1</span></li>',
        html,
        flags=re.S,
    )
    html = re.sub(
        r'<pre><code class="language-text">(.*?)</code></pre>',
        prompt_block,
        html,
        flags=re.S,
    )
    html = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener"',
        html,
    )
    return html


def toc_label(label):
    return re.sub(r"^[0-9]+[.、]\s*", "", label)


def toc_html(headings):
    links = "".join(
        f'<a href="#step-{position}"><span class="toc-num">{position:02}</span><span>{escape(toc_label(label))}</span></a>'
        for position, label in enumerate(headings, 1)
    )
    return links


def search_entries_for(title, route, route_name, number, status, headings, bodies, intro, base_url):
    entries = []
    if intro:
        text = plain(intro)
        if text:
            entries.append({
                "title": title,
                "heading": "本节说明",
                "text": text,
                "url": f"{base_url}#{route}",
                "route": route,
                "routeName": route_name,
                "lesson": number,
                "status": status,
            })
    for position, (heading, body) in enumerate(zip(headings, bodies), 1):
        text = plain(body)
        if not text:
            continue
        entries.append({
            "title": title,
            "heading": heading,
            "text": text,
            "url": f"{base_url}#step-{position}",
            "route": route,
            "routeName": route_name,
            "lesson": number,
            "status": status,
        })
    return entries


def home(rows):
    route_cards = []
    for route in ROUTES:
        meta = ROUTE_META[route]
        route_cards.append(
            f'''<a class="route-card route-{route}" href="{route}/index.html">
<figure class="route-portrait"><img src="assets/{route}.svg" alt="{meta['name']}路线的抽象侧脸线描，用作课程入口" width="300" height="220"></figure>
<div class="route-copy"><p class="eyebrow">学习路线</p><h2>{meta['title']}</h2><p>{meta['blurb']}</p>
<p class="route-meta"><span class="chip">{len(rows[route])} 节</span><span class="chip">{meta['focus']}</span></p>
<span class="route-enter">打开课表 <span aria-hidden="true">→</span></span></div></a>'''
        )
    drafts = sum(1 for route in ROUTES for item in rows[route] if item["status"] == "draft")
    examples = "".join(
        f'<a class="chip" href="search.html?q={quote(word)}">{escape(word)}</a>'
        for word in ("屏幕共享", "API Key", "LaTeX", "GitHub")
    )
    body = f'''<section class="hero home-hero"><div class="wrap">
<p class="eyebrow">{SITE_TAGLINE}</p>
<h1>爸妈的 <em>Mac 与 AI 课</em></h1>
<p class="lead">按学习路线浏览，或搜索课里的操作和概念。两条路线各自编号，不必同步。</p>
<form class="hero-search" action="search.html" method="get" role="search">
<label class="sr-only" for="home-q">搜索课程</label>
<input id="home-q" name="q" type="search" placeholder="搜索课程，例如：屏幕共享、API Key" autocomplete="off">
<button type="submit">搜索</button>
</form>
<p class="hero-examples">试一试：{examples}</p>
</div></section>
<section class="wrap stats" aria-label="课程概况">
<div class="stat"><span class="stat-value">{len(rows['dad'])}</span><span class="stat-label">爸爸的课</span></div>
<div class="stat"><span class="stat-value">{sum(1 for item in rows['mom'] if item['status'] != 'draft')}</span><span class="stat-label">妈妈的课</span></div>
<div class="stat"><span class="stat-value">{drafts}</span><span class="stat-label">后续草稿</span></div>
<div class="stat"><span class="stat-value">1</span><span class="stat-label">共同练习</span></div>
</section>
<section class="wrap route-grid" aria-label="选择学习路线">{''.join(route_cards)}</section>
<section class="wrap home-section"><div class="section-head"><div class="section-title"><p class="eyebrow">怎么用</p><h2>三步开始</h2></div></div>
<div class="card-grid">
<article class="card"><span class="card-kicker">01</span><h3>选自己的路线</h3><p>爸爸和妈妈各自从自己的课表开始，课次不要求同步。第一次来，先看一节里要做什么。</p></article>
<article class="card"><span class="card-kicker">02</span><h3>按步骤动手</h3><p>每节先写清输入、步骤和预期结果。需要提示词时，照提示词块里的文字发给 AI，再自己操作。</p></article>
<article class="card"><span class="card-kicker">03</span><h3>亲手核对</h3><p>AI 说得通顺不等于事情做对。打开原文件、原网页或 PDF，对照检查后再进入下一步。</p></article>
</div></section>'''
    write_page("index.html", SITE_FULL, "爸妈的 Mac 与 AI 课：两条独立的家庭学习路线，可按关键词搜索课里的操作和概念。",
               body, "home", page_type="home")


def route_lesson_row(item, draft=False):
    tags = []
    mode = clean_mode(item["mode"])
    if mode and mode != "—":
        tags.append(mode)
    if item["status"] == "draft":
        tags.append("草稿")
    tag_html = "".join(f'<span class="chip">{escape(tag)}</span>' for tag in tags)
    return (
        f'<a class="lesson-row{" is-draft" if draft else ""}" href="lesson-{item["number"]:02}.html">'
        f'<span class="lesson-num" lang="en-GB">Lesson {item["number"]:02}</span>'
        f'<span class="lesson-main"><span class="lesson-title">{escape(item["title"])}</span>'
        f'<span class="lesson-tags">{tag_html}</span></span>'
        '<span class="lesson-arrow" aria-hidden="true">→</span></a>'
    )


def schedule_page(route, rows):
    meta = ROUTE_META[route]
    active = [item for item in rows if item["status"] != "draft"]
    drafts = [item for item in rows if item["status"] == "draft"]
    active_html = "".join(route_lesson_row(item) for item in active)
    draft_html = ""
    if drafts:
        draft_html = f'''<section class="wrap lesson-section lesson-section-drafts">
<div class="section-head"><div class="section-title"><p class="eyebrow">后续课程</p><h2>草稿</h2></div><span class="section-note">{len(drafts)} 节</span></div>
<p class="section-intro">这些课还没有正式上过，课前会再核对工具和步骤。</p>
<div class="lesson-list">{''.join(route_lesson_row(item, draft=True) for item in drafts)}</div>
</section>'''
    from collections import Counter
    mode_counts = Counter(
        clean_mode(item["mode"]) for item in rows
        if clean_mode(item["mode"]) not in ("", "—")
    )
    mode_chips = "".join(
        f'<span class="chip">{escape(mode)} {count} 节</span>'
        for mode, count in mode_counts.items()
    )
    draft_chip = f'<span class="chip">{len(drafts)} 节草稿</span>' if drafts else ""
    body = f'''<section class="hero hero-route route-{route}"><div class="wrap">
<p class="eyebrow">学习路线 · {escape(meta['focus'])}</p>
<h1>{meta['title']}</h1>
<p class="lead">{meta['blurb']}</p>
<p class="hero-meta"><span class="chip">{len(rows)} 节</span>{mode_chips}{draft_chip}</p>
</div></section>
<section class="wrap lesson-section">
<div class="section-head"><div class="section-title"><p class="eyebrow">正在进行</p><h2>课程进度</h2></div><span class="section-note">{len(active)} 节</span></div>
<div class="lesson-list">{active_html}</div>
</section>{draft_html}
<section class="wrap lesson-section">
<a class="practice-card" href="../practice/{PRACTICE['slug']}.html">
<p class="eyebrow">共同练习 · 后续课 · 草稿</p>
<h2>{PRACTICE['title']}</h2>
<p>{PRACTICE['blurb']}</p>
<span class="route-enter">打开共同练习 <span aria-hidden="true">→</span></span>
</a>
</section>'''
    write_page(f"{route}/index.html", meta["title"], meta["blurb"], body, route,
               page_type="schedule")


def lesson_pager(route, item, rows, meta):
    position = rows.index(item)
    previous = rows[position - 1] if position > 0 else None
    following = rows[position + 1] if position + 1 < len(rows) else None

    def pager_link(target, direction):
        if target is None:
            return '<span class="pager-link is-empty" aria-hidden="true"></span>'
        label = "上一节" if direction == "previous" else "下一节"
        suffix = ' <span class="pager-status">草稿</span>' if target["status"] == "draft" else ""
        return (
            f'<a class="pager-link" href="lesson-{target["number"]:02}.html">'
            f'<span class="pager-label">{label}</span>'
            f'<span class="pager-title">第 {target["number"]} 节{suffix}</span></a>'
        )

    return f'''<nav class="lesson-pager" aria-label="课次导航">
{pager_link(previous, "previous")}
<a class="pager-link pager-home" href="index.html"><span class="pager-label">课表</span><span class="pager-title">返回{meta['title']}</span></a>
{pager_link(following, "next")}
</nav>'''


def lesson_page(route, item, rows):
    meta = ROUTE_META[route]
    path = ROOT / "course/lessons" / item["file"]
    source = path.read_text(encoding="utf-8")
    heading, body_source = route_content(source, meta["name"])
    intro, sections = split_sections(body_source, 3)
    headings = [section_heading for section_heading, _ in sections]
    bodies = [section_body for _, section_body in sections]
    content = render_body(body_source, 3, route, "../", path)
    summary = ""
    if item["title"] != heading:
        summary = f'<p class="lesson-summary">{escape(item["title"])}</p>'
    mode = clean_mode(item["mode"])
    status = status_label(item["status"])
    status_chip = f'<span class="chip chip-status">{status}</span>' if status else ""
    body = f'''<article class="lesson-page route-{route}"><div class="wrap">
<nav class="breadcrumb" aria-label="面包屑"><a href="index.html">{meta['title']}</a><span aria-hidden="true">/</span><span>第 {item['number']} 节</span></nav>
<header class="lesson-hero">
<p class="eyebrow"><span lang="en-GB">Lesson {item['number']:02}</span> · {meta['name']} · {escape(mode)} {status_chip}</p>
<h1>{escape(heading)}</h1>{summary}
</header>
<div class="lesson-layout">
<aside class="toc" aria-label="本节步骤"><p class="toc-title">本节步骤</p><nav class="toc-nav">{toc_html(headings)}</nav></aside>
<div class="lesson-body" id="{route}">{content}</div>
</div>
{lesson_pager(route, item, rows, meta)}
</div></article>'''
    write_page(f"{route}/lesson-{item['number']:02}.html", heading,
               excerpt(plain(intro) or item["title"]), body, route,
               route=route, page_type="lesson")
    title = f"{meta['name']} · 第 {item['number']} 节"
    return search_entries_for(
        title, route, meta["name"], item["number"], item["status"],
        headings, bodies, intro, f"{route}/lesson-{item['number']:02}.html",
    )


def practice_page():
    path = ROOT / "course/lessons" / PRACTICE["file"]
    source = path.read_text(encoding="utf-8")
    heading_match = re.search(r"(?m)^# (.+)$", source)
    if not heading_match:
        raise SystemExit(f"{path} 缺少一级标题")
    heading = heading_match.group(1).split("｜")[-1].strip()
    body_source = re.sub(r"(?m)^# .+\n", "", source, count=1)
    body_source = re.sub(r"(?m)^状态：.*\n?", "", body_source).strip()
    intro, sections = split_sections(body_source, 2)
    headings = [section_heading for section_heading, _ in sections]
    bodies = [section_body for _, section_body in sections]
    content = render_body(body_source, 2, "practice", "../", path)
    body = f'''<article class="lesson-page page-practice"><div class="wrap">
<nav class="breadcrumb" aria-label="面包屑"><a href="../index.html">首页</a><span aria-hidden="true">/</span><span>共同练习</span></nav>
<header class="lesson-hero">
<p class="eyebrow">共同练习 · 后续课 · <span class="chip chip-status">草稿</span></p>
<h1>{escape(heading)}</h1>
<p class="lesson-summary">{PRACTICE['blurb']}</p>
</header>
<div class="lesson-layout">
<aside class="toc" aria-label="本节步骤"><p class="toc-title">本节步骤</p><nav class="toc-nav">{toc_html(headings)}</nav></aside>
<div class="lesson-body" id="practice">{content}</div>
</div>
<nav class="lesson-pager" aria-label="课次导航">
<a class="pager-link pager-home" href="../dad/index.html"><span class="pager-label">爸爸</span><span class="pager-title">返回爸爸的课表</span></a>
<a class="pager-link pager-home" href="../mom/index.html"><span class="pager-label">妈妈</span><span class="pager-title">返回妈妈的课表</span></a>
</nav>
</div></article>'''
    write_page(f"practice/{PRACTICE['slug']}.html", heading,
               PRACTICE["blurb"], body, "practice", page_type="practice")
    title = "共同练习"
    return search_entries_for(
        title, "practice", "共同练习", None, "draft",
        headings, bodies, intro, f"practice/{PRACTICE['slug']}.html",
    )


def search_page(rows):
    counts = {
        "all": None,
        "dad": len(rows["dad"]),
        "mom": len(rows["mom"]),
        "practice": 1,
    }
    def filter_button(key, label, count):
        count_html = f'<span class="chip-count">{count}</span>' if count is not None else ""
        active = " is-active" if key == "all" else ""
        return (
            f'<button type="button" class="chip{active}" data-route="{key}">'
            f'{label}{count_html}</button>'
        )

    filters = "".join(
        filter_button(key, label, count)
        for key, label, count in (
            ("all", "全部", None),
            ("dad", "爸爸", counts["dad"]),
            ("mom", "妈妈", counts["mom"]),
            ("practice", "共同练习", counts["practice"]),
        )
    )
    body = f'''<section class="hero hero-search-page"><div class="wrap">
<p class="eyebrow">全站搜索</p>
<h1>搜索课程</h1>
<p class="lead">输入一个操作名、工具名或概念。结果会标出路线、课次和具体步骤，点开就能回到原文。</p>
<form class="search-form" id="search-form" action="search.html" method="get" role="search">
<label class="sr-only" for="course-query">关键词</label>
<input id="course-query" name="q" type="search" placeholder="例如：屏幕共享、API Key、LaTeX、GitHub" autocomplete="off">
<button type="submit">搜索</button>
</form>
<div class="search-filters" role="group" aria-label="按路线筛选">{filters}</div>
<p class="search-hints">常用：<button type="button" class="link-chip" data-query="屏幕共享">屏幕共享</button><button type="button" class="link-chip" data-query="API Key">API Key</button><button type="button" class="link-chip" data-query="LaTeX">LaTeX</button><button type="button" class="link-chip" data-query="GitHub">GitHub</button></p>
<p id="search-status" class="search-status" role="status" aria-live="polite"></p>
<ol id="search-results" class="search-results"></ol>
<div id="search-empty" class="empty-state" hidden><strong>没有找到相关内容</strong><p>试试更短的关键词，或换一个说法。</p></div>
<noscript><p class="notice">搜索需要启用 JavaScript。也可以直接打开<a href="dad/index.html">爸爸的课程</a>或<a href="mom/index.html">妈妈的课程</a>。</p></noscript>
</div></section>'''
    write_page("search.html", "搜索课程", "搜索爸妈课程里的操作、工具和概念。",
               body, "search", page_type="search",
               scripts=("search-index.js", "search.js"))


def clean_docs():
    for route in ROUTES:
        directory = DOCS / route
        directory.mkdir(parents=True, exist_ok=True)
        for page in directory.glob("lesson-*.html"):
            page.unlink()
    practice = DOCS / "practice"
    practice.mkdir(parents=True, exist_ok=True)
    for page in practice.glob("*.html"):
        page.unlink()
    assets = DOCS / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    if (assets / "lessons").exists():
        rmtree(assets / "lessons")
    if (assets / "fonts").exists():
        rmtree(assets / "fonts")


def copy_static():
    for name in ("style.css", "ui.js", "search.js"):
        copyfile(ROOT / "site" / name, DOCS / "assets" / name)
    copyfile(ROOT / "assets/site/favicon.svg", DOCS / "assets/favicon.svg")
    for route in ROUTES:
        copyfile(ROOT / f"assets/site/{route}.svg", DOCS / f"assets/{route}.svg")
    diagram = ROOT / "assets/lessons/01/illustrations/ai-two-layers.svg"
    if diagram.is_file():
        copyfile(diagram, DOCS / "assets/ai-two-layers.svg")
    fonts = ROOT / "site/fonts"
    if fonts.is_dir():
        destination = DOCS / "assets/fonts"
        destination.mkdir(parents=True, exist_ok=True)
        for font in fonts.glob("*.woff2"):
            copyfile(font, destination / font.name)


def main():
    if not (ROOT / "README.md").is_file():
        raise SystemExit("找不到 README.md")
    rows = parse_schedule()
    clean_docs()
    copy_static()
    home(rows)
    entries = []
    for route in ROUTES:
        schedule_page(route, rows[route])
        for item in rows[route]:
            entries.extend(lesson_page(route, item, rows[route]))
    entries.extend(practice_page())
    search_page(rows)
    (DOCS / "assets/search-index.js").write_text(
        "window.courseSearchIndex = " + json.dumps(entries, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(entries)} search entries, "
          f"{sum(len(items) for items in rows.values())} lesson pages, 1 practice page.")


if __name__ == "__main__":
    main()
