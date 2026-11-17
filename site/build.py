"""Build the family course site from topic Markdown."""
from html import escape, unescape
import hashlib
import json
from pathlib import Path
from shutil import copyfile, rmtree
import re
from urllib.parse import quote

from markdown import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TOPICS_DIR = ROOT / "course/topics"
GALLERY_DIR = ROOT / "course/gallery"
SITE_NAME = "爸妈的 AI 课"
SITE_FULL = "爸妈的 Mac 与 AI 课"
SITE_TAGLINE = "家庭课程 · 持续更新"
SITE_URL = "https://haoli-ku.github.io/Hao-Parents-AI-Lecture/"
ROUTES = ("dad", "mom")

ROUTE_META = {
    "dad": {
        "name": "爸爸",
        "title": "爸爸的学习路径",
        "blurb": "从 DeepSeek 账户和 Harness 开始，做中文 LaTeX 技术文档，再把工艺流程图整理成可核对、可精确修改的 DXF 工作流。",
        "focus": "AI · LaTeX · AutoCAD",
    },
    "mom": {
        "name": "妈妈",
        "title": "妈妈的学习路径",
        "blurb": "先把新 Mac、会议、邮件和家庭共享用顺，再和爸爸一起完成 AI 与 Harness 入门。",
        "focus": "Mac · 家庭协作 · AI 入门",
    },
}
AUDIENCE_META = {
    "dad": ("爸爸", "route-dad"),
    "mom": ("妈妈", "route-mom"),
    "both": ("共同", "route-both"),
}
NAV_ITEMS = (
    ("home", "首页", "index.html"),
    ("topics", "专题", "topics/index.html"),
    ("dad", "爸爸", "dad/index.html"),
    ("mom", "妈妈", "mom/index.html"),
    ("gallery", "拾趣", "gallery/index.html"),
)
LEGACY_REDIRECTS = {
    "dad/lesson-01.html": "topics/ai/01-models-and-tools.html",
    "dad/lesson-02.html": "topics/ai/02-harness-setup.html",
    "dad/lesson-03.html": "topics/ai/03-effort-and-usage.html",
    "dad/lesson-04.html": "topics/word-to-latex/01-project-goal.html",
    "dad/lesson-05.html": "topics/word-to-latex/02-compile-and-annotate.html",
    "dad/lesson-06.html": "topics/word-to-latex/03-template.html",
    "dad/lesson-07.html": "topics/word-to-latex/04-project-layout.html",
    "dad/lesson-08.html": "topics/word-to-latex/05-project-rules.html",
    "dad/lesson-09.html": "topics/word-to-latex/06-convert-segment.html",
    "dad/lesson-10.html": "topics/cad/01-convert-to-dxf.html",
    "dad/lesson-11.html": "topics/cad/03-batch-and-cross-check.html",
    "dad/lesson-12.html": "topics/cad/04-review-and-annotate.html",
    "mom/lesson-01.html": "topics/mac/01-new-mac.html",
    "mom/lesson-02.html": "topics/mac/02-apps-and-email.html",
    "mom/lesson-03.html": "topics/mac/03-shortcuts-and-sharing.html",
    "mom/lesson-04.html": "topics/mac/04-meetings-and-mactex.html",
    "mom/lesson-05.html": "topics/ai/01-models-and-tools.html",
    "mom/lesson-06.html": "topics/ai/02-harness-setup.html",
    "mom/lesson-07.html": "topics/ai/03-effort-and-usage.html",
    "practice/index.html": "topics/index.html",
    "practice/github.html": "topics/version-control/01-first-repository.html",
    "practice/image-gen.html": "topics/image-generation/01-generate-and-edit.html",
}


def compute_asset_version():
    digest = hashlib.sha1()
    sources = [ROOT / "site" / name for name in ("style.css", "ui.js", "search.js")]
    sources.append(ROOT / "README.md")
    sources.extend(sorted((ROOT / "course").rglob("*.md")))
    for path in sources:
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


ASSET_VERSION = compute_asset_version()


def rel_prefix(path):
    return "../" * (len(path.relative_to(DOCS).parts) - 1)


def brand(prefix):
    return (
        f'<a class="brand" href="{prefix}index.html">'
        '<span class="brand-mark" aria-hidden="true">AI</span>'
        f'<span class="brand-text"><span class="brand-name">{SITE_NAME}</span>'
        '<span class="brand-role">家庭课程</span></span></a>'
    )


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"(?s)^---\s*\n(.*?)\n---\s*\n?(.*)$", text)
    if not match:
        raise SystemExit(f"{path} 缺少 frontmatter")
    metadata = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise SystemExit(f"{path} 的 frontmatter 行无法解析：{line}")
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, match.group(2).strip()


def status_key(value):
    value = (value or "").strip()
    if value in ("active", "followup", "draft"):
        return value
    return "active"


def load_topics():
    topics = []
    if not TOPICS_DIR.is_dir():
        raise SystemExit("找不到 course/topics/")
    for directory in sorted(TOPICS_DIR.iterdir()):
        if not directory.is_dir():
            continue
        topic_file = directory / "topic.md"
        if not topic_file.is_file():
            raise SystemExit(f"专题目录缺少 topic.md：{directory}")
        meta, intro = parse_frontmatter(topic_file)
        for field in ("title", "subtitle", "summary", "order"):
            if not meta.get(field):
                raise SystemExit(f"{topic_file} 缺少 {field}")
        sessions = []
        for path in sorted(directory.glob("*.md")):
            if path.name == "topic.md":
                continue
            number_match = re.match(r"(\d{2})-(.+)\.md$", path.name)
            if not number_match:
                raise SystemExit(f"讲次文件名要以 NN-slug.md 命名：{path}")
            session_meta, body = parse_frontmatter(path)
            audience = session_meta.get("audience", "")
            if audience not in AUDIENCE_META:
                raise SystemExit(f"{path} 的 audience 必须是 dad/mom/both")
            for field in ("title", "summary"):
                if not session_meta.get(field):
                    raise SystemExit(f"{path} 缺少 {field}")
            sessions.append({
                "topic": meta["title"],
                "topic_slug": directory.name,
                "slug": path.stem,
                "file": path,
                "number": int(number_match.group(1)),
                "title": session_meta["title"],
                "audience": audience,
                "status": status_key(session_meta.get("status")),
                "summary": session_meta["summary"],
                "body": body,
            })
        if not sessions:
            raise SystemExit(f"{directory} 里没有讲次文件")
        numbers = [item["number"] for item in sessions]
        if len(numbers) != len(set(numbers)):
            raise SystemExit(f"{directory} 讲次编号重复：{numbers}")
        sessions.sort(key=lambda item: item["number"])
        topic = {
            "slug": directory.name,
            "title": meta["title"],
            "subtitle": meta["subtitle"],
            "summary": meta["summary"],
            "order": int(meta["order"]),
            "optional": meta.get("optional", "false").lower() == "true",
            "intro": intro,
            "sessions": sessions,
            "audiences": sorted({item["audience"] for item in sessions}),
        }
        topics.append(topic)
    orders = [topic["order"] for topic in topics]
    if len(orders) != len(set(orders)):
        raise SystemExit(f"专题 order 重复：{orders}")
    topics.sort(key=lambda topic: topic["order"])
    return topics


def topic_audience_label(topic):
    audiences = set(topic["audiences"])
    if audiences == {"both"}:
        return "共同"
    if audiences == {"dad", "mom"} or audiences == {"mom", "dad"}:
        return "爸爸 · 妈妈"
    return AUDIENCE_META[topic["audiences"][0]][0]


def session_path(session):
    return f"topics/{session['topic_slug']}/{session['slug']}.html"


def topic_path(topic):
    return f"topics/{topic['slug']}/index.html"


def session_audience_name(session):
    return AUDIENCE_META[session["audience"]][0]


def audience_matches(session, route):
    return session["audience"] == "both" or session["audience"] == route


def sessions_for(topics, route):
    return [
        (topic, [item for item in topic["sessions"] if audience_matches(item, route)])
        for topic in topics
        if any(audience_matches(item, route) for item in topic["sessions"])
    ]


def write_page(path, title, description, body, active, route=None,
               page_type="page", scripts=()):
    path = DOCS / path
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = rel_prefix(path)
    relative = path.relative_to(DOCS)
    parent = relative.parent.as_posix()
    page_dir = "" if parent == "." else parent + "/"
    page_url = SITE_URL + relative.as_posix()
    nav = []
    for key, label, href in NAV_ITEMS:
        attributes = f' href="{prefix}{href}"'
        if active == key:
            attributes += ' class="is-active"'
            attributes += ' aria-current="page"' if page_type in ("home", "topics", "path", "gallery") else ' aria-current="true"'
        nav.append(f"<a{attributes}>{label}</a>")
    footer_nav = "".join(
        f'<a href="{prefix}{href}">{label}</a>'
        for _, label, href in NAV_ITEMS + (("search", "搜索", "search.html"),)
    )
    footer_nav += f'<a href="{page_url}" target="_blank" rel="noopener">在浏览器打开</a>'
    embed = f'''<script data-embed-nav>
(function () {{
  var site = "{SITE_URL}";
  var dir = "{page_dir}";
  var embedded = false;
  try {{ embedded = window.top !== window.self; }} catch (error) {{ embedded = true; }}
  if (!embedded) return;
  var base = document.createElement("base");
  base.href = site + dir;
  document.head.appendChild(base);
  document.addEventListener("click", function (event) {{
    if (event.button !== 0 || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var link = event.target && event.target.closest ? event.target.closest("a[href]") : null;
    if (!link || link.hasAttribute("download")) return;
    if (link.target && link.target !== "_self") return;
    var href = link.getAttribute("href");
    if (!href || href.charAt(0) === "#" || /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(href)) return;
    event.preventDefault();
    window.location.assign(new URL(href, site + dir).href);
  }}, true);
}})();
</script>'''
    body_class = f"page-{page_type}"
    if route:
        body_class += f" route-{route}"
    document_title = title if title == SITE_FULL else f"{title} · {SITE_FULL}"
    script_tags = "".join(
        f'<script defer src="{prefix}assets/{name}?v={ASSET_VERSION}"></script>' for name in ("ui.js",) + tuple(scripts)
    )
    path.write_text(
        f'''<!doctype html>
<html lang="zh-CN" data-page-dir="{page_dir}" data-page-path="{relative.as_posix()}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(document_title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="theme-color" content="#f7f6f2">
{embed}
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/style.css?v={ASSET_VERSION}">
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




def markdown_html(text):
    return markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


def plain(text):
    html = markdown_html(text)
    html = re.sub(r"<[^>]+>", " ", html)
    return " ".join(unescape(html).split())


def excerpt(text, limit=140):
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


def status_label(status):
    return {"draft": "草稿", "followup": "后续课"}.get(status, "")




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
        '<figcaption>上层负责交互，下层生成回答。这台 Mac 的连接方式如下。</figcaption>'
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




def display_gallery_date(value):
    match = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", value.strip())
    if match:
        return f"{match.group(1)} 年 {int(match.group(2))} 月"
    return value.strip()


def parse_gallery():
    items = []
    if not GALLERY_DIR.is_dir():
        return items
    required = ("title", "date", "summary", "image", "alt", "credit")
    for path in sorted(GALLERY_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.match(r"(?s)^---\s*\n(.*?)\n---\s*\n?(.*)$", text)
        if not match:
            raise SystemExit(f"{path} 缺少 gallery frontmatter")
        metadata = {}
        for line in match.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, separator, value = line.partition(":")
            if not separator:
                raise SystemExit(f"{path} 的 frontmatter 行无法解析：{line}")
            metadata[key.strip()] = value.strip().strip('"').strip("'")
        missing = [key for key in required if not metadata.get(key)]
        if missing:
            raise SystemExit(f"{path} 缺少 frontmatter 字段：{', '.join(missing)}")
        item = dict(metadata)
        item["slug"] = path.stem
        item["source_path"] = path
        item["body"] = match.group(2).strip()
        item["date_label"] = display_gallery_date(item["date"])
        items.append(item)
    items.sort(key=lambda item: item["date"], reverse=True)
    return items


def gallery_credit(item):
    relation = item.get("relation", "").strip()
    credit = item.get("credit", "").strip()
    return f"{relation}{credit}" if relation else credit


def gallery_credit_line(item):
    credit = gallery_credit(item)
    extra = [value for value in (item.get("credit_en", ""), item.get("affiliation", "")) if value]
    if extra:
        return f"{credit}（{'，'.join(extra)}）"
    return credit


def gallery_name_line(item):
    credit = item.get("credit", "").strip()
    extra = [value for value in (item.get("credit_en", ""), item.get("affiliation", "")) if value]
    if extra:
        return f"{credit}（{'，'.join(extra)}）"
    return credit


def gallery_index(items):
    cards = []
    for item in items:
        image = "../" + item["image"]
        cards.append(f'''<a class="gallery-card" href="{item['slug']}.html">
<figure class="gallery-card-art"><img src="{escape(image)}" alt="{escape(item['alt'])}" loading="lazy"></figure>
<div class="gallery-card-copy">
<p class="eyebrow">拾趣 · {escape(item['date_label'])}</p>
<h2>{escape(item['title'])}</h2>
<p>{escape(item['summary'])}</p>
<p class="gallery-credit">原画 · {escape(gallery_credit(item))}手绘 · 线稿 · {escape(item.get('image_credit', 'ChatGPT 生成'))}</p>
<span class="route-enter">看这幅画 <span aria-hidden="true">→</span></span>
</div>
</a>''')
    empty = ""
    if not cards:
        empty = '<p class="empty-state">这里还没有展品。等下一件好玩的东西。</p>'
    body = f'''<section class="hero hero-route"><div class="wrap">
<p class="eyebrow">拾趣</p>
<h1>拾趣</h1>
<p class="lead">课程之外的小作品、画和家里好玩的东西。第一件是赵诗雅博士在我办公室白板上留下的一幅画。</p>
</div></section>
<section class="wrap lesson-section">
<div class="gallery-grid{' is-single' if len(items) == 1 else ''}">{''.join(cards)}</div>
{empty}
</section>'''
    write_page("gallery/index.html", "拾趣",
               "课程之外的小作品、画和家里好玩的东西。",
               body, "gallery", page_type="gallery")


def gallery_pager(items, item):
    position = items.index(item)
    previous = items[position - 1] if position > 0 else None
    following = items[position + 1] if position + 1 < len(items) else None

    def pager_link(target, label):
        if target is None:
            return '<span class="pager-link is-empty" aria-hidden="true"></span>'
        return (
            f'<a class="pager-link" href="{target["slug"]}.html">'
            f'<span class="pager-label">{label}</span>'
            f'<span class="pager-title">{escape(target["title"])}</span></a>'
        )

    return f'''<nav class="lesson-pager" aria-label="展品导航">
{pager_link(previous, "上一件")}
<a class="pager-link pager-home" href="index.html"><span class="pager-label">拾趣</span><span class="pager-title">返回拾趣</span></a>
{pager_link(following, "下一件")}
</nav>'''


def gallery_page(item, items):
    credit = gallery_credit_line(item)
    image_credit = item.get("image_credit", "ChatGPT 生成")
    email = item.get("email", "").strip()
    email_html = f'<a href="mailto:{escape(email)}">{escape(email)}</a>' if email else ""
    details = [value for value in (item.get("credit_en", ""), item.get("affiliation", "")) if value]
    ack_detail = f"（{'，'.join(details)}）" if details else ""
    image = "../" + item["image"]
    original_image = "../" + item["original_image"] if item.get("original_image") else ""
    original_alt = item.get("original_alt", "原始白板照片")
    peek_image = "../" + item.get("peek_image", item.get("original_image", "")) if item.get("peek_image") or item.get("original_image") else ""
    vector_caption = f"整理版线稿 · {image_credit}"
    original_caption = f"原始白板照片 · {item['credit']}手绘"
    meta_rows = []
    for label, value in (
        ("原画", f"{gallery_credit(item)}手绘"),
        ("整理版", image_credit),
        ("时间", item["date_label"]),
        ("地点", item.get("location", "")),
        ("媒介", item.get("medium", "")),
        ("联系", email_html),
    ):
        if value:
            meta_rows.append(f"<div><dt>{label}</dt><dd>{value}</dd></div>")

    if original_image:
        art = f'''<figure class="gallery-art is-original">
<span class="gallery-peek gallery-peek-vector" aria-hidden="true"><img src="{escape(image)}" alt=""></span>
<span class="gallery-peek gallery-peek-original" aria-hidden="true"><img src="{escape(peek_image)}" alt="" loading="lazy" decoding="async"></span>
<button class="gallery-switch is-original" type="button" aria-pressed="true" aria-label="切换原图和整理版线稿"
        data-gallery-switch
        data-vector-caption="{escape(vector_caption)}"
        data-original-caption="{escape(original_caption)}">
<span class="gallery-stack">
<img class="gallery-layer gallery-layer-vector" src="{escape(image)}" alt="{escape(item['alt'])}">
<img class="gallery-layer gallery-layer-original" src="{escape(original_image)}" alt="{escape(original_alt)}" loading="lazy" decoding="async">
</span>
<span class="gallery-caption"><span data-gallery-caption aria-live="polite">{escape(original_caption)}</span><span class="gallery-hint">点击切换</span></span>
</button>
</figure>'''
    else:
        art = f'''<figure class="gallery-art">
<img src="{escape(image)}" alt="{escape(item['alt'])}">
<figcaption>{escape(vector_caption)}</figcaption>
</figure>'''

    body_html = markdown_html(item["body"]) if item.get("body") else ""
    copy_html = f'<div class="gallery-copy">{body_html}</div>' if body_html else ""
    body = f'''<article class="gallery-page" id="gallery"><div class="wrap">
<nav class="breadcrumb" aria-label="面包屑"><a href="../index.html">首页</a><span aria-hidden="true">/</span><a href="index.html">拾趣</a><span aria-hidden="true">/</span><span>{escape(item['title'])}</span></nav>
<header class="gallery-hero">
<p class="eyebrow">拾趣 · {escape(item['date_label'])}</p>
<h1>{escape(item['title'])}</h1>
<p class="lead">{escape(item['summary'])}</p>
</header>
<div class="gallery-layout">
{art}
<div class="gallery-side">
<div class="acknowledgement">
<p class="eyebrow">致谢</p>
<p>这幅白板画由<strong>{escape(gallery_credit(item))}</strong>{escape(ack_detail)}手绘。{escape(item['date_label'])}，她来丹麦南丹麦大学（SDU）看我，在我办公室的白板上留下这幅画。</p>
<p>页面上的整理版线稿由 ChatGPT 从原图清理生成。</p>
</div>
<dl class="gallery-meta">{''.join(meta_rows)}</dl>
{copy_html}
</div>
</div>
{gallery_pager(items, item)}
</div></article>'''
    write_page(f"gallery/{item['slug']}.html", item['title'], item['summary'], body,
               "gallery", page_type="gallery")
    return {
        "title": item['title'],
        "heading": "拾趣",
        "text": " ".join(value for value in (
            plain(item['body']), gallery_credit_line(item), item.get('image_credit', ''),
            item.get('affiliation', ''), item.get('email', ''), item.get('location', ''),
            item.get('medium', ''),
        ) if value),
        "url": f"gallery/{item['slug']}.html#gallery",
        "route": "gallery",
        "routeName": "拾趣",
        "lesson": None,
        "status": "active",
    }




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
        if "/assets/topics/" in url or "/assets/lessons/" in url:
            relative = copy_asset(url, source_path)
            if attribute == "src":
                return f'src="{prefix}assets/{relative}"'
            suffix = "" if relative.lower().endswith((".html", ".htm")) else " download"
            return f'href="{prefix}assets/{relative}"{suffix}'
        if "://" in url or url.startswith("mailto:"):
            return match.group(0)
        if ".md" in url and attribute == "href":
            path_part, _, fragment = url.partition("#")
            target = (source_path.parent / path_part).resolve()
            try:
                relative = target.relative_to(ROOT / "course")
            except ValueError:
                raise SystemExit(f"课稿里的 Markdown 链接跳出 course/：{url}")
            parts = relative.parts
            if parts[0] == "topics" and len(parts) >= 3:
                new = f"topics/{parts[1]}/{Path(parts[-1]).stem}.html"
            elif parts[0] == "gallery":
                new = f"gallery/{Path(parts[-1]).stem}.html"
            else:
                raise SystemExit(f"无法解析的 Markdown 链接：{url}")
            if fragment:
                new += f"#{fragment}"
            return f'href="{prefix}{new}"'
        return match.group(0)

    return re.sub(r'(href|src)="([^"]+)"', repl, html)


def session_label(session):
    return f"第 {session['number']} 讲"


def status_chip(session):
    labels = {"followup": "后续课", "draft": "草稿"}
    label = labels.get(session["status"], "")
    return f'<span class="chip chip-status">{label}</span>' if label else ""


def audience_chip(session):
    return f'<span class="chip audience-chip audience-{session["audience"]}">{session_audience_name(session)}</span>'


def topic_card(topic, prefix="", href=None):
    optional = '<span class="chip chip-optional">按需</span>' if topic["optional"] else ""
    target = href or f"{prefix}{topic_path(topic)}"
    return f'''<a class="topic-card" href="{target}">
<span class="topic-index" aria-hidden="true">{topic['order']:02d}</span>
<p class="eyebrow">专题 · {len(topic['sessions'])} 讲 · {topic_audience_label(topic)}</p>
<h2>{escape(topic['title'])}</h2>
<p class="topic-subtitle">{escape(topic['subtitle'])}</p>
<p class="topic-summary">{escape(topic['summary'])}</p>
<p class="topic-tags">{optional}</p>
<span class="route-enter">打开专题 <span aria-hidden="true">→</span></span>
</a>'''


def session_row(session, prefix, local=False):
    target = f"{session['slug']}.html" if local else f"{prefix}{session_path(session)}"
    return (
        f'<a class="lesson-row" href="{target}">'
        f'<span class="lesson-num">{session_label(session)}</span>'
        f'<span class="lesson-main"><span class="lesson-title">{escape(session["title"])}</span>'
        f'<span class="lesson-tags">{audience_chip(session)}{status_chip(session)}</span></span>'
        f'<span class="lesson-arrow" aria-hidden="true">→</span></a>'
    )


def topic_index(topics):
    cards = "".join(topic_card(topic, href=f"{topic['slug']}/index.html") for topic in topics)
    body = f'''<section class="hero hero-route"><div class="wrap">
<p class="eyebrow">全部内容 · 按专题浏览</p>
<h1>专题</h1>
<p class="lead">每个专题是一组按顺序排好的讲次。可以按自己的路径学，也可以从任意一个专题开始；标「按需」的专题不必按顺序。</p>
<p class="hero-meta"><span class="chip">{len(topics)} 个专题</span><span class="chip">{sum(len(t['sessions']) for t in topics)} 讲</span></p>
</div></section>
<section class="wrap lesson-section"><div class="topic-grid">{cards}</div></section>
<section class="wrap lesson-section"><div class="section-head"><div class="section-title"><p class="eyebrow">学习路径</p><h2>按人看</h2></div></div>
<div class="path-grid">
<a class="path-card route-dad" href="../dad/index.html"><p class="eyebrow">爸爸</p><h2>爸爸的学习路径</h2><p>AI 入门 → 中文 LaTeX 文档 → AutoCAD 图纸代码流。</p><span class="route-enter">打开路径 →</span></a>
<a class="path-card route-mom" href="../mom/index.html"><p class="eyebrow">妈妈</p><h2>妈妈的学习路径</h2><p>Mac 基础与家庭协作 → 和爸爸一起完成 AI 入门。</p><span class="route-enter">打开路径 →</span></a>
</div></section>'''
    write_page("topics/index.html", "专题", "按专题浏览课程：Mac、AI、LaTeX、AutoCAD、生图与版本管理。",
               body, "topics", page_type="topics")


def topic_page(topic):
    rows = "".join(session_row(item, "", local=True) for item in topic["sessions"])
    optional = '<span class="chip chip-optional">按需专题</span>' if topic["optional"] else ""
    intro = render_body(topic["intro"], 2, "topics", "../../", TOPICS_DIR / topic["slug"] / "topic.md") if topic["intro"] else ""
    body = f'''<section class="hero hero-route route-{topic['audiences'][0] if len(topic['audiences']) == 1 else 'both'}"><div class="wrap">
<nav class="breadcrumb" aria-label="面包屑"><a href="../../index.html">首页</a><span aria-hidden="true">/</span><a href="../index.html">专题</a><span aria-hidden="true">/</span><span>{escape(topic['title'])}</span></nav>
<p class="eyebrow">专题 · {len(topic['sessions'])} 讲 · {topic_audience_label(topic)}</p>
<h1>{escape(topic['title'])}</h1>
<p class="lead">{escape(topic['subtitle'])}</p>
<p>{escape(topic['summary'])}</p>
<p class="hero-meta"><span class="chip">{len(topic['sessions'])} 讲</span>{optional}</p>
</div></section>
<section class="wrap lesson-section"><div class="section-head"><div class="section-title"><p class="eyebrow">讲次</p><h2>按顺序</h2></div><span class="section-note">{len(topic['sessions'])} 讲</span></div>
<div class="lesson-list">{rows}</div>
</section>{('<section class="wrap lesson-section lesson-section-drafts"><div class="section-title"><h2>专题说明</h2></div>' + intro + '</section>') if intro else ''}'''
    write_page(f"topics/{topic['slug']}/index.html", topic["title"], topic["summary"],
               body, "topics", page_type="topics")


def path_page(route, topics):
    meta = ROUTE_META[route]
    groups = sessions_for(topics, route)
    active = [item for _, items in groups for item in items if item["status"] != "draft"]
    sections = []
    for topic, items in groups:
        rows = "".join(session_row(item, "../") for item in items)
        optional = '<span class="chip chip-optional">按需</span>' if topic["optional"] else ""
        sections.append(f'''<section class="wrap lesson-section path-section">
<div class="section-head"><div class="section-title"><p class="eyebrow">专题 · {len(items)} 讲</p>
<h2><a href="../{topic_path(topic)}">{escape(topic['title'])}</a></h2><p class="section-intro">{escape(topic['subtitle'])}</p></div><span class="section-note">{optional}</span></div>
<div class="lesson-list">{rows}</div></section>''')
    total = len({item["slug"] for _, items in groups for item in items})
    optional_count = sum(1 for topic, items in groups if topic["optional"] for _ in items)
    optional_chip = f'<span class="chip chip-optional">{optional_count} 讲按需</span>' if optional_count else ""
    body = f'''<section class="hero hero-route route-{route}"><div class="wrap">
<p class="eyebrow">学习路径 · {escape(meta['focus'])}</p>
<h1>{meta['title']}</h1>
<p class="lead">{meta['blurb']}</p>
<p class="hero-meta"><span class="chip">{total} 讲</span><span class="chip">{len(groups)} 个专题</span>{optional_chip}</p>
</div></section>
{''.join(sections)}
<section class="wrap lesson-section"><div class="section-head"><div class="section-title"><p class="eyebrow">全部</p><h2>按专题浏览</h2></div></div>
<a class="overview-card" href="../topics/index.html"><p class="eyebrow">专题</p><h2>{len(topics)} 个专题</h2><p>不按人的路径，直接看所有专题和讲次。</p><span class="route-enter">打开专题总览 →</span></a>
</section>'''
    write_page(f"{route}/index.html", meta["title"], meta["blurb"], body, route, page_type="path")


def session_pager(topic, session):
    items = topic["sessions"]
    position = items.index(session)
    previous = items[position - 1] if position > 0 else None
    following = items[position + 1] if position + 1 < len(items) else None

    def link(target, direction):
        if target is None:
            return '<span class="pager-link is-empty" aria-hidden="true"></span>'
        label = "上一讲" if direction == "previous" else "下一讲"
        return (
            f'<a class="pager-link" href="{target["slug"]}.html">'
            f'<span class="pager-label">{label}</span>'
            f'<span class="pager-title">{session_label(target)} · {escape(target["title"])}</span></a>'
        )

    return f'''<nav class="lesson-pager" aria-label="讲次导航">
{link(previous, "previous")}
<a class="pager-link pager-home" href="index.html"><span class="pager-label">专题</span><span class="pager-title">返回{escape(topic['title'])}</span></a>
{link(following, "next")}
</nav>'''


def session_page(topic, session):
    intro, sections = split_sections(session["body"], 3)
    headings = [heading for heading, _ in sections]
    content = render_body(session["body"], 3, session["audience"], "../../", session["file"])
    toc_block = ""
    layout_class = "lesson-layout no-toc"
    if headings:
        layout_class = "lesson-layout"
        toc_block = f'<aside class="toc" aria-label="本节步骤"><p class="toc-title">本节步骤</p><nav class="toc-nav">{toc_html(headings)}</nav></aside>'
    audience, route_class = AUDIENCE_META[session["audience"]]
    body = f'''<article class="lesson-page {route_class}"><div class="wrap">
<nav class="breadcrumb" aria-label="面包屑"><a href="../../index.html">首页</a><span aria-hidden="true">/</span><a href="../index.html">专题</a><span aria-hidden="true">/</span><a href="index.html">{escape(topic['title'])}</a><span aria-hidden="true">/</span><span>{session_label(session)}</span></nav>
<header class="lesson-hero">
<p class="eyebrow">专题 · {escape(topic['title'])} · {session_label(session)} · {audience}{status_chip(session)}</p>
<h1>{escape(session['title'])}</h1>
<p class="lesson-summary">{escape(session['summary'])}</p>
</header>
<div class="{layout_class}">
{toc_block}
<div class="lesson-body" id="session">{content}</div>
</div>
{session_pager(topic, session)}
</div></article>'''
    write_page(f"topics/{topic['slug']}/{session['slug']}.html", session["title"],
               session["summary"], body, "topics", route=session["audience"],
               page_type="session")


def search_entries_for_session(topic, session):
    intro, sections = split_sections(session["body"], 3)
    entries = []
    for index, (heading, text) in enumerate(sections, start=1):
        entries.append({
            "topic": topic["slug"],
            "topicName": topic["title"],
            "audience": session["audience"],
            "audienceName": session_audience_name(session),
            "number": session["number"],
            "title": session["title"],
            "step": heading,
            "text": plain(f"{intro} {text}")[:1200],
            "url": f"topics/{topic['slug']}/{session['slug']}.html#step-{index}",
            "status": session["status"],
        })
    return entries


def home(topics, gallery):
    route_cards = []
    for route in ROUTES:
        meta = ROUTE_META[route]
        count = len({item['slug'] for _, items in sessions_for(topics, route) for item in items})
        route_cards.append(
            f'''<a class="route-card route-{route}" href="{route}/index.html">
<figure class="route-portrait"><img src="assets/{route}.svg" alt="{meta['name']}学习路径的抽象侧脸线描，用作入口" width="300" height="220"></figure>
<div class="route-copy"><p class="eyebrow">学习路径</p><h2>{meta['title']}</h2><p>{meta['blurb']}</p>
<p class="route-meta"><span class="chip">{count} 讲</span><span class="chip">{meta['focus']}</span></p>
<span class="route-enter">打开路径 <span aria-hidden="true">→</span></span></div></a>'''
        )
    gallery_section = ""
    if gallery:
        feature = gallery[0]
        gallery_section = f'''<section class="wrap home-section" aria-label="拾趣">
<div class="section-head"><div class="section-title"><p class="eyebrow">拾趣</p><h2>课程之外的小作品</h2></div><a class="section-link" href="gallery/index.html">全部 <span aria-hidden="true">→</span></a></div>
<a class="gallery-feature" href="gallery/{feature['slug']}.html">
<figure class="gallery-feature-art"><img src="{feature['image']}" alt="{escape(feature['alt'])}" loading="lazy"></figure>
<div class="gallery-feature-copy"><p class="eyebrow">拾趣 · {escape(feature['date_label'])}</p><h3>{escape(feature['title'])}</h3><p>{escape(feature['summary'])}</p><p class="gallery-credit">原画 · {escape(gallery_credit(feature))}手绘 · 线稿 · {escape(feature.get('image_credit', 'ChatGPT 生成'))}</p><span class="route-enter">看这幅画 <span aria-hidden="true">→</span></span></div>
</a>
</section>'''
    examples = "".join(
        f'<a class="chip" href="search.html?q={quote(word)}">{escape(word)}</a>'
        for word in ("Harness", "LaTeX", "DXF", "共享相簿")
    )
    total = sum(len(topic["sessions"]) for topic in topics)
    body = f'''<section class="hero home-hero"><div class="hero-sketch" aria-hidden="true"><img src="assets/whiteboard-lineart.svg" alt=""></div><div class="wrap">
<p class="eyebrow">{SITE_TAGLINE}</p>
<h1>爸妈的 <em>Mac 与 AI 课</em></h1>
<p class="lead">按专题浏览，或从自己的学习路径开始。每个专题里的讲次按顺序排好，标「按需」的可以随时插进来。</p>
<form class="hero-search" action="search.html" method="get" role="search">
<label class="sr-only" for="home-q">搜索课程</label>
<input id="home-q" name="q" type="search" placeholder="搜索课程，例如：Harness、DXF、共享相簿" autocomplete="off">
<button type="submit">搜索</button>
</form>
<p class="hero-examples">试一试：{examples}</p>
</div></section>
<section class="wrap stats" aria-label="课程概况">
<div class="stat"><span class="stat-value">{len(topics)}</span><span class="stat-label">专题</span></div>
<div class="stat"><span class="stat-value">{total}</span><span class="stat-label">讲次</span></div>
<div class="stat"><span class="stat-value">2</span><span class="stat-label">学习路径</span></div>
<div class="stat"><span class="stat-value">{len(gallery)}</span><span class="stat-label">拾趣</span></div>
</section>
<section class="wrap home-section"><div class="section-head"><div class="section-title"><p class="eyebrow">专题</p><h2>按主题学</h2></div><a class="section-link" href="topics/index.html">全部 <span aria-hidden="true">→</span></a></div>
<div class="topic-grid">{''.join(topic_card(topic) for topic in topics)}</div></section>
<section class="wrap route-grid" aria-label="选择学习路径">{''.join(route_cards)}</section>
{gallery_section}
<section class="wrap home-section"><div class="section-head"><div class="section-title"><p class="eyebrow">怎么用</p><h2>三步开始</h2></div></div>
<div class="card-grid">
<article class="card"><span class="card-kicker">01</span><h3>选专题或路径</h3><p>想系统学就按专题顺序；只想补一件事就从路径里挑一讲。两条路径不必同步。</p></article>
<article class="card"><span class="card-kicker">02</span><h3>按步骤动手</h3><p>每讲先写清输入、步骤和预期结果。需要提示词时，照提示词块里的文字发给 AI，再自己操作。</p></article>
<article class="card"><span class="card-kicker">03</span><h3>亲手核对</h3><p>AI 说得通顺不等于事情做对。打开原文件、原网页或 PDF，对照检查后再进入下一步。</p></article>
</div></section>'''
    write_page("index.html", SITE_FULL, "爸妈的 Mac 与 AI 课：按专题或学习路径浏览，可搜索课里的操作和概念。",
               body, "home", page_type="home")


def search_page(topics, gallery):
    total = sum(len(topic["sessions"]) for topic in topics)
    filters = [f'<button type="button" class="chip is-active" data-topic="all">全部</button>']
    for topic in topics:
        filters.append(
            f'<button type="button" class="chip" data-topic="{topic["slug"]}">{escape(topic["title"])}'
            f'<span class="chip-count">{len(topic["sessions"])}</span></button>'
        )
    filters.append(f'<button type="button" class="chip" data-topic="gallery">拾趣<span class="chip-count">{len(gallery)}</span></button>')
    body = f'''<section class="hero hero-search-page"><div class="wrap">
<p class="eyebrow">全站搜索</p>
<h1>搜索课程</h1>
<p class="lead">输入操作名、工具名、概念或展品名。结果会标出专题和讲次，点开回到原文。</p>
<form class="search-form" id="search-form" action="search.html" method="get" role="search">
<label class="sr-only" for="course-query">关键词</label>
<input id="course-query" name="q" type="search" placeholder="例如：Harness、DXF、共享相簿" autocomplete="off">
<button type="submit">搜索</button>
</form>
<div class="search-filters" role="group" aria-label="按专题筛选">{''.join(filters)}</div>
<p class="search-hints">常用：<button type="button" class="link-chip" data-query="Harness">Harness</button><button type="button" class="link-chip" data-query="LaTeX">LaTeX</button><button type="button" class="link-chip" data-query="DXF">DXF</button><button type="button" class="link-chip" data-query="共享相簿">共享相簿</button></p>
<p id="search-status" class="search-status" role="status" aria-live="polite"></p>
<ol id="search-results" class="search-results"></ol>
<div id="search-empty" class="empty-state" hidden><strong>没有找到相关内容</strong><p>试试更短的关键词，或换一个说法。</p></div>
<noscript><p class="notice">搜索需要启用 JavaScript。也可以直接打开<a href="topics/index.html">专题总览</a>。</p></noscript>
</div></section>'''
    write_page("search.html", "搜索课程", "搜索课程、讲次和拾趣里的操作、工具、概念和作品。",
               body, "search", page_type="search", scripts=("search-index.js", "search.js"))


def write_redirect(old_path, new_path):
    import os
    target = DOCS / new_path
    if not target.is_file():
        raise SystemExit(f"重定向目标不存在：{new_path}")
    page = DOCS / old_path
    page.parent.mkdir(parents=True, exist_ok=True)
    relative = os.path.relpath(target, page.parent)
    html = f'''<!doctype html>
<html lang="zh-CN" data-redirect="1">
<head><meta charset="utf-8"><title>页面已迁移</title>
<meta http-equiv="refresh" content="0; url={relative}">
<link rel="canonical" href="{SITE_URL}{new_path}"></head>
<body><p>这个地址已迁移到 <a href="{relative}">新位置</a>。</p></body></html>'''
    page.write_text(html, encoding="utf-8")


def clean_docs():
    for route in ROUTES:
        directory = DOCS / route
        directory.mkdir(parents=True, exist_ok=True)
        for page in directory.glob("lesson-*.html"):
            page.unlink()
    for name in ("topics", "practice", "gallery"):
        directory = DOCS / name
        if directory.exists():
            rmtree(directory)
    for name in ("topics", "lessons"):
        directory = DOCS / "assets" / name
        if directory.exists():
            rmtree(directory)
    fonts = DOCS / "assets" / "fonts"
    if fonts.exists():
        rmtree(fonts)


def copy_static():
    for name in ("style.css", "ui.js", "search.js"):
        copyfile(ROOT / "site" / name, DOCS / "assets" / name)
    copyfile(ROOT / "assets/site/favicon.svg", DOCS / "assets/favicon.svg")
    copyfile(ROOT / "assets/site/whiteboard-lineart.svg", DOCS / "assets/whiteboard-lineart.svg")
    for route in ROUTES:
        copyfile(ROOT / f"assets/site/{route}.svg", DOCS / f"assets/{route}.svg")
    gallery_assets = ROOT / "assets/gallery"
    if gallery_assets.is_dir():
        for asset in gallery_assets.rglob("*"):
            if not asset.is_file():
                continue
            destination = DOCS / "assets/gallery" / asset.relative_to(gallery_assets)
            destination.parent.mkdir(parents=True, exist_ok=True)
            copyfile(asset, destination)
    diagram = ROOT / "assets/topics/ai/illustrations/ai-two-layers.svg"
    if not diagram.is_file():
        raise SystemExit(f"缺少 AI 两层示意图：{diagram}")
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
    topics = load_topics()
    gallery = parse_gallery()
    clean_docs()
    copy_static()
    home(topics, gallery)
    topic_index(topics)
    entries = []
    for topic in topics:
        topic_page(topic)
        entries.append({
            "topic": topic["slug"],
            "topicName": topic["title"],
            "audience": "both" if len(topic["audiences"]) > 1 else topic["audiences"][0],
            "audienceName": topic_audience_label(topic),
            "number": 0,
            "title": topic["title"],
            "step": "专题介绍",
            "text": f"{topic['subtitle']} {topic['summary']} {plain(topic['intro'])}"[:1200],
            "url": f"topics/{topic['slug']}/index.html",
            "status": "active",
        })
        for session in topic["sessions"]:
            session_page(topic, session)
            entries.extend(search_entries_for_session(topic, session))
    for route in ROUTES:
        path_page(route, topics)
    gallery_index(gallery)
    for item in gallery:
        entries.append(gallery_page(item, gallery))
    search_page(topics, gallery)
    for old, new in LEGACY_REDIRECTS.items():
        write_redirect(old, new)
    (DOCS / "assets/search-index.js").write_text(
        "window.courseSearchIndex = " + json.dumps(entries, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(entries)} search entries, {sum(len(t['sessions']) for t in topics)} sessions, "
          f"{len(topics)} topics, {len(gallery)} gallery pages, {len(LEGACY_REDIRECTS)} redirects.")


if __name__ == "__main__":
    main()
