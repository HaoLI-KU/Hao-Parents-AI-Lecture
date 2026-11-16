"""Check generated course pages, links, anchors and search coverage."""
from html import unescape
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
pages = sorted(
    path for path in DOCS.rglob("*.html")
    if "assets" not in path.relative_to(DOCS).parts
)
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
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:")):
        return
    if href.startswith("data:"):
        return
    links_checked += 1
    path, _, fragment = href.partition("#")
    path = path.split("?", 1)[0]
    if path.endswith(".md"):
        fail(f"{page}: 生成页里仍有 Markdown 链接 {href}")
        return
    target = (page.parent / path).resolve() if path else page
    try:
        target.relative_to(DOCS)
    except ValueError:
        fail(f"{page}: 链接跳出 docs/：{href}")
        return
    if not target.is_file():
        fail(f"{page}: 链接目标不存在 {href}")
        return
    if fragment:
        fragment = unquote(fragment)
        target_html = target.read_text(encoding="utf-8")
        if f'id="{fragment}"' not in target_html:
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
    if 'data-page-dir="' not in html:
        fail(f"{relative}: 缺少 data-page-dir")
    if 'data-page-path="' not in html:
        fail(f"{relative}: 缺少 data-page-path")
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


def main():
    if not pages:
        fail("docs/ 里没有生成任何网页")
        report()
        return

    for page in pages:
        check_page(page)

    if not (DOCS / ".nojekyll").is_file():
        fail("缺少 docs/.nojekyll")


    search = DOCS / "search.html"
    if not search.is_file():
        fail("缺少 docs/search.html")
    else:
        search_html = search.read_text(encoding="utf-8")
        for needle in ("id=\"course-query\"", "assets/search.js", "assets/search-index.js"):
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
    entry_pages = set()
    for entry in entries:
        url = entry.get("url", "")
        path, _, fragment = url.partition("#")
        entry_pages.add(path)
        target = (DOCS / path).resolve()
        if not target.is_file():
            fail(f"搜索索引指向不存在的页面：{url}")
            continue
        if fragment and f'id="{fragment}"' not in target.read_text(encoding="utf-8"):
            fail(f"搜索索引指向不存在的锚点：{url}")

    try:
        rows = build.parse_schedule()
    except SystemExit as error:
        fail(str(error))
        rows = {route: [] for route in build.ROUTES}

    try:
        gallery = build.parse_gallery()
    except SystemExit as error:
        fail(str(error))
        gallery = []

    expected_pages = set()
    referenced_files = set()
    for route, items in rows.items():
        for item in items:
            page = f"{route}/lesson-{item['number']:02}.html"
            expected_pages.add(page)
            referenced_files.add(item["file"])
            if not (DOCS / page).is_file():
                fail(f"课表有但网页没有：{page}")
            if page not in entry_pages:
                fail(f"搜索索引没有覆盖课页：{page}")
    expected_pages.add("practice/index.html")
    for item in build.PRACTICES:
        practice_page = f"practice/{item['slug']}.html"
        expected_pages.add(practice_page)
        referenced_files.add(item["file"])
        if not (DOCS / practice_page).is_file():
            fail(f"缺少共同练习页：{practice_page}")
        if practice_page not in entry_pages:
            fail(f"搜索索引没有覆盖共同练习页：{practice_page}")
    if not (DOCS / "practice/index.html").is_file():
        fail("缺少共同练习首页：practice/index.html")

    expected_pages.add("gallery/index.html")
    if not (DOCS / "gallery/index.html").is_file():
        fail("缺少拾趣首页：gallery/index.html")
    gallery_slugs = set()
    for item in gallery:
        slug = item["slug"]
        gallery_slugs.add(slug)
        page = f"gallery/{slug}.html"
        expected_pages.add(page)
        if not (DOCS / page).is_file():
            fail(f"缺少拾趣作品页：{page}")
        if page not in entry_pages:
            fail(f"搜索索引没有覆盖拾趣作品页：{page}")
    for path in sorted((ROOT / "course/gallery").glob("*.md")):
        if path.stem not in gallery_slugs:
            fail(f"拾趣稿件没有进入构建：course/gallery/{path.name}")

    for path in sorted((ROOT / "course/lessons").glob("*.md")):
        if path.name in referenced_files or path.name == "audit-01-07.md":
            continue
        fail(f"课稿没有进入课表或共同练习：course/lessons/{path.name}")

    # 妈妈路线不应再出现养花草稿；skills.md 的长期方向除外。
    for folder in (ROOT / "course", ROOT / "docs"):
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".html"}:
                text = path.read_text(encoding="utf-8")
                if any(word in text for word in ("养花小站", "我的养花笔记", "plant-notes", "plants.json")):
                    fail(f"仍残留养花草稿：{path.relative_to(ROOT)}")
    for name in ("README.md", "website.md", "workflow.md", "teaching.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        if any(word in text for word in ("养花小站", "我的养花笔记", "plant-notes", "plants.json")):
            fail(f"规则文件仍残留养花草稿：{name}")

    # 课表和课页 eyebrow 不再有排课方式；妈妈 1–4 正文里的腾讯会议软件操作不算。
    for route in build.ROUTES:
        page = DOCS / route / "index.html"
        if page.is_file():
            text = page.read_text(encoding="utf-8")
            for word in ("腾讯会议", "上海家中"):
                if word in text:
                    fail(f"{route}/index.html 仍有排课方式：{word}")
    for page in DOCS.glob("*/lesson-*.html"):
        text = page.read_text(encoding="utf-8")
        eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', text, re.S)
        if eyebrow and ("腾讯会议" in eyebrow.group(1) or "上海家中" in eyebrow.group(1)):
            fail(f"{page.relative_to(DOCS)} 的 eyebrow 仍有排课方式")

    shortcuts = {
        "mom/lesson-01.html": ("⌘C", "⌘V", "⌘S"),
        "mom/lesson-03.html": ("⌘C", "⌘V", "⌘S", "⌘W", "⌘Q", "⇧⌘4"),
    }
    for page, needles in shortcuts.items():
        html = (DOCS / page).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in html:
                fail(f"{page}: 快捷键 {needle} 没有保留")

    if len(entries) < len(expected_pages):
        warn("搜索条目少于课页数量，请确认每节都有可搜索正文")

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
