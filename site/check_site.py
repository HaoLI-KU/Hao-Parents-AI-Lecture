"""Check generated topic pages, links, anchors and search coverage."""
from html import unescape
import itertools
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "site"))
import build  # noqa: E402

errors = []
warnings = []
links_checked = 0


def fail(message):
    errors.append(message)


def warn(message):
    warnings.append(message)


def page_ids(html):
    return re.findall(r'id="([^"]+)"', html)


def check_link(page, raw_href):
    global links_checked
    href = unescape(raw_href).strip()
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")):
        return
    links_checked += 1
    path, _, fragment = href.partition("#")
    path = path.split("?", 1)[0]
    target = (page.parent / path).resolve() if path else page
    try:
        target.relative_to(DOCS)
    except ValueError:
        fail(f"{page}: 链接跳出 docs/：{href}")
        return
    if path.endswith(".md"):
        if target.is_file() and "assets" in target.relative_to(DOCS).parts:
            return
        fail(f"{page}: 生成页里仍有 Markdown 链接 {href}")
        return
    if not target.is_file():
        fail(f"{page}: 链接目标不存在 {href}")
        return
    if fragment:
        fragment = unquote(fragment)
        if f'id="{fragment}"' not in target.read_text(encoding="utf-8"):
            fail(f"{page}: 锚点不存在 {href}")


def check_page(page):
    html = page.read_text(encoding="utf-8")
    relative = page.relative_to(DOCS).as_posix()
    if 'lang="zh-CN"' not in html:
        fail(f"{relative}: 缺少 lang=\"zh-CN\"")
    if len(re.findall(r"<h1[ >]", html)) != 1:
        fail(f"{relative}: 应恰好有一个 h1")
    if '<a class="skip-link" href="#main">' not in html:
        fail(f"{relative}: 缺少跳到正文链接")
    if 'data-page-dir="' not in html or 'data-page-path="' not in html:
        fail(f"{relative}: 缺少 data-page-dir / data-page-path")
    if 'data-embed-nav' not in html:
        fail(f"{relative}: 缺少嵌入式导航脚本")
    if '在浏览器打开' not in html:
        fail(f"{relative}: 缺少“在浏览器打开”外链")
    ids = page_ids(html)
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        fail(f"{relative}: 重复 id：{', '.join(duplicates)}")
    for match in re.finditer(r'(?:href|src)="([^"]*)"', html):
        check_link(page, match.group(1))



CURRICULUM = ROOT / "course/curriculum.md"
AUDIENCE_MAP = {"爸爸": "dad", "妈妈": "mom", "共同": "both"}
CURRICULUM_FIELDS = ("讲", "文件", "标题", "受众", "状态", "前置", "学完能做到", "产出 / 验收", "覆盖点", "视觉")
GENERIC_STEPS = {
    "准备", "收尾", "检查清单", "妈妈清单", "小结", "总结", "下一步",
    "检查", "练习", "备注", "备用",
}


def curriculum_text() -> str:
    return CURRICULUM.read_text(encoding="utf-8") if CURRICULUM.is_file() else ""


def split_table_cells(line):
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def parse_curriculum():
    text = curriculum_text()
    sections = {}
    current = None
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^## 专题：([a-z0-9-]+)｜(.+?)\s*$", line)
        if match:
            slug, title = match.groups()
            if slug in sections:
                fail(f"课程地图重复专题：{slug}")
            current = {"slug": slug, "title": title.strip(), "rows": []}
            sections[slug] = current
            continue
        if current is None or not line.startswith("|"):
            continue
        cells = split_table_cells(line)
        if "讲" not in cells or "文件" not in cells:
            continue
        if index + 1 >= len(lines):
            continue
        header = cells
        rows = []
        for row_line in lines[index + 2:]:
            if not row_line.startswith("|"):
                break
            values = split_table_cells(row_line)
            if not any(values):
                continue
            if len(values) != len(header):
                fail(f"课程地图表格列数不一致：{row_line}")
                continue
            rows.append(dict(zip(header, values)))
        current["rows"] = rows
    return sections


def normalise_text(value):
    return re.sub(r"\s+", "", str(value or "")).lower()


def text_tokens(value):
    text = normalise_text(value)
    tokens = set(re.findall(r"[a-z0-9_]+", text))
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        tokens.update(run[i:i + 2] for i in range(len(run) - 1))
    return tokens


def text_similarity(left, right):
    a, b = text_tokens(left), text_tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check_curriculum(topics):
    if not CURRICULUM.is_file():
        fail("缺少课程地图：course/curriculum.md")
        return
    sections = parse_curriculum()
    topic_by_slug = {topic["slug"]: topic for topic in topics}
    listed_slugs = []
    sessions = {}
    for slug, section in sections.items():
        listed_slugs.append(slug)
        topic = topic_by_slug.get(slug)
        if topic is None:
            fail(f"课程地图有未知专题：{slug}")
            continue
        if section["title"] != topic["title"]:
            fail(f"课程地图专题标题不一致：{slug}「{section['title']}」≠「{topic['title']}」")
        if not section["rows"]:
            fail(f"课程地图专题没有讲次：{slug}")
            continue
        for row in section["rows"]:
            missing = [field for field in CURRICULUM_FIELDS if not row.get(field)]
            if missing:
                fail(f"课程地图行缺少字段（{', '.join(missing)}）：{row.get('文件', slug)}")
                continue
            file_value = row["文件"].strip()
            file_path = (ROOT / "course" / file_value).resolve()
            try:
                relative = file_path.relative_to(ROOT)
            except ValueError:
                fail(f"课程地图文件路径跳出仓库：{file_value}")
                continue
            matches = [session for session in topic["sessions"] if session["file"].resolve() == file_path]
            if not matches:
                fail(f"课程地图文件不存在于专题：{file_value}")
                continue
            if len(matches) > 1:
                fail(f"课程地图文件重复：{file_value}")
                continue
            session = matches[0]
            session_key = session["file"].relative_to(ROOT).as_posix()
            if session_key in sessions:
                fail(f"课程地图重复列出课稿：{file_value}")
            sessions[session_key] = (section, row, session)
            if row["讲"] != f"{session['number']:02d}":
                fail(f"课程地图讲次编号不一致：{file_value}「{row['讲']}」≠「{session['number']:02d}」")
            if row["标题"] != session["title"]:
                fail(f"课程地图标题不一致：{file_value}「{row['标题']}」≠「{session['title']}」")
            if AUDIENCE_MAP.get(row["受众"]) != session["audience"]:
                fail(f"课程地图受众不一致：{file_value}「{row['受众']}」≠「{session['audience']}」")
            if row["状态"] != session["status"]:
                fail(f"课程地图状态不一致：{file_value}「{row['状态']}」≠「{session['status']}」")
            if row["视觉"] not in {"—", "概念图", "截图", "结果图", "对照"}:
                warn(f"课程地图视觉类型未知：{file_value}「{row['视觉']}」")

    actual_slugs = [topic["slug"] for topic in topics]
    if listed_slugs != actual_slugs:
        fail("课程地图专题顺序与 topic.md 的 order 不一致")
    for topic in topics:
        for session in topic["sessions"]:
            session_key = session["file"].relative_to(ROOT).as_posix()
            if session_key not in sessions:
                fail(f"课程地图漏掉讲次：{session['file'].relative_to(ROOT)}")
    covers = {}
    for session in sessions.values():
        _, row, source = session
        for tag in re.split(r"[,，]", row["覆盖点"]):
            tag = tag.strip()
            if not tag:
                continue
            covers.setdefault(tag, []).append(source)
    for tag, sources in sorted(covers.items()):
        if len(sources) > 1:
            names = "、".join(source["file"].relative_to(ROOT).as_posix() for source in sources)
            warn(f"重复覆盖点「{tag}」：{names}")

    all_sessions = [session for topic in topics for session in topic["sessions"]]
    for left, right in itertools.combinations(all_sessions, 2):
        score = text_similarity(left["title"] + " " + left["summary"], right["title"] + " " + right["summary"])
        if normalise_text(left["title"]) == normalise_text(right["title"]):
            warn(f"标题重复：{left['file'].relative_to(ROOT)} 与 {right['file'].relative_to(ROOT)}")
        elif score >= 0.55:
            warn(f"标题/摘要相似度 {score:.2f}：{left['file'].relative_to(ROOT)} 与 {right['file'].relative_to(ROOT)}，请人工确认是否重复")

    headings = {}
    for session in all_sessions:
        source = session["file"].relative_to(ROOT).as_posix()
        for heading in re.findall(r"^###\s+(.+?)\s*$", session["body"], re.M):
            normalized = re.sub(r"^\d+\.\s*", "", heading).strip()
            if not normalized or normalized in GENERIC_STEPS:
                continue
            headings.setdefault(normalized, []).append(source)
    for heading, sources in sorted(headings.items()):
        if len(sources) > 1:
            warn(f"步骤标题重复「{heading}」：{'、'.join(sources)}")


def main():
    topics = build.load_topics()
    gallery = build.parse_gallery()
    pages = sorted(
        path for path in DOCS.rglob("*.html")
        if "assets" not in path.relative_to(DOCS).parts
    )
    if not pages:
        fail("docs/ 里没有生成任何网页")
        return report()

    for page in pages:
        check_page(page)
    check_curriculum(topics)

    if not (DOCS / ".nojekyll").is_file():
        fail("缺少 docs/.nojekyll")
    if (ROOT / "course/lessons").exists() or (ROOT / "course/practices").exists():
        fail("源码树仍有 course/lessons 或 course/practices")
    for path in (ROOT / "course/topics").glob("*/**/*.md"):
        if path.name == "topic.md":
            continue
        if not re.match(r"\d{2}-.+\.md$", path.name):
            fail(f"课稿命名不合规则：{path}")

    search = DOCS / "search.html"
    if not search.is_file():
        fail("缺少 docs/search.html")
    else:
        search_html = search.read_text(encoding="utf-8")
        for needle in ('id="course-query"', "assets/search.js", "assets/search-index.js"):
            if needle not in search_html:
                fail(f"search.html 缺少 {needle}")

    index_file = DOCS / "assets/search-index.js"
    entries = []
    if not index_file.is_file():
        fail("缺少 docs/assets/search-index.js")
    else:
        raw = index_file.read_text(encoding="utf-8").strip()
        try:
            entries = json.loads(raw.split("=", 1)[1].rstrip().rstrip(";"))
        except (IndexError, json.JSONDecodeError) as error:
            fail(f"search-index.js 解析失败：{error}")
    entry_pages = {entry.get("url", "").split("#", 1)[0] for entry in entries}
    for entry in entries:
        url = entry.get("url", "")
        path, _, fragment = url.partition("#")
        target = (DOCS / path).resolve()
        if not target.is_file():
            fail(f"搜索索引指向不存在的页面：{url}")
        elif fragment and f'id="{fragment}"' not in target.read_text(encoding="utf-8"):
            fail(f"搜索索引指向不存在的锚点：{url}")

    expected = {"index.html", "search.html", "topics/index.html",
                "dad/index.html", "mom/index.html", "gallery/index.html"}
    for route in build.ROUTES:
        if not (DOCS / f"{route}/index.html").is_file():
            fail(f"缺少 {route}/index.html")
    for topic in topics:
        page = f"topics/{topic['slug']}/index.html"
        expected.add(page)
        if not (DOCS / page).is_file():
            fail(f"缺少专题页：{page}")
        if page not in entry_pages:
            fail(f"搜索索引没有覆盖专题页：{page}")
        for session in topic["sessions"]:
            page = build.session_path(session)
            expected.add(page)
            if not (DOCS / page).is_file():
                fail(f"缺少课页：{page}")
            if page not in entry_pages:
                fail(f"搜索索引没有覆盖课页：{page}")
    for slug in [item["slug"] for item in gallery]:
        page = f"gallery/{slug}.html"
        expected.add(page)
        if not (DOCS / page).is_file():
            fail(f"缺少拾趣作品页：{page}")
        if page not in entry_pages:
            fail(f"搜索索引没有覆盖拾趣页：{page}")
    for page in sorted(expected):
        if not (DOCS / page).is_file():
            fail(f"缺少页面：{page}")


    for folder in (ROOT / "course", DOCS):
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".html"}:
                text = path.read_text(encoding="utf-8")
                if any(word in text for word in ("养花小站", "我的养花笔记", "plant-notes", "plants.json")):
                    fail(f"仍残留养花草稿：{path.relative_to(ROOT)}")
    for name in ("README.md", "website.md", "workflow.md", "teaching.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        if any(word in text for word in ("养花小站", "我的养花笔记", "plant-notes", "plants.json")):
            fail(f"规则文件仍残留养花草稿：{name}")

    for page in DOCS.glob("topics/*/*.html"):
        eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', page.read_text(encoding="utf-8"), re.S)
        if eyebrow and ("腾讯会议" in eyebrow.group(1) or "上海家中" in eyebrow.group(1)):
            fail(f"{page.relative_to(DOCS)} 的 eyebrow 仍有排课方式")

    shortcuts = {
        "topics/mac/01-new-mac.html": ("⌘C", "⌘V", "⌘S"),
        "topics/mac/03-shortcuts-and-sharing.html": ("⌘C", "⌘V", "⌘S", "⌘W", "⌘Q", "⇧⌘4"),
    }
    for page, needles in shortcuts.items():
        html = (DOCS / page).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in html:
                fail(f"{page}: 快捷键 {needle} 没有保留")

    if len(entries) < len(expected):
        warn("搜索条目少于页面数量，请确认每讲都有可搜索正文")
    print(f"页面 {len(pages)} 个；内部链接/资源 {links_checked} 个；搜索条目 {len(entries)} 条。")
    report()


def report():
    for message in warnings:
        print(f"提醒：{message}")
    if errors:
        for message in errors:
            print(f"错误：{message}")
        print(f"检查失败：{len(errors)} 项。")
        sys.exit(1)
    print("检查通过。")


if __name__ == "__main__":
    main()
